import asyncio
import os
import sys
import random
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

from src.config.settings import settings
from src.conversation.manager import ConversationManager
from src.conversation.models import ConversationState
from src.db.repository import MongoDBRepository
from src.db.models import UserDB, UserSession

# Configure logger
logger.remove()
logger.add(sys.stderr, level=settings.LOG_LEVEL)

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)
logger.add("logs/bot.log", rotation="1 day", retention="7 days", level=settings.LOG_LEVEL)

# Initialize conversation manager
conversation_manager = ConversationManager()

# Initialize database repository
db_repository = MongoDBRepository()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler for /start command"""
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name
    username = user.username
    
    # Store user in context for later use
    context.user_data["user_id"] = user_id
    context.user_data["first_name"] = first_name
    
    # Get or create user in database
    user_db = await db_repository.get_user(user_id)
    if not user_db:
        user_db = UserDB.create_new(
            telegram_id=user_id,
            first_name=first_name,
            last_name=last_name,
            username=username
        )
        await db_repository.create_user(user_db)
    
    # Create new session
    session = UserSession.create_new(telegram_id=user_id)
    await db_repository.create_session(session)
    context.user_data["current_session"] = session
    
    # Reset conversation to beginning
    user_db.current_node = "saludo_inicial"
    await db_repository.update_user(user_db)
    
    # Get initial node and send message
    initial_node = conversation_manager.get_node("saludo_inicial")
    if initial_node:
        user_data = {"nombre": first_name}
        message_text = conversation_manager.format_message(initial_node, user_data)
        
        # Create keyboard markup
        markup = conversation_manager.create_keyboard_markup(initial_node)
        
        # Store current node ID in context
        context.user_data["current_node"] = "saludo_inicial"
        
        await update.message.reply_text(message_text, reply_markup=markup)
        return ConversationState.RESPONDING
    else:
        await update.message.reply_text("Error: No se pudo iniciar la conversación. Por favor, contacta al soporte.")
        return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /help command"""
    help_text = (
        "📋 *CardioVID-Bot - Ayuda*\n\n"
        "Este bot te permite monitorear tus síntomas de EPOC "
        "y recibir recomendaciones médicas.\n\n"
        "Comandos disponibles:\n"
        "/start - Iniciar el bot\n"
        "/help - Mostrar esta ayuda\n"
        "/reset - Reiniciar la conversación\n"
        "/historial - Ver tu historial de interacciones\n"
        "/empeore - Reportar empeoramiento de síntomas\n\n"
        "Si en algún momento presentas síntomas de empeoramiento, "
        "puedes usar el comando /empeore o escribir la palabra EMPEORÉ "
        "y seguiremos el protocolo de exacerbación."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler for /reset command - Reset conversation to beginning"""
    user_id = update.effective_user.id
    user_db = await db_repository.get_user(user_id)
    
    if user_db:
        # Complete current session if exists
        current_session = context.user_data.get("current_session")
        if current_session:
            final_message = "Sesión reiniciada por el usuario"
            current_session.complete_session(final_message=final_message)
            await db_repository.update_session(current_session)
        
        # Create new session
        session = UserSession.create_new(telegram_id=user_id)
        await db_repository.create_session(session)
        context.user_data["current_session"] = session
        
        user_db.current_node = "saludo_inicial"
        await db_repository.update_user(user_db)
        
        # Store current node ID in context
        context.user_data["current_node"] = "saludo_inicial"
        
        initial_node = conversation_manager.get_node("saludo_inicial")
        user_data = {"nombre": user_db.first_name}
        message_text = conversation_manager.format_message(initial_node, user_data)
        
        # Create keyboard markup
        markup = conversation_manager.create_keyboard_markup(initial_node)
        
        await update.message.reply_text(message_text, reply_markup=markup)
        return ConversationState.RESPONDING
    else:
        await update.message.reply_text("Por favor, inicia el bot primero con /start")
        return ConversationHandler.END

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle callback queries from inline keyboards"""
    query = update.callback_query
    await query.answer()  # Answer callback query to stop loading state
    
    user_id = update.effective_user.id
    selected_option = query.data
    
    # Get user from database
    user_db = await db_repository.get_user(user_id)
    if not user_db:
        await query.message.reply_text("Por favor, inicia el bot primero con /start")
        return ConversationHandler.END
    
    # Get current node
    current_node_id = user_db.current_node
    current_node = conversation_manager.get_node(current_node_id)
    
    # Get or create session
    session = context.user_data.get("current_session")
    if not session:
        session = await db_repository.get_active_session(user_id)
        if not session:
            session = UserSession.create_new(telegram_id=user_id)
            await db_repository.create_session(session)
        context.user_data["current_session"] = session
    
    # Add response to session
    session.add_response(
        node_id=current_node_id,
        response=selected_option,
        message_text=current_node.message
    )
    await db_repository.update_session(session)
    
    # Record response in user document
    timestamp = datetime.now().isoformat()
    user_db.responses[current_node_id] = {"answer": selected_option, "timestamp": timestamp}
    user_db.last_interaction = timestamp
    
    # Get next node id
    next_node_id = conversation_manager.get_next_node_id(current_node_id, selected_option)
    if not next_node_id:
        # Mensaje final para la sesión
        final_message = "Conversación finalizada"
        
        # Complete session when conversation ends
        session.complete_session(final_message=final_message)
        await db_repository.update_session(session)
        context.user_data.pop("current_session", None)
        
        await query.message.reply_text(final_message)
        return ConversationHandler.END
    
    # Update user with new node
    user_db.current_node = next_node_id
    await db_repository.update_user(user_db)
    
    # Store current node ID in context
    context.user_data["current_node"] = next_node_id
    
    # Get next node and send message
    next_node = conversation_manager.get_node(next_node_id)
    user_data = {"nombre": user_db.first_name}
    message_text = conversation_manager.format_message(next_node, user_data)
    
    # Create keyboard markup
    markup = conversation_manager.create_keyboard_markup(next_node)
    
    # Send new message
    await query.message.reply_text(message_text, reply_markup=markup)
    
    # Recordatorio ocasional sobre el comando /empeore (10% de probabilidad)
    should_remind = random.random() < 0.1  # 10% de probabilidad
    if should_remind:
        reminder_text = (
            "📝 *Recordatorio*: Si en algún momento presentas empeoramiento de síntomas, "
            "puedes usar el comando /empeore para acceder rápidamente al protocolo de exacerbación."
        )
        await query.message.reply_text(reminder_text, parse_mode="Markdown")
    
    # Return appropriate state based on node
    return conversation_manager.get_state_for_node(next_node_id)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle text messages"""
    message_text = update.message.text
    user_id = update.effective_user.id
    
    # Check if message is "EMPEORÉ"
    if message_text.upper() == "EMPEORÉ":
        # Get user from database
        user_db = await db_repository.get_user(user_id)
        if not user_db:
            await update.message.reply_text("Por favor, inicia el bot primero con /start")
            return ConversationHandler.END
        
        # Complete current session if exists
        current_session = context.user_data.get("current_session")
        if current_session:
            final_message = "Sesión terminada por empeoramiento de síntomas"
            current_session.complete_session(final_message=final_message)
            await db_repository.update_session(current_session)
        
        # Create new session for empeoramiento
        session = UserSession.create_new(telegram_id=user_id, session_type="empeoramiento")
        session.add_response(
            node_id="EMPEORÉ_MESSAGE",
            response=message_text,
            message_text="Usuario reportó empeoramiento"
        )
        await db_repository.create_session(session)
        context.user_data["current_session"] = session
        
        await update.message.reply_text(
            "He detectado que tus síntomas han empeorado. "
            "Te estamos redirigiendo al protocolo de exacerbación..."
        )
        
        # Reset conversation to filtro_1
        user_db.current_node = "filtro_1"
        await db_repository.update_user(user_db)
        
        # Store current node ID in context
        context.user_data["current_node"] = "filtro_1"
        
        node = conversation_manager.get_node("filtro_1")
        user_data = {"nombre": user_db.first_name}
        message_text = conversation_manager.format_message(node, user_data)
        
        # Create keyboard markup
        markup = conversation_manager.create_keyboard_markup(node)
        
        await update.message.reply_text(message_text, reply_markup=markup)
        return ConversationState.FILTRO_1
    else:
        await update.message.reply_text(
            "Por favor, usa los botones proporcionados para responder "
            "o utiliza los comandos /start, /help o /reset.\n\n"
            "Si tus síntomas han empeorado, escribe EMPEORÉ."
        )
        return ConversationState.RESPONDING

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /historial command - Show user session history"""
    user_id = update.effective_user.id
    
    # Get user from database
    user_db = await db_repository.get_user(user_id)
    if not user_db:
        await update.message.reply_text("Por favor, inicia el bot primero con /start")
        return
    
    # Get user sessions
    sessions = await db_repository.get_user_sessions(user_id, limit=5)
    
    if not sessions:
        await update.message.reply_text("No tienes sesiones registradas aún.")
        return
    
    # Format session history
    history_text = "📊 *Historial de sesiones:*\n\n"
    
    for session in sessions:
        start_date = datetime.fromisoformat(session.start_time).strftime("%d/%m/%Y %H:%M")
        session_type = "Empeoramiento" if session.session_type == "empeoramiento" else "Normal"
        responses_count = len(session.responses)
        final_msg = f"✓ {session.final_message}" if session.final_message else "✓ Completada"
        
        history_text += (
            f"*{start_date}* - Tipo: {session_type}\n"
            f"Respuestas: {responses_count}\n"
            f"Estado: {final_msg}\n"
            "Últimas respuestas:\n"
        )
        
        # Show last 3 responses of the session
        for response in session.responses[-3:]:
            history_text += f"- Nodo: `{response.node_id}` → `{response.response}`\n"
        
        history_text += "\n"
    
    history_text += "\nSe muestran las últimas 5 sesiones completadas."
    
    await update.message.reply_text(history_text, parse_mode="Markdown")

async def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(settings.BOT_TOKEN).build()

    # Connect to database
    await db_repository.connect()
    
    # Configure bot commands menu
    await setup_bot_commands(application)
    
    # Setup conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ConversationState.INITIAL: [
                CallbackQueryHandler(handle_callback),
            ],
            ConversationState.RESPONDING: [
                CallbackQueryHandler(handle_callback),
                MessageHandler(filters.Regex(r"(?i)^EMPEORÉ$"), handle_message),
            ],
            ConversationState.FILTRO_1: [
                CallbackQueryHandler(handle_callback),
            ],
            ConversationState.FILTRO_2: [
                CallbackQueryHandler(handle_callback),
            ],
            ConversationState.FIN: [
                CallbackQueryHandler(handle_callback),
            ],
            ConversationState.EDUCATION_OPT: [
                CallbackQueryHandler(handle_callback),
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("reset", reset_command),
            CommandHandler("help", help_command),
            CommandHandler("historial", history_command),
            CommandHandler("empeore", empeore_command),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message),
        ],
    )

    # Register handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("historial", history_command))
    application.add_handler(CommandHandler("empeore", empeore_command))
    
    # Start the Bot
    logger.info(f"Starting CardioVID Bot as @{settings.BOT_NAME}")
    
    # Set up signal handlers
    stop_event = asyncio.Event()
    
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, stopping bot...")
        stop_event.set()
    
    # Register signal handlers
    import signal
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler) # Termination signal
    
    # Run the bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # Keep the program running until stopped by signal
    await stop_event.wait()
    
    # Close database connection when application exits
    logger.info("Shutting down bot...")
    await application.stop()
    await db_repository.close()
    logger.info("Bot stopped")

async def setup_bot_commands(application: Application) -> None:
    """Set up bot commands menu"""
    commands = [
        ("start", "Iniciar el bot"),
        ("help", "Mostrar ayuda"),
        ("reset", "Reiniciar la conversación"),
        ("historial", "Ver mi historial"),
        ("empeore", "Reportar empeoramiento")
    ]
    
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands menu configured")

async def empeore_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler for /empeore command - Same as typing EMPEORÉ"""
    user_id = update.effective_user.id
    
    await update.message.reply_text(
        "He detectado que tus síntomas han empeorado. "
        "Te estamos redirigiendo al protocolo de exacerbación..."
    )
    
    # Reset conversation to filtro_1
    user_db = await db_repository.get_user(user_id)
    
    if not user_db:
        await update.message.reply_text("Por favor, inicia el bot primero con /start")
        return ConversationHandler.END
    
    # Complete current session if exists
    current_session = context.user_data.get("current_session")
    if current_session:
        final_message = "Sesión terminada por empeoramiento de síntomas (comando)"
        current_session.complete_session(final_message=final_message)
        await db_repository.update_session(current_session)
    
    # Create new session for empeoramiento
    session = UserSession.create_new(telegram_id=user_id, session_type="empeoramiento")
    session.add_response(
        node_id="EMPEORÉ_COMMAND",
        response="/empeore",
        message_text="Usuario reportó empeoramiento (comando)"
    )
    await db_repository.create_session(session)
    context.user_data["current_session"] = session
    
    # Reset conversation to filtro_1
    user_db.current_node = "filtro_1"
    await db_repository.update_user(user_db)
    
    # Store current node ID in context
    context.user_data["current_node"] = "filtro_1"
    
    node = conversation_manager.get_node("filtro_1")
    user_data = {"nombre": user_db.first_name}
    message_text = conversation_manager.format_message(node, user_data)
    
    # Create keyboard markup
    markup = conversation_manager.create_keyboard_markup(node)
    
    await update.message.reply_text(message_text, reply_markup=markup)
    return ConversationState.FILTRO_1

if __name__ == "__main__":
    try:
        # Use asyncio.run for Python 3.12
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        logger.error(traceback.format_exc()) 
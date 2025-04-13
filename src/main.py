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

# Función auxiliar para obtener mensajes de forma segura
def get_node_message(node) -> str:
    """Obtener el mensaje de un nodo de forma segura, manejando diferentes tipos de datos"""
    try:
        # Caso 1: Si es un diccionario con clave "message"
        if isinstance(node, dict) and "message" in node:
            return str(node["message"])
        
        # Caso 2: Si es un objeto con atributo message
        if hasattr(node, "message"):
            return str(node.message)
        
        # Caso 3: Si es un objeto con método get
        if hasattr(node, "get") and callable(getattr(node, "get")):
            try:
                msg = node.get("message", "")
                return str(msg) if msg is not None else ""
            except:
                pass
        
        # Caso 4: Si podemos convertirlo a string
        try:
            return str(node)
        except:
            pass
        
        # Si todo falla, devolver cadena vacía
        return ""
    except Exception as e:
        logger.error(f"Error al obtener mensaje del nodo: {e}")
        return ""

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
    
    # Complete current session if exists
    current_session = context.user_data.get("current_session")
    if current_session:
        final_message = "Sesión terminada por inicio de nueva conversación"
        current_session.complete_session(final_message=final_message)
        await db_repository.update_session(current_session)
        logger.info(f"Sesión anterior completada por /start para usuario {user_id} con mensaje final: {final_message}")
    
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
        logger.info(f"Nuevo usuario creado: {user_id}")
    
    # Create new session
    session = UserSession.create_new(telegram_id=user_id)
    await db_repository.create_session(session)
    context.user_data["current_session"] = session
    logger.info(f"Nueva sesión creada por /start para usuario {user_id}")
    
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
        
        # Añadir respuesta a la nueva sesión
        session.add_response(
            node_id="START_COMMAND",
            response="/start",
            message_text="Inicio de conversación"
        )
        await db_repository.update_session(session)
        
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
            logger.info(f"Sesión completada por reset para usuario {user_id} con mensaje final: {final_message}")
        
        # Create new session
        session = UserSession.create_new(telegram_id=user_id)
        await db_repository.create_session(session)
        context.user_data["current_session"] = session
        logger.info(f"Nueva sesión creada por reset para usuario {user_id}")
        
        user_db.current_node = "saludo_inicial"
        await db_repository.update_user(user_db)
        
        # Store current node ID in context
        context.user_data["current_node"] = "saludo_inicial"
        
        initial_node = conversation_manager.get_node("saludo_inicial")
        user_data = {"nombre": user_db.first_name}
        message_text = conversation_manager.format_message(initial_node, user_data)
        
        # Create keyboard markup
        markup = conversation_manager.create_keyboard_markup(initial_node)
        
        # Añadir respuesta a la nueva sesión
        session.add_response(
            node_id="RESET_COMMAND",
            response="/reset",
            message_text="Conversación reiniciada"
        )
        await db_repository.update_session(session)
        
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
    try:
        # Extraer mensaje del nodo de forma segura
        node_message = get_node_message(current_node)
        session.add_response(
            node_id=current_node_id,
            response=selected_option,
            message_text=node_message
        )
        await db_repository.update_session(session)
        logger.debug(f"Respuesta registrada para usuario {user_id}, nodo {current_node_id}")
    except Exception as e:
        logger.error(f"Error al guardar respuesta: {e}")
    
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
        try:
            session.complete_session(final_message=final_message)
            await db_repository.update_session(session)
            logger.info(f"Sesión completada para usuario {user_id} con mensaje final: {final_message}")
        except Exception as e:
            logger.error(f"Error al completar sesión: {e}")
        
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
        # Mensaje de respuesta
        response_message = "He detectado que tus síntomas han empeorado. Te estamos redirigiendo al protocolo de exacerbación..."
        
        # Get user from database
        user_db = await db_repository.get_user(user_id)
        if not user_db:
            await update.message.reply_text("Por favor, inicia el bot primero con /start")
            return ConversationHandler.END
        
        # Complete current session if exists
        current_session = context.user_data.get("current_session")
        if current_session:
            try:
                final_message = "Sesión terminada por empeoramiento de síntomas (texto)"
                current_session.complete_session(final_message=final_message)
                await db_repository.update_session(current_session)
                logger.info(f"Sesión anterior completada para usuario {user_id} con mensaje final: {final_message}")
            except Exception as e:
                logger.error(f"Error al completar sesión anterior: {e}")
        
        # Create new session for empeoramiento
        try:
            session = UserSession.create_new(telegram_id=user_id, session_type="empeoramiento")
            session.add_response(
                node_id="EMPEORÉ_MESSAGE",
                response=message_text,
                message_text=response_message
            )
            # Marcar la sesión como completada inmediatamente
            session.complete_session(final_message="Protocolo de exacerbación activado")
            await db_repository.create_session(session)
            logger.info(f"Sesión de empeoramiento creada y completada para usuario {user_id} por texto EMPEORÉ")
        except Exception as e:
            logger.error(f"Error al crear sesión de empeoramiento: {e}")
        
        # Establecer nodo actual en filtro_1 (para futuras interacciones)
        user_db.current_node = "filtro_1"
        await db_repository.update_user(user_db)
        context.user_data["current_node"] = "filtro_1"
        
        # Enviar solo el mensaje de activación del protocolo
        await update.message.reply_text(response_message)
        
        # La interacción termina aquí
        return ConversationState.RESPONDING
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
    
    for i, session in enumerate(sessions, 1):
        start_date = datetime.fromisoformat(session.start_time).strftime("%d/%m/%Y %H:%M")
        end_date = datetime.fromisoformat(session.end_time).strftime("%d/%m/%Y %H:%M")
        duration = datetime.fromisoformat(session.end_time) - datetime.fromisoformat(session.start_time)
        minutes = duration.total_seconds() // 60
        
        session_type = "⚠️ Empeoramiento" if session.session_type == "empeoramiento" else "📝 Normal"
        responses_count = len(session.responses)
        final_msg = f"✓ {session.final_message}" if session.final_message else "✓ Completada"
        
        history_text += (
            f"*{i}. Sesión del {start_date}*\n"
            f"Tipo: {session_type}\n"
            f"Duración: {int(minutes)} min\n"
            f"Respuestas: {responses_count}\n"
            f"Estado: {final_msg}\n"
            "Últimas respuestas:\n"
        )
        
        # Show last 3 responses of the session
        for response in session.responses[-3:]:
            history_text += f"- `{response.node_id}`: {response.response}\n"
        
        history_text += "\n"
    
    history_text += "\n_Se muestran las últimas 5 sesiones completadas._"
    
    await update.message.reply_text(history_text, parse_mode="Markdown")
    logger.info(f"Historial mostrado para usuario {user_id}: {len(sessions)} sesiones")

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
    
    # Mensaje de respuesta
    response_message = "He detectado que tus síntomas han empeorado. Te estamos redirigiendo al protocolo de exacerbación..."
    
    # Get user from database
    user_db = await db_repository.get_user(user_id)
    if not user_db:
        await update.message.reply_text("Por favor, inicia el bot primero con /start")
        return ConversationHandler.END
    
    # Complete current session if exists
    current_session = context.user_data.get("current_session")
    if current_session:
        try:
            final_message = "Sesión terminada por empeoramiento de síntomas (comando)"
            current_session.complete_session(final_message=final_message)
            await db_repository.update_session(current_session)
            logger.info(f"Sesión anterior completada para usuario {user_id} con mensaje final: {final_message}")
        except Exception as e:
            logger.error(f"Error al completar sesión anterior: {e}")
    
    # Create new session for empeoramiento
    try:
        session = UserSession.create_new(telegram_id=user_id, session_type="empeoramiento")
        session.add_response(
            node_id="EMPEORÉ_COMMAND",
            response="/empeore",
            message_text=response_message
        )
        # Marcar la sesión como completada inmediatamente
        session.complete_session(final_message="Protocolo de exacerbación activado")
        await db_repository.create_session(session)
        logger.info(f"Sesión de empeoramiento creada y completada para usuario {user_id} por comando /empeore")
    except Exception as e:
        logger.error(f"Error al crear sesión de empeoramiento: {e}")
    
    # Establecer nodo actual en filtro_1 (para futuras interacciones)
    user_db.current_node = "filtro_1"
    await db_repository.update_user(user_db)
    context.user_data["current_node"] = "filtro_1"
    
    # Enviar solo el mensaje de activación del protocolo
    await update.message.reply_text(response_message)
    
    # La interacción termina aquí
    return ConversationState.RESPONDING

if __name__ == "__main__":
    try:
        # Use asyncio.run for Python 3.12
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        logger.error(traceback.format_exc()) 
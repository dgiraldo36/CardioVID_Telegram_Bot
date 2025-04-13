# 📱 CardioVID-Bot: Plan de Migración de Telegram a WhatsApp Cloud API

## 🔍 Visión General

Este documento presenta un plan completo para migrar el CardioVID-Bot de Telegram a la plataforma WhatsApp Cloud API, ampliando su alcance a pacientes con EPOC que utilizan WhatsApp como su plataforma principal de mensajería.

---

## 📋 Requisitos Previos

### Requisitos de WhatsApp Business

- [ ] Crear una Cuenta de WhatsApp Business (WABA)
- [ ] Registrar una cuenta de Meta Developer
- [ ] Crear una aplicación en el Portal de Desarrolladores de Meta
- [ ] Configurar una cuenta verificada de Business Manager
- [ ] Obtener un número de teléfono para la API de WhatsApp Business
- [ ] Configurar la verificación de dos pasos con un PIN de 6 dígitos
- [ ] Generar un token de acceso con permiso `whatsapp_business_messaging`

### Requisitos Técnicos

- [ ] Endpoint HTTPS público para webhooks (p.ej., Ngrok para desarrollo)
- [ ] Actualizar el entorno de desarrollo con SDK/bibliotecas de WhatsApp
- [ ] Verificar compatibilidad con MongoDB (la configuración actual sigue siendo válida)

---

## 🔄 Comparación de Arquitectura

| Componente | Bot de Telegram | WhatsApp Cloud API | Impacto de Migración |
|-----------|--------------|-------------------|------------------|
| **Autenticación** | Token de bot | Token de acceso + Secreto de App | Medio |
| **Recepción de Mensajes** | Long polling | Webhooks | Alto |
| **Interfaz de Usuario** | InlineKeyboard | Mensajes interactivos (botones, listas) | Medio |
| **Gestión de Estado** | ConversationHandler | Requiere implementación personalizada | Medio |
| **Soporte de Medios** | Métodos nativos | Diferentes endpoints de API | Bajo |
| **Límites de Tasa** | Liberal | Estricto (1K/día inicial, ventana de 24h) | Alto |
| **Base de Datos** | MongoDB | MongoDB (sin cambios) | Ninguno |
| **Lógica de Conversación** | Flujo basado en nodos | Flujo basado en nodos (reutilizable) | Bajo |

---

## 💰 Costos Asociados a WhatsApp Cloud API

A diferencia de Telegram, que es completamente gratuito para bots, WhatsApp Cloud API opera bajo un modelo de precios basado en conversaciones. Es importante considerar estos costos en la planificación del proyecto.

### Costos de Configuración Inicial

| Concepto | Costo (USD) | Detalles |
|----------|-------------|----------|
| Registro de número telefónico | $5 - $15 / mes | Varía según el país y tipo de número |
| Configuración de Business Manager | Gratuito | Requiere verificación de negocio |
| Registro de WABA | Gratuito | Cuenta de WhatsApp Business |

### Modelo de Precios por Conversación

WhatsApp usa un modelo de "ventana de servicio" de 24 horas y clasifica los mensajes en dos categorías principales:

#### 1. Conversaciones Iniciadas por Usuario

| Tipo | Descripción | Límite Gratuito | Costo por Exceder Límite |
|------|-------------|-----------------|--------------------------|
| Conversaciones estándar | Respuestas a mensajes de usuarios dentro de 24h | 1,000 conversaciones/mes | $0.0085 - $0.0311 por conversación* |

#### 2. Conversaciones Iniciadas por Negocio

| Tipo | Descripción | Costo Base |
|------|-------------|------------|
| Conversaciones con plantilla | Usando plantillas pre-aprobadas | $0.0168 - $0.0593 por conversación* |
| Conversaciones con plantilla de marketing | Plantillas promocionales | $0.0311 - $0.0593 por conversación* |

*Los precios varían según el país del destinatario. Ejemplos:
- México: ~$0.0122 por conversación iniciada por usuario
- Colombia: ~$0.0107 por conversación iniciada por usuario
- España: ~$0.0311 por conversación iniciada por usuario

### Consideraciones de Costos para CardioVID-Bot

| Escenario | Estimación Mensual |
|-----------|-------------------|
| 100 pacientes con interacción semanal | Hasta 400 conversaciones - Dentro del límite gratuito |
| 300 pacientes con interacción semanal | ~1,200 conversaciones - ~$1.70/mes adicionales |
| Recordatorios y educación proactiva | ~300 mensajes de plantilla - ~$5.04/mes adicionales |
| Escalado a 1,000 pacientes | ~4,000 conversaciones/mes - ~$25.50/mes |

### Optimización de Costos

1. **Consolidar Mensajes**
   - Agrupar múltiples preguntas en un solo mensaje cuando sea posible
   - Reducir fragmentación en la conversación

2. **Maximizar Ventana de 24 Horas**
   - Diseñar flujos que aprovechen respuestas dentro de la ventana gratuita
   - Planificar seguimientos dentro de las 24 horas de la última interacción

3. **Gestión de Plantillas**
   - Crear plantillas reutilizables para mensajes comunes
   - Minimizar el uso de plantillas de marketing (más costosas)

4. **Modelo de Escala**
   - Plan Inicial: Aprovechar el límite gratuito de 1,000 conversaciones
   - Plan de Crecimiento: Presupuestar $0.01-$0.03 por paciente/semana para interacciones regulares

5. **Monitoreo de Uso**
   - Implementar seguimiento de uso para evitar sorpresas en facturación
   - Establecer alertas cuando se aproxime al 80% del límite gratuito

### Presupuesto Mensual Recomendado

| Fase | Pacientes | Presupuesto Estimado (USD) |
|------|-----------|----------------------------|
| Piloto | 50-100 | $5-15 (principalmente costo del número) |
| Inicial | 100-300 | $15-25 |
| Crecimiento | 300-1,000 | $25-75 |
| Escala | 1,000+ | $75+ (aproximadamente $0.075 por paciente) |

*Nota: Estos costos son estimaciones basadas en precios actuales de Meta y pueden variar. Es recomendable consultar la [página oficial de precios](https://developers.facebook.com/docs/whatsapp/pricing/) para información actualizada.*

---

## 📝 Plan de Migración Paso a Paso

### 1️⃣ Configuración de WhatsApp Business

```markdown
- Registrarse para acceso a WhatsApp Business API
- Configurar webhooks en el Portal de Desarrolladores de Meta
- Configurar verificación de dos pasos
- Crear plantillas de mensajes para contacto inicial (si es necesario)
- Probar la conectividad básica con la API de WhatsApp
```

### 2️⃣ Actualizaciones de la Estructura del Proyecto

```
cardiovid-bot-whatsapp/
├── README.md
├── requirements.txt
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── src/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada (cambios mayores)
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Añadir configuraciones específicas de WhatsApp
│   ├── conversation/
│   │   ├── __init__.py
│   │   ├── manager.py          # Cambios mínimos
│   │   └── models.py           # Añadir tipos de mensajes de WhatsApp
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py           # Cambios mínimos
│   │   └── repository.py       # No se necesitan cambios
│   └── whatsapp/               # Nuevo directorio
│       ├── __init__.py
│       ├── client.py           # Cliente de API de WhatsApp
│       ├── handlers.py         # Manejadores de mensajes
│       ├── templates.py        # Plantillas de mensajes
│       ├── webhook.py          # Manejador de webhook
│       └── message_builder.py  # Utilidades de formato de mensajes
└── tests/
    ├── __init__.py
    └── test_whatsapp.py        # Pruebas específicas de WhatsApp
```

### 3️⃣ Actualizar Dependencias

```python
# requirements.txt
requests==2.31.0       # Para llamadas a la API de WhatsApp
fastapi==0.104.1       # Para el servidor webhook
uvicorn==0.23.2        # Servidor ASGI
pydantic==2.3.0        # Misma versión que antes
motor==3.3.0           # Misma versión que antes
pymongo==4.5.0         # Misma versión que antes
python-dotenv==1.0.0   # Misma versión que antes
pytest==7.4.3          # Misma versión que antes
pytest-asyncio==0.21.1 # Misma versión que antes
loguru==0.7.2          # Misma versión que antes
```

### 4️⃣ Implementación del Cliente de WhatsApp

Crear un nuevo módulo cliente de WhatsApp para manejar interacciones con la API:

```python
# src/whatsapp/client.py
import requests
import json
from typing import Dict, Any, Optional
from loguru import logger
from src.config.settings import settings

class WhatsAppClient:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v17.0"
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        
    def send_text_message(self, to: str, text: str) -> Dict[str, Any]:
        """Enviar un mensaje de texto simple a un usuario de WhatsApp"""
        endpoint = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"body": text}
        }
        
        return self._make_request("POST", endpoint, payload)
    
    def send_interactive_message(self, to: str, message_body: str, buttons: list) -> Dict[str, Any]:
        """Enviar un mensaje interactivo con botones"""
        endpoint = f"{self.base_url}/{self.phone_number_id}/messages"
        
        # Formato de botones para la API de WhatsApp
        button_items = []
        for i, button in enumerate(buttons):
            button_items.append({
                "type": "reply",
                "reply": {
                    "id": f"btn_{i}",
                    "title": button[:20]  # WhatsApp limita el texto del botón a 20 caracteres
                }
            })
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": message_body},
                "action": {"buttons": button_items}
            }
        }
        
        return self._make_request("POST", endpoint, payload)
    
    def _make_request(self, method: str, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Realizar solicitud HTTP a la API de WhatsApp"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            if method.upper() == "POST":
                response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
            else:
                response = requests.get(endpoint, headers=headers)
                
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en solicitud a API de WhatsApp: {str(e)}")
            return {"error": str(e)}
```

### 5️⃣ Implementación del Webhook

Crear un manejador de webhook usando FastAPI:

```python
# src/whatsapp/webhook.py
from fastapi import FastAPI, Request, Response, BackgroundTasks, Depends
from loguru import logger
import hmac
import hashlib
import json
from typing import Dict, Any

from src.config.settings import settings
from src.conversation.manager import ConversationManager
from src.db.repository import MongoDBRepository
from src.whatsapp.handlers import handle_message

app = FastAPI()
db_repository = MongoDBRepository()
conversation_manager = ConversationManager()

@app.on_event("startup")
async def startup_event():
    await db_repository.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await db_repository.close()

def verify_webhook_signature(request: Request) -> bool:
    """Verificar que la solicitud de webhook sea de Meta"""
    if settings.WHATSAPP_APP_SECRET:
        signature = request.headers.get("x-hub-signature-256", "")
        if not signature:
            return False
            
        # Obtener el cuerpo de la solicitud sin procesar
        body = await request.body()
        
        # Calcular firma esperada
        expected_signature = "sha256=" + hmac.new(
            settings.WHATSAPP_APP_SECRET.encode(), 
            body, 
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    return True  # Omitir verificación si no hay app secret definido

@app.get("/webhook")
async def verify_webhook(request: Request):
    """Manejar verificación de webhook desde WhatsApp"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode and token:
        if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
            logger.info("Webhook verificado")
            return Response(content=challenge)
        else:
            logger.warning("Verificación de webhook fallida")
            return Response(status_code=403)
            
    return Response(status_code=400)

@app.post("/webhook")
async def webhook_handler(request: Request, background_tasks: BackgroundTasks):
    """Manejar eventos entrantes de webhook desde WhatsApp"""
    # Verificar firma del webhook
    if not verify_webhook_signature(request):
        logger.warning("Firma de webhook inválida")
        return Response(status_code=401)
    
    # Procesar datos del webhook
    data = await request.json()
    logger.debug(f"Webhook recibido: {data}")
    
    # Comprobar si es un mensaje de WhatsApp
    if "object" in data and data["object"] == "whatsapp_business_account":
        if "entry" in data and data["entry"]:
            for entry in data["entry"]:
                if "changes" in entry and entry["changes"]:
                    for change in entry["changes"]:
                        if "value" in change and "messages" in change["value"]:
                            # Procesar mensajes en segundo plano para devolver 200 rápidamente
                            background_tasks.add_task(
                                process_messages, 
                                change["value"]["messages"],
                                change["value"]["contacts"] if "contacts" in change["value"] else []
                            )
    
    # Siempre devolver 200 OK para confirmar recepción
    return Response(status_code=200)

async def process_messages(messages: list, contacts: list):
    """Procesar mensajes entrantes de WhatsApp"""
    for message in messages:
        # Extraer información de contacto si está disponible
        contact_info = {}
        for contact in contacts:
            if contact["wa_id"] == message["from"]:
                contact_info = contact["profile"]
                break
                
        # Manejar el mensaje
        await handle_message(
            message, 
            contact_info, 
            conversation_manager, 
            db_repository
        )
```

### 6️⃣ Manejadores de Mensajes

Implementar manejadores de mensajes para procesar mensajes entrantes de WhatsApp:

```python
# src/whatsapp/handlers.py
from loguru import logger
from datetime import datetime
from typing import Dict, Any, Optional

from src.conversation.manager import ConversationManager
from src.db.repository import MongoDBRepository
from src.db.models import UserDB
from src.whatsapp.client import WhatsAppClient

whatsapp_client = WhatsAppClient()

async def handle_message(
    message: Dict[str, Any], 
    contact_info: Dict[str, Any],
    conversation_manager: ConversationManager,
    db_repository: MongoDBRepository
):
    """Manejar mensajes entrantes de WhatsApp"""
    # Extraer datos del mensaje
    message_type = message.get("type")
    sender_id = message.get("from")
    
    if not sender_id:
        logger.error("No se encontró ID de remitente en el mensaje")
        return
    
    # Obtener o crear usuario
    user_db = await get_or_create_user(sender_id, contact_info, db_repository)
    
    # Comprobar tipo de mensaje y procesar en consecuencia
    if message_type == "text":
        await handle_text_message(
            sender_id, 
            message["text"]["body"], 
            user_db, 
            conversation_manager, 
            db_repository
        )
    elif message_type == "interactive":
        await handle_interactive_message(
            sender_id,
            message["interactive"],
            user_db,
            conversation_manager,
            db_repository
        )
    else:
        # Enviar mensaje predeterminado para tipos de mensajes no soportados
        whatsapp_client.send_text_message(
            sender_id,
            "Por favor, usa los botones proporcionados para responder o envía texto."
        )

async def get_or_create_user(
    wa_id: str, 
    contact_info: Dict[str, Any],
    db_repository: MongoDBRepository
) -> UserDB:
    """Obtener usuario existente o crear uno nuevo"""
    # Convertir ID de WhatsApp a entero para almacenamiento (eliminar prefijo + si está presente)
    telegram_id = int(wa_id.lstrip("+"))
    
    user_db = await db_repository.get_user(telegram_id)
    if not user_db:
        # Crear nuevo usuario
        first_name = contact_info.get("name", "Usuario")
        user_db = UserDB.create_new(
            telegram_id=telegram_id,
            first_name=first_name,
            username=None
        )
        await db_repository.create_user(user_db)
        
        # Inicializar conversación
        user_db.current_node = "saludo_inicial"
        await db_repository.update_user(user_db)
        
        # Enviar mensaje de bienvenida
        await send_node_message(telegram_id, "saludo_inicial", user_db, conversation_manager)
    
    return user_db

async def handle_text_message(
    sender_id: str,
    text: str,
    user_db: UserDB,
    conversation_manager: ConversationManager,
    db_repository: MongoDBRepository
):
    """Manejar mensajes de texto"""
    # Comprobar palabras clave específicas
    if text.upper() == "EMPEORÉ":
        # Actualizar estado del usuario
        user_db.current_node = "filtro_1"
        await db_repository.update_user(user_db)
        
        # Enviar mensaje de reconocimiento
        whatsapp_client.send_text_message(
            sender_id,
            "He detectado que tus síntomas han empeorado. "
            "Te estamos redirigiendo al protocolo de exacerbación..."
        )
        
        # Enviar mensaje del nodo de filtro
        await send_node_message(sender_id, "filtro_1", user_db, conversation_manager)
    
    elif text.upper() in ["HOLA", "INICIAR", "START"]:
        # Reiniciar conversación
        user_db.current_node = "saludo_inicial"
        await db_repository.update_user(user_db)
        
        # Enviar mensaje de bienvenida
        await send_node_message(sender_id, "saludo_inicial", user_db, conversation_manager)
    
    elif text.upper() == "AYUDA" or text.upper() == "HELP":
        # Enviar mensaje de ayuda
        help_text = (
            "📋 *CardioVID-Bot - Ayuda*\n\n"
            "Este bot te permite monitorear tus síntomas de EPOC "
            "y recibir recomendaciones médicas.\n\n"
            "Comandos disponibles:\n"
            "INICIAR - Iniciar el bot\n"
            "AYUDA - Mostrar esta ayuda\n"
            "REINICIAR - Reiniciar la conversación\n\n"
            "Si en algún momento presentas síntomas de empeoramiento, "
            "escribe la palabra EMPEORÉ y seguiremos el protocolo."
        )
        whatsapp_client.send_text_message(sender_id, help_text)
    
    else:
        # Respuesta predeterminada para texto no reconocido
        whatsapp_client.send_text_message(
            sender_id,
            "Por favor, usa los botones proporcionados para responder.\n\n"
            "Si tus síntomas han empeorado, escribe EMPEORÉ."
        )

async def handle_interactive_message(
    sender_id: str,
    interactive_data: Dict[str, Any],
    user_db: UserDB,
    conversation_manager: ConversationManager,
    db_repository: MongoDBRepository
):
    """Manejar mensajes interactivos (respuestas de botones)"""
    interactive_type = interactive_data.get("type")
    
    # Extraer la selección del usuario basada en el tipo interactivo
    selected_option = None
    if interactive_type == "button_reply":
        # Obtener texto del botón desde ID
        button_id = interactive_data["button_reply"]["id"]
        button_index = int(button_id.split("_")[1])
        
        # Obtener nodo actual para encontrar la opción correspondiente
        current_node = conversation_manager.get_node(user_db.current_node)
        if current_node and current_node.options and button_index < len(current_node.options):
            selected_option = current_node.options[button_index].text
    
    if not selected_option:
        logger.error(f"No se pudo extraer la opción seleccionada del mensaje interactivo: {interactive_data}")
        whatsapp_client.send_text_message(
            sender_id,
            "Lo siento, no pude procesar tu respuesta. Por favor, intenta nuevamente."
        )
        return
    
    # Registrar respuesta del usuario
    timestamp = datetime.now().isoformat()
    user_db.responses[user_db.current_node] = {
        "answer": selected_option,
        "timestamp": timestamp
    }
    user_db.last_interaction = timestamp
    
    # Obtener siguiente nodo basado en selección
    next_node_id = conversation_manager.get_next_node_id(user_db.current_node, selected_option)
    if not next_node_id:
        logger.warning(f"No se encontró nodo siguiente para {user_db.current_node} con opción {selected_option}")
        whatsapp_client.send_text_message(
            sender_id,
            "Gracias por tu respuesta. La conversación ha finalizado."
        )
        return
    
    # Actualizar nodo actual del usuario
    user_db.current_node = next_node_id
    await db_repository.update_user(user_db)
    
    # Enviar mensaje del siguiente nodo
    await send_node_message(sender_id, next_node_id, user_db, conversation_manager)

async def send_node_message(
    recipient_id: str,
    node_id: str,
    user_db: UserDB,
    conversation_manager: ConversationManager
):
    """Enviar mensaje apropiado para el nodo de conversación actual"""
    node = conversation_manager.get_node(node_id)
    if not node:
        logger.error(f"Nodo {node_id} no encontrado")
        return
    
    # Formatear mensaje con datos de usuario
    user_data = {"nombre": user_db.first_name}
    message_text = conversation_manager.format_message(node, user_data)
    
    # Comprobar si el nodo tiene opciones para botones interactivos
    if node.options and len(node.options) > 0:
        # Extraer textos de opciones para botones (limitado a 3 para WhatsApp)
        button_texts = [option.text for option in node.options[:3]]
        
        # Enviar mensaje interactivo con botones
        whatsapp_client.send_interactive_message(recipient_id, message_text, button_texts)
    else:
        # Enviar mensaje de texto simple
        whatsapp_client.send_text_message(recipient_id, message_text)
```

### 7️⃣ Actualizar Configuración

Actualizar el archivo de configuración para incluir configuraciones específicas de WhatsApp:

```python
# src/config/settings.py (solo adiciones)
class Settings(BaseModel):
    # Configuraciones existentes...
    
    # Configuraciones de API de WhatsApp
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    WHATSAPP_ACCESS_TOKEN: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    WHATSAPP_APP_SECRET: str = os.getenv("WHATSAPP_APP_SECRET", "")
    WHATSAPP_VERIFY_TOKEN: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
    WHATSAPP_WEBHOOK_URL: str = os.getenv("WHATSAPP_WEBHOOK_URL", "")
```

### 8️⃣ Actualizar Variables de Entorno

```bash
# .env.example (adiciones)
# Configuración de API de WhatsApp
WHATSAPP_PHONE_NUMBER_ID=tu_id_de_numero_telefonico
WHATSAPP_ACCESS_TOKEN=tu_token_de_acceso
WHATSAPP_APP_SECRET=tu_secreto_de_app
WHATSAPP_VERIFY_TOKEN=tu_token_de_verificacion_personalizado
WHATSAPP_WEBHOOK_URL=https://tu-dominio.com/webhook
```

---

## ⏱️ Cronograma de Implementación

| Fase | Descripción | Duración |
|-------|-------------|----------|
| **1** | Configuración de WhatsApp Business | 1-2 días |
| **2** | Estructura del Proyecto y Dependencias | 1 día |
| **3** | Implementación del Cliente de WhatsApp | 2 días |
| **4** | Configuración de Webhook | 1 día |
| **5** | Manejadores de Mensajes | 2-3 días |
| **6** | Pruebas y Depuración | 2-3 días |
| **7** | Documentación y Despliegue | 1 día |
| **Total** | | **10-13 días** |

---

## 🧪 Estrategia de Pruebas

### Pruebas Manuales

1. **Flujo de Autenticación**
   - Verificar conectividad de API
   - Probar verificación de webhook

2. **Flujo de Conversación**
   - Probar el flujo completo de evaluación del paciente
   - Verificar que todas las ramas de conversación funcionen correctamente

3. **Casos Límite**
   - Probar comportamiento de límites de tasa de mensajes
   - Probar recuperación de fallos de API
   - Probar conversaciones concurrentes

### Pruebas Automatizadas

1. **Pruebas Unitarias** para componentes principales:
   - Cliente de WhatsApp
   - Análisis de mensajes
   - Manejadores de webhook

2. **Pruebas de Integración**:
   - Integración con MongoDB
   - Flujos completos de conversación

---

## 🚀 Consideraciones de Despliegue

### Entorno de Producción

- Usar un servidor web adecuado (uvicorn detrás de nginx)
- Configurar certificados SSL apropiados para webhooks
- Configurar registro y monitoreo adecuados
- Configurar copias de seguridad automatizadas para la base de datos

### Despliegue con Docker

Actualizar el archivo docker-compose.yml para incluir el servicio de webhook de WhatsApp:

```yaml
version: '3.8'

services:
  whatsapp-webhook:
    build: .
    restart: always
    env_file:
      - .env
    ports:
      - "8000:8000"
    command: uvicorn src.whatsapp.webhook:app --host 0.0.0.0 --port 8000
    volumes:
      - ./logs:/app/logs
    depends_on:
      - mongodb

  mongodb:
    image: mongo:6
    restart: always
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      - MONGO_INITDB_DATABASE=cardiovid_bot

volumes:
  mongodb_data:
```

---

## 🔄 Mantenimiento Post-Despliegue

### Monitoreo

- Configurar monitoreo para límites de tasa de API
- Monitorear éxito de entrega de webhooks
- Configurar alertas para errores críticos

### Mantenimiento Continuo

- Mantener actualizado el token de API de WhatsApp Business
- Monitorear cambios en las políticas de WhatsApp
- Aplicar actualizaciones de seguridad regularmente
- Revisar patrones de interacción de pacientes para oportunidades de mejora

---

## 🛡️ Consideraciones de Seguridad

1. **Protección de Datos**
   - Asegurar que todos los datos de pacientes estén debidamente encriptados
   - Implementar controles de acceso adecuados
   - Cumplir con regulaciones de datos de salud

2. **Seguridad de API**
   - Almacenar credenciales de API de manera segura
   - Validar firmas de webhook
   - Implementar manejo adecuado de errores

3. **Cumplimiento**
   - Asegurar cumplimiento con Política de WhatsApp Business
   - Adherirse a regulaciones de mensajería de salud
   - Mantener registros adecuados de consentimiento

---

## 📊 Métricas de Éxito

Seguir las siguientes métricas para evaluar el éxito de la migración:

1. **Métricas Técnicas**
   - Tasa de entrega exitosa de mensajes
   - Tiempo de respuesta
   - Frecuencia de errores

2. **Métricas de Negocio**
   - Tasa de adopción de usuarios
   - Tasa de finalización de conversación
   - Métricas de satisfacción del paciente
   - Efectividad de intervención médica

---

Este plan de migración proporciona una hoja de ruta completa para la transición del CardioVID-Bot de Telegram a WhatsApp Cloud API, asegurando una interrupción mínima del servicio mientras se maximizan los beneficios del mayor alcance y capacidades interactivas de WhatsApp. 
# 🩺 CardioVID-Bot: Bot de Telegram para Monitoreo de EPOC

<div align="center">
  
![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)

</div>

## 📋 Descripción del Proyecto

CardioVID-Bot es un bot de Telegram diseñado para asistir en el monitoreo de pacientes con EPOC (Enfermedad Pulmonar Obstructiva Crónica) a través de un flujo de conversación estructurado. El bot sigue una ruta de conversación predefinida para evaluar los síntomas del paciente y proporcionar recomendaciones apropiadas o programar citas médicas.

## 🛠️ Stack Tecnológico Recomendado

### 🤖 SDK de Telegram Bot

**Recomendado: aiogram 3.x**

```bash
pip install aiogram==3.1.1
```

<details>
<summary>✨ Características principales</summary>

- Soporte nativo para modelos Pydantic
- Completamente asíncrono
- Sugerencias de tipo y prácticas modernas de Python
- Excelente documentación
- Comunidad activa
</details>

<details>
<summary>🔄 Alternativas</summary>

1. **python-telegram-bot**
   - ✅ Pros: SDK más popular, bien documentado
   - ❌ Cons: Menor integración nativa con Pydantic

2. **pyTelegramBotAPI (telebot)**
   - ✅ Pros: Simple y fácil de usar
   - ❌ Cons: Menos estructurado para flujos de conversación complejos

3. **Telethon**
   - ✅ Pros: Acceso completo a la API del cliente de Telegram
   - ❌ Cons: Puede ser excesivo para un bot, menos funcionalidad específica para bots
</details>

### 💾 Base de Datos

**Recomendado: MongoDB**

MongoDB es una excelente elección para este proyecto por varias razones:

- Esquema flexible que puede adaptarse a medida que evoluciona el proyecto
- Estructura de documentos similar a JSON que refleja los formatos de respuesta de Telegram
- Buen rendimiento para cargas de trabajo con predominio de lectura
- Configuración y mantenimiento simples

```bash
pip install motor==3.3.0  # Driver MongoDB asíncrono
pip install pymongo==4.5.0  # Driver MongoDB síncrono (si es necesario)
```

<details>
<summary>🔄 Alternativas</summary>

1. **PostgreSQL (con SQLAlchemy)**
   - ✅ Pros: Conformidad ACID, datos estructurados
   - ❌ Cons: Esquema más rígido, requiere más configuración para cambios

2. **Redis**
   - ✅ Pros: Muy rápido, bueno para almacenar en caché estados de usuarios
   - ❌ Cons: No ideal como base de datos principal para todos los datos de usuario

3. **SQLite**
   - ✅ Pros: Configuración cero, portátil
   - ❌ Cons: No adecuado para producción o acceso concurrente
</details>

## 📝 Plan de Implementación del Proyecto

### Fase 1: Configuración y Estructura Básica

1. **Configuración del Entorno**
   - Crear entorno virtual
   - Instalar dependencias
   - Configurar gestión de configuración

2. **Registro del Bot**
   - Registrar bot con BotFather
   - Obtener token API
   - Configurar webhook o mecanismo de polling

3. **Estructura Básica del Proyecto**
   - Definir estructura de carpetas
   - Crear instancia básica del bot
   - Implementar registro de logs

### Fase 2: Implementación del Flujo de Conversación

1. **Modelo de Conversación**
   - Analizar y validar conversation.json usando Pydantic
   - Crear sistema de gestión de estados

2. **Manejadores de Mensajes**
   - Implementar manejadores para diferentes estados de conversación
   - Configurar lógica de teclado y botones

3. **Gestión del Estado del Usuario**
   - Seguimiento de la posición del usuario en la conversación
   - Almacenar respuestas del usuario

### Fase 3: Integración de Base de Datos

1. **Diseño del Esquema de Base de Datos**
   - Colección de usuarios
   - Colección de historial de conversaciones
   - Colección de datos de salud del usuario

2. **Operaciones de Base de Datos**
   - Operaciones CRUD para datos de usuario
   - Optimizaciones de consultas
   - Estrategia de respaldo

### Fase 4: Pruebas y Despliegue

1. **Pruebas**
   - Pruebas unitarias para manejadores
   - Pruebas de flujo de conversación
   - Pruebas de integración con MongoDB

2. **Despliegue**
   - Contenerización con Docker
   - Configuración de pipeline CI/CD
   - Configuración del entorno de producción

## 📊 Ejemplos de Modelos Pydantic

```python
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ConversationOption(BaseModel):
    text: str
    next: Optional[str] = None

class ConversationNode(BaseModel):
    id: str
    message: str
    options: Optional[List[ConversationOption]] = None
    next: Optional[str] = None

class Conversation(BaseModel):
    conversation: List[ConversationNode]

class User(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    current_node: str
    responses: Dict[str, Any] = {}
    registered_at: str
    education_opt_in: bool = False
```

## 📂 Estructura del Proyecto

```
cardiovid-bot/
├── README.md
├── requirements.txt
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── src/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada
│   │   ├── __init__.py
│   │   ├── handlers.py         # Manejadores de mensajes
│   │   ├── keyboards.py        # Generadores de teclado
│   │   └── middlewares.py      # Middlewares del bot
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Configuración de la aplicación
│   ├── conversation/
│   │   ├── __init__.py
│   │   ├── manager.py          # Gestión de estado de conversación
│   │   └── models.py           # Modelos Pydantic
│   └── db/
│       ├── __init__.py
│       ├── models.py           # Modelos de base de datos
│       └── repository.py       # Operaciones de base de datos
└── tests/
    ├── __init__.py
    ├── test_handlers.py
    └── test_conversation.py
```

## 🗄️ Diseño del Esquema MongoDB

### Colección de Usuarios
```json
{
  "_id": ObjectId,
  "telegram_id": 123456789,
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "current_node": "filtro_1",
  "responses": {
    "saludo_inicial": {"answer": "Sí", "timestamp": "2023-06-01T10:30:00Z"},
    "filtro_1": {"answer": "Sí a 2 o más", "timestamp": "2023-06-01T10:32:00Z"}
  },
  "education_opt_in": true,
  "registered_at": "2023-06-01T10:30:00Z",
  "last_interaction": "2023-06-01T10:32:00Z"
}
```

## 🚀 Próximos Pasos

1. Clonar este repositorio
2. Configurar tu entorno virtual
3. Instalar dependencias con `pip install -r requirements.txt`
4. Crear un archivo `.env` basado en `.env.example`
5. Ejecutar el bot con `python src/main.py`

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor, siéntete libre de enviar un Pull Request.

---

<div align="center">
  
  **Desarrollado con ❤️ para la Clínica CardioVID**
  
</div> 
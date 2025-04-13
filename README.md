# 🩺 CardioVID-Bot: Bot de Telegram para Monitoreo de EPOC

<div align="center">
  
![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)

</div>

## 📋 Descripción del Proyecto

CardioVID-Bot es un bot de Telegram diseñado para asistir en el monitoreo de pacientes con EPOC (Enfermedad Pulmonar Obstructiva Crónica) a través de un flujo de conversación estructurado. El bot sigue una ruta de conversación predefinida para evaluar los síntomas del paciente y proporcionar recomendaciones apropiadas o programar citas médicas.

## ✨ Funcionalidades Implementadas

### 🤖 Características Principales

- **Conversación Estructurada**: Flujo de conversación guiado por nodos definidos en JSON.
- **Botones Interactivos**: Uso de teclados en línea para facilitar respuestas.
- **Sesiones de Usuario**: Registro completo de cada interacción en MongoDB.
- **Protocolo de Exacerbación**: Activación rápida escribiendo "EMPEORÉ" o usando el comando `/empeore`.
- **Historial de Sesiones**: Visualización del historial de interacciones pasadas.
- **Menú de Comandos**: Acceso rápido a todas las funciones mediante el menú nativo de Telegram.

### 📱 Comandos Disponibles

- `/start` - Iniciar o reiniciar el bot
- `/help` - Mostrar ayuda y comandos disponibles
- `/reset` - Reiniciar la conversación desde el inicio
- `/historial` - Ver el historial de interacciones pasadas
- `/empeore` - Reportar empeoramiento de síntomas (inicia el protocolo de exacerbación)

### 💾 Almacenamiento de Datos

El bot almacena en MongoDB:

1. **Información del Usuario**: Datos básicos del usuario de Telegram.
2. **Sesiones Completas**: Todas las interacciones desde el inicio hasta el fin de cada sesión.
3. **Mensajes Finales**: Registro del estado final de cada sesión (completada normalmente, reiniciada o por empeoramiento).
4. **Historial de Respuestas**: Todas las respuestas proporcionadas por el usuario durante la conversación.

### 🔔 Notificaciones y Recordatorios

- Recordatorios periódicos sobre la opción de reportar empeoramiento.
- Mensajes claros sobre el estado actual de la conversación.
- Indicaciones sobre cómo proceder en caso de síntomas graves.

## 🛠️ Stack Tecnológico

- **Framework**: python-telegram-bot
- **Base de Datos**: MongoDB (con motor para operaciones asíncronas)
- **Validación de Datos**: Pydantic
- **Registro**: Loguru
- **Configuración**: dotenv para variables de entorno

## 📊 Modelos de Datos

### Usuario (UserDB)
```python
class UserDB(BaseModel):
    telegram_id: int                    # ID único de Telegram
    username: Optional[str] = None      # Nombre de usuario (opcional)
    first_name: str                     # Nombre del usuario
    last_name: Optional[str] = None     # Apellido (opcional)
    current_node: str                   # Nodo actual en la conversación
    responses: Dict[str, Any]           # Historial de respuestas por nodo
    registered_at: str                  # Fecha de registro
    last_interaction: str               # Última interacción
    education_opt_in: bool = False      # Opt-in para contenido educativo
```

### Sesión de Usuario (UserSession)
```python
class UserSession(BaseModel):
    telegram_id: int                    # ID del usuario
    session_id: str                     # ID único de la sesión
    start_time: str                     # Hora de inicio
    end_time: str                       # Hora de finalización
    session_type: str                   # Tipo: "normal" o "empeoramiento"
    responses: List[NodeResponse]       # Lista de respuestas en la sesión
    completed: bool = False             # Si la sesión está completada
    final_message: Optional[str] = None # Mensaje de finalización
```

## 📂 Estructura del Proyecto

```
cardiovid-bot/
├── README.md
├── requirements.txt
├── .env
├── conversation.json           # Definición del flujo de conversación
├── src/
│   ├── main.py                 # Punto de entrada
│   ├── config/
│   │   └── settings.py         # Configuración de la aplicación
│   ├── conversation/
│   │   ├── manager.py          # Gestión del estado de conversación
│   │   └── models.py           # Modelos de la conversación
│   └── db/
│       ├── models.py           # Modelos de base de datos
│       └── repository.py       # Operaciones de MongoDB
└── logs/
    └── bot.log                 # Archivos de registro
```

## 🗄️ Esquema MongoDB

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

### Colección de Sesiones
```json
{
  "_id": ObjectId,
  "telegram_id": 123456789,
  "session_id": "123456789_2023-06-01T10:30:00Z",
  "start_time": "2023-06-01T10:30:00Z",
  "end_time": "2023-06-01T10:45:00Z",
  "session_type": "normal",
  "responses": [
    {
      "node_id": "saludo_inicial",
      "response": "Sí",
      "timestamp": "2023-06-01T10:30:00Z",
      "message_text": "Hola, ¿cómo te sientes hoy?"
    },
    {
      "node_id": "filtro_1",
      "response": "Sí a 2 o más",
      "timestamp": "2023-06-01T10:32:00Z",
      "message_text": "¿Has tenido alguno de estos síntomas?"
    }
  ],
  "completed": true,
  "final_message": "Conversación finalizada"
}
```

## 🚀 Configuración y Ejecución

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/usuario/cardiovid-bot.git
   cd cardiovid-bot
   ```

2. **Configurar entorno**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**:
   Crear un archivo `.env` con:
   ```
   BOT_TOKEN=your_bot_token_from_botfather
   BOT_NAME=your_bot_name
   MONGODB_CONNECTION_STRING=your_mongodb_connection_string
   MONGODB_DATABASE=cardiovid_bot
   LOG_LEVEL=INFO
   ```

4. **Ejecutar el bot**:
   ```bash
   python src/main.py
   ```

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor, siéntete libre de enviar un Pull Request.

## 📈 Próximas mejoras

- Implementación de detección de sesiones abandonadas
- Análisis estadístico de respuestas de usuarios
- Expansión del flujo de conversación para más condiciones médicas
- Integración con sistemas de alertas para el personal médico
- Recordatorios programados para seguimiento de pacientes

---

<div align="center">
  
  **Desarrollado con ❤️ para la Clínica CardioVID**
  
</div> 
# 💰 Costos Asociados a WhatsApp Cloud API

A diferencia de Telegram, que es completamente gratuito para bots, WhatsApp Cloud API opera bajo un modelo de precios basado en conversaciones. Es importante considerar estos costos en la planificación del proyecto.

## Costos de Configuración Inicial

| Concepto | Costo (USD) | Detalles |
|----------|-------------|----------|
| Registro de número telefónico | $5 - $15 / mes | Varía según el país y tipo de número |
| Configuración de Business Manager | Gratuito | Requiere verificación de negocio |
| Registro de WABA | Gratuito | Cuenta de WhatsApp Business |

## Modelo de Precios por Conversación

WhatsApp usa un modelo de "ventana de servicio" de 24 horas y clasifica los mensajes en dos categorías principales:

### 1. Conversaciones Iniciadas por Usuario

| Tipo | Descripción | Límite Gratuito | Costo por Exceder Límite |
|------|-------------|-----------------|--------------------------|
| Conversaciones estándar | Respuestas a mensajes de usuarios dentro de 24h | 1,000 conversaciones/mes | $0.0085 - $0.0311 por conversación* |

### 2. Conversaciones Iniciadas por Negocio

| Tipo | Descripción | Costo Base |
|------|-------------|------------|
| Conversaciones con plantilla | Usando plantillas pre-aprobadas | $0.0168 - $0.0593 por conversación* |
| Conversaciones con plantilla de marketing | Plantillas promocionales | $0.0311 - $0.0593 por conversación* |

*Los precios varían según el país del destinatario. Ejemplos:
- México: ~$0.0122 por conversación iniciada por usuario
- Colombia: ~$0.0107 por conversación iniciada por usuario
- España: ~$0.0311 por conversación iniciada por usuario

## Consideraciones de Costos para CardioVID-Bot

| Escenario | Estimación Mensual |
|-----------|-------------------|
| 100 pacientes con interacción semanal | Hasta 400 conversaciones - Dentro del límite gratuito |
| 300 pacientes con interacción semanal | ~1,200 conversaciones - ~$1.70/mes adicionales |
| Recordatorios y educación proactiva | ~300 mensajes de plantilla - ~$5.04/mes adicionales |
| Escalado a 1,000 pacientes | ~4,000 conversaciones/mes - ~$25.50/mes |

## Optimización de Costos

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

## Presupuesto Mensual Recomendado

| Fase | Pacientes | Presupuesto Estimado (USD) |
|------|-----------|----------------------------|
| Piloto | 50-100 | $5-15 (principalmente costo del número) |
| Inicial | 100-300 | $15-25 |
| Crecimiento | 300-1,000 | $25-75 |
| Escala | 1,000+ | $75+ (aproximadamente $0.075 por paciente) |

*Nota: Estos costos son estimaciones basadas en precios actuales de Meta y pueden variar. Es recomendable consultar la [página oficial de precios](https://developers.facebook.com/docs/whatsapp/pricing/) para información actualizada.* 
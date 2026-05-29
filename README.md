# Zeroagent

> Una herramienta para crear chatbots rapidamente con una libreria.

## Características
Maneja la memoria en archivos .zr que guardan el historial de conversaciones, y estos archivos se generan automaticamente con un titulo de hasta 5 palabras.
Maneja el modelo de genai en un archivo Settings.zr, y se puede cambiar facilmente. y de mas parametros

## Parametros
1. System_Instruction : Instrucciones que se le dan al agente.
2. Model : Modelo que se usa para generar las respuestas.
3. API_Key : Clave de api para el modelo.
4. Memory : booleano que indica si se debe guardar la memoria.
5. Request_Delay : Tiempo de espera entre peticiones.

## Ejemplo de uso

```python
import Agent

# Cargar configuraciones
Agent.LoadAll()

# Cambiar personalidad del agente
Agent.System_Instruction = "Eres un pirata simpático e ingenioso que habla español y siempre usa modismos piratas como '¡Ahoy, camarada!' o '¡Rayos y truenos!'."

# Habilitar busqueda web
Agent.Google_Search_Tool = True

# Iniciar conversacion
Agent.New_Conversation()

# Enviar mensaje
stream = Agent.Create_Chat("Hola, ¿quién eres?", stream=True)
for chunk in stream:
    print(chunk, end="", flush=True)
```

## Cosas por añadir al futuro
1. Sistema de buses para mensajes 
2. Implementacion con otras ias

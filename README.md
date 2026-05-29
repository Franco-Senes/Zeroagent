# 🤖 ZeroAgent

> Un agente de Inteligencia Artificial potente, modular y altamente personalizable basado en la última SDK oficial de **Google GenAI** (`google-genai`).

ZeroAgent está diseñado para ofrecer una experiencia interactiva avanzada en la terminal, incorporando características de nivel de producción como memoria persistente de conversaciones, streaming inteligente, recuperación automática de límites de cuota, delay adaptativo y herramientas de búsqueda web (Google Search Grounding).

---

## ✨ Características Principales

* **🧠 Memoria Persistente Dinámica**: Guarda automáticamente el historial de conversaciones y crea archivos estructurados `.zr` para reanudar sesiones. ¡Genera títulos contextuales de hasta 5 palabras automáticamente para cada conversación!
* **⚡ Respuestas en Streaming**: Renderizado en tiempo real de tokens para una experiencia interactiva sumamente fluida.
* **🔍 Google Search Grounding**: Conexión directa a Google Search para obtener información actualizada en tiempo real.
* **🛡️ Recuperación Inteligente de Errores (429)**: Si superas la cuota de búsqueda de Google, ZeroAgent desactiva la herramienta automáticamente y vuelve a intentar la solicitud sin interrumpir la experiencia. Maneja de forma transparente los tiempos de espera sugeridos por la API.
* **⚙️ Retraso de Peticiones Adaptativo (Request Delay)**: Configuración configurable de retraso entre peticiones para evitar bloqueos y rate-limits en entornos de alta demanda.
* **🎭 Instrucciones de Sistema Personalizables**: Cambia la personalidad y directrices del agente al vuelo (ej: un pirata simpático, un asistente técnico, etc.).

---

## 🛠️ Estructura del Proyecto

* **`Agent.py`**: El núcleo del agente que maneja la inicialización del cliente Gemini, el flujo de streaming, la persistencia de la memoria y la lógica de recuperación de cuotas.
* **`Settings.zr`**: Archivo de configuración local donde se guarda el modelo preferido, la clave de API (API Key) y las banderas de memoria.
* **`test.py`**: Suite de pruebas completa para demostrar las capacidades del agente interactivo en un flujo de conversación real.

---

## 🚀 Guía de Inicio Rápido

### 1. Requisitos Previos

Asegúrate de tener instalado Python 3.10+ y la librería oficial de Google GenAI:

```bash
pip install google-genai
```

### 2. Configuración de API Key

Ejecuta el agente por primera vez o crea un archivo `Settings.zr` en el directorio raíz con el siguiente formato:

```json
{
    "Model": "gemini-2.5-flash",
    "API Key": "TU_API_KEY_AQUÍ",
    "Memory": true,
    "Request_Delay": 0
}
```

*Nota: El archivo `Settings.zr` está excluido en el `.gitignore` por motivos de seguridad para evitar que subas accidentalmente tu API Key a repositorios públicos.*

### 3. Ejecutar la Suite de Pruebas

Para probar las funcionalidades de streaming, búsqueda web y memoria, ejecuta:

```bash
python test.py
```

---

## 📝 Ejemplo de Uso Rápido

```python
import Agent

# 1. Cargar configuraciones
Agent.LoadAll()

# 2. Configurar personalidad e instrucciones
Agent.System_Instruction = "Eres un asistente de inteligencia artificial útil, educado y profesional."
Agent.Google_Search_Tool = True

# 3. Enviar mensaje con streaming
stream = Agent.Create_Chat("Hola, ¿cómo estás hoy?", stream=True)
for chunk in stream:
    print(chunk, end="", flush=True)
```

---

## 🔒 Licencia

Este proyecto es de código abierto. Siéntete libre de clonarlo, modificarlo y adaptarlo a tus necesidades.

import google.genai as genai
from google.genai.errors import ClientError, APIError
import json
import os
import re
import time
from datetime import datetime

# Imports para soporte multimodal de imágenes
_PIL_available = False
try:
    from PIL import Image
    import requests
    import io
    _PIL_available = True
except ImportError:
    pass

Maybe = "Maybe"
Memory = Maybe
API_Key = "Maybe"
Model = "Maybe"
Selected_Memory_ID = None
Request_Delay = 0
System_Instruction = "Eres un asistente de inteligencia artificial útil, educado y profesional."
Google_Search_Tool = True
Memory_Context_Ids = None  # Puede ser "All", una lista de IDs como [0, 1] o None
_active_client = None



def LoadSettings():
    global Memory, API_Key, Model, Request_Delay
    if not os.path.exists("Settings.zr"):
        with open("Settings.zr", "w") as f:
            json.dump({
                "Model": "gemini-2.5-flash",
                "API Key": "",
                "Memory": True,
                "Request_Delay": 0,
            }, f, indent=4)
        Model = "gemini-2.5-flash"
        API_Key = ""
        Memory = True
        Request_Delay = 0
    else:
        with open("Settings.zr", "r") as f:
            content = f.read()
        cleaned_content = re.sub(r',(\s*[\]}])', r'\1', content)
        try:
            data = json.loads(cleaned_content)
            Model = data.get("Model", "Maybe")
            API_Key = data.get("API Key", "Maybe")
            Memory = data.get("Memory", "Maybe")
            Request_Delay = data.get("Request_Delay", 0)
        except Exception as e:
            print(f"Error parsing Settings.zr: {e}")


def get_429_delay(e):
    error_msg = str(e)
    match = re.search(r'Please retry in ([\d\.]+)s', error_msg)
    if match:
        return float(match.group(1)) + 0.5
    return 15.0


def Select_Memory(memory_id):
    global Selected_Memory_ID
    Selected_Memory_ID = memory_id
    print(f"Selected memory/conversation ID: {Selected_Memory_ID}")


def New_Conversation():
    global Selected_Memory_ID
    Selected_Memory_ID = None
    print("Started a new conversation session.")


def Create_Chat(prompt, image=None, stream=False):
    global Selected_Memory_ID, System_Instruction, Google_Search_Tool, _active_client, Request_Delay, Memory_Context_Ids
    if Request_Delay > 0:
        print(f"[Delay] Esperando {Request_Delay} segundos antes de enviar la petición...")
        time.sleep(Request_Delay)
    
    # Carga de imagen multimodal
    loaded_image = None
    if image is not None:
        if not _PIL_available:
            raise ImportError(
                "Las librerías 'Pillow' y 'requests' son requeridas para procesar imágenes. "
                "Por favor, instálalas usando: pip install Pillow requests"
            )
        try:
            if isinstance(image, str) and (image.startswith("http://") or image.startswith("https://")):
                print(f"[Multimodal] Descargando imagen desde URL: {image}...")
                response = requests.get(image, timeout=15)
                response.raise_for_status()
                loaded_image = Image.open(io.BytesIO(response.content))
            else:
                print(f"[Multimodal] Cargando imagen desde ruta local: {image}...")
                loaded_image = Image.open(image)
        except Exception as e:
            print(f"Error al cargar la imagen '{image}': {e}")
            raise e

    history = []
    if Selected_Memory_ID is not None:
        file_name = "Memory.zr" if Selected_Memory_ID == 0 else f"Memory{Selected_Memory_ID}.zr"
        if os.path.exists(file_name):
            try:
                with open(file_name, "r") as f:
                    content = f.read()
                cleaned_content = re.sub(r',(\s*[\]}])', r'\1', content)
                data = json.loads(cleaned_content)
                messages = data.get("Messages", [])
                for msg in messages:
                    saved_prompt = msg.get("Prompt", "")
                    saved_response = msg.get("Response", "")
                    if saved_prompt:
                        history.append({"role": "user", "parts": [{"text": saved_prompt}]})
                    if saved_response:
                        history.append({"role": "model", "parts": [{"text": saved_response}]})
                print(f"Loaded memory history from {file_name}")
            except Exception as e:
                print(f"Error loading memory history from {file_name}: {e}")
    
    tools = []
    if Google_Search_Tool:
        tools.append({"google_search": {}})
        
    # Inyectar resúmenes históricos de memoria
    sys_instruction_to_use = System_Instruction
    if Memory_Context_Ids is not None:
        contexto_memoria = ""
        resumenes = GetMemory(Memory_Context_Ids)
        if isinstance(resumenes, dict):
            for cid, res in resumenes.items():
                if res.strip():
                    contexto_memoria += f"- Conversación {cid}: {res.strip()}\n"
        elif isinstance(resumenes, str) and resumenes.strip():
            contexto_memoria += f"- Conversación: {resumenes.strip()}\n"
        
        if contexto_memoria:
            sys_instruction_to_use = f"{System_Instruction}\n\n[CONTEXTO HISTÓRICO DE CHATS ANTERIORES]:\n{contexto_memoria}"

    config = genai.types.GenerateContentConfig(
        system_instruction=sys_instruction_to_use if sys_instruction_to_use else None,
        tools=tools if tools else None
    )
    _active_client = genai.Client(api_key=API_Key)
    if history:
        chat = _active_client.chats.create(model=Model, history=history, config=config)
    else:
        chat = _active_client.chats.create(model=Model, config=config)
    if stream:
        def generator():
            global Google_Search_Tool
            nonlocal chat, config, loaded_image
            for attempt in range(6):
                try:
                    if loaded_image is not None:
                        response_stream = chat.send_message_stream([loaded_image, prompt])
                    else:
                        response_stream = chat.send_message_stream(prompt)
                    
                    compiled_text = ""
                    for chunk in response_stream:
                        text = chunk.text
                        compiled_text += text
                        yield text
                    Save_Memory(prompt, compiled_text)
                    return
                except Exception as e:
                    if "429" in str(e) and attempt < 5:
                        if Google_Search_Tool:
                            print(f"\n[Warning] Límite de cuota superado en Google Search Grounding. Desactivando buscador y reintentando sin herramientas...")
                            Google_Search_Tool = False
                            config = genai.types.GenerateContentConfig(
                                system_instruction=sys_instruction_to_use if sys_instruction_to_use else None,
                                tools=None
                            )
                            if history:
                                chat = _active_client.chats.create(model=Model, history=history, config=config)
                            else:
                                chat = _active_client.chats.create(model=Model, config=config)
                            continue
                        delay = get_429_delay(e)
                        print(f"\n[Warning] Límite de cuota (429) detectado en streaming. Reintentando en {delay:.2f} segundos...")
                        time.sleep(delay)
                        continue
                    raise e
        return generator()
    else:
        for attempt in range(6):
            try:
                if loaded_image is not None:
                    response = chat.send_message([loaded_image, prompt])
                else:
                    response = chat.send_message(prompt)
                response_text = response.text
                Save_Memory(prompt, response_text)
                return response
            except Exception as e:
                if "429" in str(e) and attempt < 5:
                    if Google_Search_Tool:
                        print(f"\n[Warning] Límite de cuota superado en Google Search Grounding. Desactivando buscador y reintentando sin herramientas...")
                        Google_Search_Tool = False
                        config = genai.types.GenerateContentConfig(
                            system_instruction=sys_instruction_to_use if sys_instruction_to_use else None,
                            tools=None
                        )
                        if history:
                            chat = _active_client.chats.create(model=Model, history=history, config=config)
                        else:
                            chat = _active_client.chats.create(model=Model, config=config)
                        continue
                    delay = get_429_delay(e)
                    print(f"\n[Warning] Límite de cuota (429) detectado. Reintentando en {delay:.2f} segundos...")
                    time.sleep(delay)
                    continue
                raise e


def GetMemory(chat_id="All"):
    if not os.path.exists("resumen.json"):
        return {} if chat_id == "All" else ""
    try:
        with open("resumen.json", "r") as f:
            content = f.read()
        cleaned_content = re.sub(r',(\s*[\]}])', r'\1', content)
        data = json.loads(cleaned_content)
        
        if chat_id == "All":
            return data
        elif isinstance(chat_id, list):
            result = {}
            for cid in chat_id:
                cid_str = str(cid)
                if cid_str in data:
                    result[cid_str] = data[cid_str]
            return result
        else:
            return data.get(str(chat_id), "")
    except Exception as e:
        print(f"Error al leer resumen.json: {e}")
        return {} if chat_id == "All" else ""


def _update_summary(file_id, messages):
    global Model, API_Key, Request_Delay
    if Request_Delay > 0:
        time.sleep(Request_Delay)
    
    # Construir el texto de la conversación para resumir
    conversation_text = ""
    for msg in messages:
        p = msg.get("Prompt", "")
        r = msg.get("Response", "")
        conversation_text += f"Usuario: {p}\nAgente: {r}\n\n"
    
    summary_prompt = (
        "Resume de forma muy breve y concisa los puntos clave y acuerdos principales de la siguiente conversación. "
        "Manténlo corto, máximo 2-3 párrafos o puntos bala. Conversación:\n\n" + conversation_text
    )
    
    for attempt in range(6):
        try:
            client = genai.Client(api_key=API_Key)
            res = client.models.generate_content(model=Model, contents=summary_prompt)
            summary_text = res.text.strip()
            
            # Guardar en resumen.json
            resumen_data = {}
            if os.path.exists("resumen.json"):
                try:
                    with open("resumen.json", "r") as f:
                        cleaned_content = re.sub(r',(\s*[\]}])', r'\1', f.read())
                        resumen_data = json.loads(cleaned_content)
                except Exception:
                    pass
            
            resumen_data[str(file_id)] = summary_text
            with open("resumen.json", "w") as f:
                json.dump(resumen_data, f, indent=4)
                
            print(f"[Memoria] Resumen actualizado y guardado en resumen.json para el Chat ID: {file_id}")
            return summary_text
        except Exception as e:
            if "429" in str(e) and attempt < 5:
                delay = get_429_delay(e)
                print(f"[Warning] Límite de cuota (429) en resumen. Reintentando en {delay:.2f} segundos...")
                time.sleep(delay)
                continue
            print(f"Error al generar el resumen de la conversación: {e}")
            break
    return ""


def Save_Memory(prompt, Response):
    global Selected_Memory_ID, _active_client
    file_id = Selected_Memory_ID
    is_new = False
    if file_id is None:
        is_new = True
        if not os.path.exists("Memory.zr"):
            file_name = "Memory.zr"
            file_id = 0
        else:
            i = 1
            while os.path.exists(f"Memory{i}.zr"):
                i += 1
            file_name = f"Memory{i}.zr"
            file_id = i
        Selected_Memory_ID = file_id
    else:
        file_name = "Memory.zr" if file_id == 0 else f"Memory{file_id}.zr"
    messages = []
    title = "Nueva conversación"
    summary = ""
    if os.path.exists(file_name):
        try:
            with open(file_name, "r") as f:
                content = f.read()
            cleaned_content = re.sub(r',(\s*[\]}])', r'\1', content)
            data = json.loads(cleaned_content)
            messages = data.get("Messages", [])
            title = data.get("Title", "Nueva conversación")
            summary = data.get("Summary", "")
        except Exception as e:
            print(f"Error loading existing conversation to append: {e}")
    
    messages.append({
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Prompt": prompt,
        "Response": Response
    })
    
    if is_new:
        if Request_Delay > 0:
            time.sleep(Request_Delay)
        for attempt in range(6):
            try:
                _active_client = genai.Client(api_key=API_Key)
                title_prompt = f"Generate a very short, concise title (max 5 words) for a conversation starting with: '{prompt}'. Return ONLY the title text, no quotes, no extra symbols."
                res = _active_client.models.generate_content(model=Model, contents=title_prompt)
                title = res.text.strip().replace('"', '')
                break
            except Exception as e:
                if "429" in str(e) and attempt < 5:
                    delay = get_429_delay(e)
                    print(f"\n[Warning] Límite de cuota (429) en título. Reintentando en {delay:.2f} segundos...")
                    time.sleep(delay)
                    continue
                print(f"Error generating conversation title: {e}")
                title = f"Conversación {file_id}"
                break

    # Determinar si debemos generar o actualizar el resumen
    num_messages = len(messages)
    if num_messages == 1 or num_messages % 5 == 0:
        print(f"[Memoria] Generando/Actualizando resumen para el turno {num_messages}...")
        summary = _update_summary(file_id, messages)

    try:
        with open(file_name, "w") as f:
            json.dump({
                "Id": file_id,
                "File_Name": file_name,
                "Title": title,
                "Summary": summary,
                "Messages": messages
            }, f, indent=4)
        print(f"Saved turn to conversation '{title}' ({file_name}, ID: {file_id}). Total messages: {len(messages)}")
    except Exception as e:
        print(f"Error saving conversation turn: {e}")



def LoadAll():
    LoadSettings()

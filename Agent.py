#Libaries
import google.genai as genai
from google.genai.errors import ClientError, APIError
import json
import os
import re
import time
from datetime import datetime

#Variables
Maybe = "Maybe"
Memory = Maybe # True = Memory activated, Maybe = Memory being decided, False = Memory deactivated
API_Key = "Maybe" #The Api key 
Model = "Maybe" #The model 
Selected_Memory_ID = None # The selected memory/conversation ID to preload
Request_Delay = 0 # Delay in seconds between requests to avoid rate limits

# Hackathon Agent Features
System_Instruction = "Eres un asistente de inteligencia artificial útil, educado y profesional."
Google_Search_Tool = True # True = Enabled, False = Disabled

# Active Client reference to prevent garbage collection mid-stream
_active_client = None

#Load Settings
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
        #Saves Settings on Ram
        with open("Settings.zr", "r") as f:
            content = f.read()
        
        # Clean trailing commas if any exist (e.g., if manually edited)
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

def Create_Chat(prompt, stream=False):
    global Selected_Memory_ID, System_Instruction, Google_Search_Tool, _active_client, Request_Delay
    
    # Apply automatic delay if set
    if Request_Delay > 0:
        print(f"[Delay] Esperando {Request_Delay} segundos antes de enviar la petición...")
        time.sleep(Request_Delay)
    
    # Load history from the selected memory ID if set
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
    
    # Configure tools and system instruction
    tools = []
    if Google_Search_Tool:
        tools.append({"google_search": {}})
        
    config = genai.types.GenerateContentConfig(
        system_instruction=System_Instruction if System_Instruction else None,
        tools=tools if tools else None
    )
    
    # Create the chat session and persist client in global memory to prevent garbage collection mid-stream
    _active_client = genai.Client(api_key=API_Key)
    if history:
        chat = _active_client.chats.create(model=Model, history=history, config=config)
    else:
        chat = _active_client.chats.create(model=Model, config=config)
    
    if stream:
        def generator():
            global Google_Search_Tool
            nonlocal chat, config
            for attempt in range(6):
                try:
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
                                system_instruction=System_Instruction if System_Instruction else None,
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
        # Send the new prompt to get the response
        for attempt in range(6):
            try:
                response = chat.send_message(prompt)
                response_text = response.text
                # Save the current exchange to memory
                Save_Memory(prompt, response_text)
                return response
            except Exception as e:
                if "429" in str(e) and attempt < 5:
                    if Google_Search_Tool:
                        print(f"\n[Warning] Límite de cuota superado en Google Search Grounding. Desactivando buscador y reintentando sin herramientas...")
                        Google_Search_Tool = False
                        config = genai.types.GenerateContentConfig(
                            system_instruction=System_Instruction if System_Instruction else None,
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

def Save_Memory(prompt, Response):
    global Selected_Memory_ID, _active_client
    
    file_id = Selected_Memory_ID
    is_new = False
    if file_id is None:
        is_new = True
        # Start a new conversation and find the next available ID
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
    if os.path.exists(file_name):
        try:
            with open(file_name, "r") as f:
                content = f.read()
            cleaned_content = re.sub(r',(\s*[\]}])', r'\1', content)
            data = json.loads(cleaned_content)
            messages = data.get("Messages", [])
            title = data.get("Title", "Nueva conversación")
        except Exception as e:
            print(f"Error loading existing conversation to append: {e}")
            
    # Append the new turn
    messages.append({
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Prompt": prompt,
        "Response": Response
    })
    
    # Generate a title if it's the first message of a new conversation
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
    
    # Write back to file
    try:
        with open(file_name, "w") as f:
            json.dump({
                "Id": file_id,
                "File_Name": file_name,
                "Title": title,
                "Messages": messages
            }, f, indent=4)
        print(f"Saved turn to conversation '{title}' ({file_name}, ID: {file_id}). Total messages: {len(messages)}")
    except Exception as e:
        print(f"Error saving conversation turn: {e}")

def LoadAll():
    LoadSettings() #Loads settings
    



    
    


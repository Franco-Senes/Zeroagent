import os
import Agent
import glob
import json
import re
import sys
import time

def print_memory_files():
    print(f"Current saved memory files: {glob.glob('Memory*.zr')}")

def print_file_contents(file_path):
    if os.path.exists(file_path):
        print(f"\n--- Content of {file_path} ---")
        with open(file_path, "r") as f:
            content = f.read()
        cleaned_content = re.sub(r',(\s*[\]}])', r'\1', content)
        print(json.dumps(json.loads(cleaned_content), indent=4))
        print("-" * (len(file_path) + 10))

def main():
    print("=" * 60)
    print("ZeroAgent Hackathon Features Test Script")
    print("=" * 60)

    # Clean up old Memory files first for a clean test run
    for f in glob.glob('Memory*.zr'):
        try:
            os.remove(f)
        except Exception:
            pass

    # 1. Load settings from Settings.zr
    print("\n[Step 1] Loading Settings...")
    Agent.LoadAll()
    print(f"-> Model loaded: {Agent.Model}")
    print(f"-> Memory active: {Agent.Memory}")
    print(f"-> API Key present: {'Yes' if Agent.API_Key else 'No (Empty)'}")

    # 2. Configure Hackathon Features in RAM
    print("\n[Step 2] Configuring Hackathon Agent Settings...")
    Agent.System_Instruction = "Eres un pirata simpático e ingenioso que habla español y siempre usa modismos piratas como '¡Ahoy, camarada!' o '¡Rayos y truenos!'."
    Agent.Google_Search_Tool = True
    Agent.Request_Delay = 2  # Wait 2 seconds before each API call to prevent rate limits
    print(f"-> System Instruction: '{Agent.System_Instruction}'")
    print(f"-> Google Search Grounding Tool: {'ENABLED' if Agent.Google_Search_Tool else 'DISABLED'}")
    print(f"-> Automatic Request Delay: {Agent.Request_Delay} seconds")

    # 3. Start a new conversation session
    print("\n[Step 3] Starting a new conversation session...")
    Agent.New_Conversation()
    print_memory_files()

    # 4. Turn 1 using STREAMING (This will generate a title dynamically)
    print("\n[Step 4] Sending Message 1 using Streaming (stream=True)...")
    prompt = "Hola, ¿quién eres y qué te gusta hacer?"
    print(f"Prompt: '{prompt}'")
    print("AI Response (Streaming): ", end="")
    sys.stdout.flush()

    # Get stream generator
    stream_generator = Agent.Create_Chat(prompt, stream=True)
    
    # Consume generator and print chunks in real-time
    for chunk in stream_generator:
        print(chunk, end="", flush=True)
        time.sleep(0.02) # Subtle artificial delay to make the streaming visual effect pop
    print("\n")

    # Let's see the new conversation title created automatically
    active_file = "Memory.zr" if Agent.Selected_Memory_ID == 0 else f"Memory{Agent.Selected_Memory_ID}.zr"
    print_file_contents(active_file)

    # 5. Turn 2 testing Google Search Grounding live!
    print("\n[Step 5] Sending Message 2 to test Google Search Tool...")
    search_prompt = "Dime, ¿quién ganó la última Champions League masculina?"
    print(f"Prompt: '{search_prompt}'")
    print("AI Response (Streaming): ", end="")
    sys.stdout.flush()

    # Stream the Google Search grounded response
    search_generator = Agent.Create_Chat(search_prompt, stream=True)
    for chunk in search_generator:
        print(chunk, end="", flush=True)
        time.sleep(0.01)
    print("\n")

    # Final print of the conversation file
    print_file_contents(active_file)

    print("=" * 60)
    print("Hackathon Features Test Completed Successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()

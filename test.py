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
    for f in glob.glob('Memory*.zr'):
        try:
            os.remove(f)
        except Exception:
            pass
    print("\n[Step 1] Loading Settings...")
    Agent.LoadAll()
    print(f"-> Model loaded: {Agent.Model}")
    print(f"-> Memory active: {Agent.Memory}")
    print(f"-> API Key present: {'Yes' if Agent.API_Key else 'No (Empty)'}")
    print("\n[Step 2] Configuring Hackathon Agent Settings...")
    Agent.System_Instruction = "Eres un pirata simpático e ingenioso que habla español y siempre usa modismos piratas como '¡Ahoy, camarada!' o '¡Rayos y truenos!'."
    Agent.Google_Search_Tool = True
    Agent.Request_Delay = 2
    print(f"-> System Instruction: '{Agent.System_Instruction}'")
    print(f"-> Google Search Grounding Tool: {'ENABLED' if Agent.Google_Search_Tool else 'DISABLED'}")
    print(f"-> Automatic Request Delay: {Agent.Request_Delay} seconds")
    print("\n[Step 3] Starting a new conversation session...")
    Agent.New_Conversation()
    print_memory_files()
    print("\n[Step 4] Sending Message 1 using Streaming (stream=True)...")
    prompt = "Hola, ¿quién eres y qué te gusta hacer?"
    print(f"Prompt: '{prompt}'")
    print("AI Response (Streaming): ", end="")
    sys.stdout.flush()
    stream_generator = Agent.Create_Chat(prompt, stream=True)
    for chunk in stream_generator:
        print(chunk, end="", flush=True)
        time.sleep(0.02)
    print("\n")
    active_file = "Memory.zr" if Agent.Selected_Memory_ID == 0 else f"Memory{Agent.Selected_Memory_ID}.zr"
    print_file_contents(active_file)
    print("\n[Step 5] Sending Message 2 to test Google Search Tool...")
    search_prompt = "Dime, ¿quién ganó la última Champions League masculina?"
    print(f"Prompt: '{search_prompt}'")
    print("AI Response (Streaming): ", end="")
    sys.stdout.flush()
    search_generator = Agent.Create_Chat(search_prompt, stream=True)
    for chunk in search_generator:
        print(chunk, end="", flush=True)
        time.sleep(0.01)
    print("\n")
    print_file_contents(active_file)
    print("=" * 60)
    print("Hackathon Features Test Completed Successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

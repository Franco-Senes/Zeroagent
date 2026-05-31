import Agent
import sys
import time
import os
import glob

def clean_old_files():
    for f in glob.glob('Memory*.zr') + ['resumen.json']:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass

def main():
    print("=" * 60)
    print("Testing Cross-Chat Memory and Summarization in Zeroagent")
    print("=" * 60)
    
    # 1. Clean up
    clean_old_files()
    
    # Load settings
    Agent.LoadAll()
    Agent.Model = "gemini-2.5-flash"
    Agent.Google_Search_Tool = False
    Agent.System_Instruction = "Eres un asistente amable que recuerda datos perfectamente."
    
    # 2. First Conversation (Chat 0)
    print("\n[Step 1] Starting Chat 0...")
    Agent.New_Conversation()
    
    prompt1 = "Hola, mi color favorito es el verde esmeralda y me encantan las orquídeas salvajes."
    print(f"Prompt: '{prompt1}'")
    print("AI Response: ", end="")
    sys.stdout.flush()
    
    stream = Agent.Create_Chat(prompt=prompt1, stream=True)
    for chunk in stream:
        print(chunk, end="", flush=True)
        time.sleep(0.01)
    print("\n")
    
    # Verify resumen.json and Memory.zr are created and contain summaries
    print("\n[Step 2] Verifying generated files and summaries...")
    time.sleep(1)  # small buffer for save operation
    
    if os.path.exists("resumen.json"):
        print("-> resumen.json exists!")
    else:
        print("-> ERROR: resumen.json does not exist!")
        
    print("\n--- GetMemory('All') result: ---")
    print(Agent.GetMemory("All"))
    print("-" * 30)
    
    print("\n--- GetMemory(0) result: ---")
    print(Agent.GetMemory(0))
    print("-" * 30)
    
    # 3. Second Conversation (Chat 1) with historical context
    print("\n[Step 3] Starting Chat 1 and enabling cross-chat memory...")
    Agent.New_Conversation()
    Agent.Memory_Context_Ids = "All"  # Inject all previous summaries
    
    prompt2 = "Hola, ¿te acuerdas de qué flor y de qué color te hablé en la otra conversación?"
    print(f"Prompt: '{prompt2}'")
    print("AI Response: ", end="")
    sys.stdout.flush()
    
    stream = Agent.Create_Chat(prompt=prompt2, stream=True)
    for chunk in stream:
        print(chunk, end="", flush=True)
        time.sleep(0.01)
    print("\n")
    
    print("=" * 60)
    print("Cross-Chat Memory Test Completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()

import Agent
import sys
import time

def main():
    print("=" * 60)
    print("Testing Multimodal Image Processing in Zeroagent")
    print("=" * 60)
    
    # Load settings
    Agent.LoadAll()
    print(f"-> Model: {Agent.Model}")
    print(f"-> API Key present: {'Yes' if Agent.API_Key else 'No'}")
    
    # Set to multimodal model (2.5 flash supports multimodality)
    Agent.Model = "gemini-2.5-flash"
    Agent.System_Instruction = "Eres un asistente visual útil. Describe la imagen con precisión."
    Agent.Google_Search_Tool = False
    
    # Start conversation
    Agent.New_Conversation()
    
    # URL of Pillow Logo
    image_url = "https://www.python.org/static/community_logos/python-logo-master-v3-TM.png"
    prompt = "¿Qué palabra dice este logotipo de programación y de qué colores son sus dos serpientes?"
    
    print(f"\n[Step 1] Sending prompt with image URL: {image_url}")
    print(f"Prompt: '{prompt}'")
    print("\nAI Response (Streaming): ", end="")
    sys.stdout.flush()
    
    try:
        stream = Agent.Create_Chat(prompt=prompt, image=image_url, stream=True)
        for chunk in stream:
            print(chunk, end="", flush=True)
            time.sleep(0.01)
        print("\n")
    except Exception as e:
        print(f"\nError occurred during multimodal creation: {e}")
        
    print("=" * 60)
    print("Multimodal Test Completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()

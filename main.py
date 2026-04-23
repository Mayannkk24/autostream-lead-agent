import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from src.agent import app
    from langchain_core.messages import HumanMessage
    print("Agent modules loaded successfully.")
except Exception as e:
    print(f"IMPORT ERROR: {e}")
    sys.exit(1)

def run_agent():
    print("\n--- AutoStream Lead Agent is Starting ---")
    state = {
        "messages": [],
        "user_info": {"name": None, "email": None, "platform": None},
        "intent": ""
    }
    
    print("Agent is now live. Type 'exit' to quit.")
    
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting AutoStream Agent. Goodbye!")
            break
        
        pre_invoke_count = len(state["messages"])
        state["messages"].append(HumanMessage(content=user_input))
        
        try:
            # Invoke the graph
            output = app.invoke(state)
            
            if output and "messages" in output and len(output["messages"]) > pre_invoke_count:
                state = output
                
                # --- CONTENT EXTRACTOR START ---
                # This part cleans up the 'signature' and 'extras' mess
                raw_content = state['messages'][-1].content
                
                if isinstance(raw_content, list):
                    # Extract the text portion if the response is a list
                    clean_text = next((item['text'] for item in raw_content if 'text' in item), str(raw_content))
                else:
                    # Use as is if it's already a string
                    clean_text = raw_content
                
                print(f"Agent: {clean_text}")
                # --- CONTENT EXTRACTOR END ---
                
            else:
                print("Agent: I'm experiencing a bit of lag. Could you please repeat that?")
                
        except Exception as e:
            if "503" in str(e):
                print("Agent: (Server busy) Give me just a second to catch up...")
            elif "404" in str(e):
                print("Agent: (Model Error) Please check the model name in agent.py.")
            else:
                print(f"RUNTIME ERROR: {e}")

if __name__ == "__main__":
    print("Starting main execution...")
    run_agent()
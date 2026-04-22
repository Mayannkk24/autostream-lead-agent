import os
import sys
from dotenv import load_dotenv

print("Checking environment...")
load_dotenv()

try:
    from src.agent import app
    from langchain_core.messages import HumanMessage
    print("Agent modules loaded successfully.")
except Exception as e:
    print(f"IMPORT ERROR: {e}")
    sys.exit(1)

def run_agent():
    print("--- AutoStream Lead Agent is Starting ---")
    state = {
        "messages": [],
        "user_info": {"name": None, "email": None, "platform": None},
        "intent": ""
    }
    
    print("Agent is now live. Type 'exit' to quit.")
    
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        
        state["messages"].append(HumanMessage(content=user_input))
        
        try:
            output = app.invoke(state)
            state = output
            print(f"Agent: {state['messages'][-1].content}")
        except Exception as e:
            print(f"RUNTIME ERROR: {e}")

if __name__ == "__main__":
    print("Starting main execution...")
    run_agent()
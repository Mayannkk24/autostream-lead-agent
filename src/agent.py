from typing import Annotated, TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
import os
from dotenv import load_dotenv
from src.utils import get_knowledge_base
from src.tools import mock_lead_capture

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_info: dict
    intent: str

llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0)

def get_clean_text(message):
    content = message.content
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and 'text' in item:
                return item['text']
        return str(content)
    return str(content)

def intent_classifier(state: AgentState):
    user_msg = get_clean_text(state['messages'][-1]).lower()
    
    # 1. PRIORITY: If we are already asking for lead info, STAY in lead_capture
    if len(state['messages']) > 1:
        last_ai = get_clean_text(state['messages'][-2]).lower()
        if any(x in last_ai for x in ["name?", "email address?", "platform?"]):
            return {"intent": "high_intent"}

    # 2. RAG TRIGGER: If they ask about services/pricing
    if any(x in user_msg for x in ["interested", "service", "pricing", "cost", "plan"]):
        return {"intent": "inquiry"}
    
    # 3. SIGNUP TRIGGER: If they confirm they want to join
    if any(x in user_msg for x in ["yes", "sign up", "join", "start"]):
        return {"intent": "high_intent"}
    
    return {"intent": "greeting"}

def greeting_node(state: AgentState):
    return {"messages": [AIMessage(content="Hello! I'm the AutoStream Assistant. How can I help you today?")]}

def rag_node(state: AgentState):
    kb = get_knowledge_base()
    user_msg = get_clean_text(state['messages'][-1])
    # Force the agent to show plans and then ASK to sign up
    prompt = f"Data: {kb}\n\nQuestion: {user_msg}\n\nAnswer based on data and end with: 'Would you like to sign up for one of these plans?'"
    return {"messages": [llm.invoke(prompt)]}

def lead_capture_node(state: AgentState):
    info = state.get("user_info") or {"name": None, "email": None, "platform": None}
    user_msg = get_clean_text(state['messages'][-1])
    
    last_ai = get_clean_text(state['messages'][-2]).lower() if len(state['messages']) > 1 else ""

    # Slot Filling
    if "your name?" in last_ai and not info["name"]:
        info["name"] = user_msg
    elif "email address?" in last_ai and not info["email"]:
        info["email"] = user_msg
    elif "platform?" in last_ai and not info["platform"]:
        info["platform"] = user_msg

    # Platform detection from history
    history = " ".join([get_clean_text(m).lower() for m in state['messages']])
    if not info["platform"]:
        if "youtube" in history: info["platform"] = "YouTube"
        elif "instagram" in history: info["platform"] = "Instagram"

    # Step-by-Step flow
    if not info["name"]:
        return {"messages": [AIMessage(content="I'd love to help with that! First, what is your name?")], "user_info": info}
    
    if not info["email"]:
        return {"messages": [AIMessage(content=f"Thanks {info['name']}, what is your email address?")], "user_info": info}
    
    if not info["platform"]:
        return {"messages": [AIMessage(content="And which platform do you use (YouTube or Instagram)?")], "user_info": info}

    # FINISH: Call tool and end conversation clearly
    mock_lead_capture(info["name"], info["email"], info["platform"])
    return {
        "messages": [AIMessage(content=f"Excellent! I've captured your details for {info['platform']}. Our team will contact you soon. Have a great day! [CONVERSATION COMPLETED]")], 
        "user_info": info
    }

# --- Graph ---
builder = StateGraph(AgentState)
builder.add_node("classifier", intent_classifier)
builder.add_node("greeting", greeting_node)
builder.add_node("rag", rag_node)
builder.add_node("lead_capture", lead_capture_node)
builder.set_entry_point("classifier")

def route(state):
    intent = state.get("intent", "greeting")
    if "inquiry" in intent: return "rag"
    if "high_intent" in intent: return "lead_capture"
    return "greeting"

builder.add_conditional_edges("classifier", route)
builder.add_edge("greeting", END)
builder.add_edge("rag", END)
builder.add_edge("lead_capture", END)
app = builder.compile()
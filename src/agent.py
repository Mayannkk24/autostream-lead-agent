from typing import Annotated, TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
import os
from dotenv import load_dotenv
from src.utils import get_knowledge_base
from src.tools import mock_lead_capture

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_info: dict  # Tracks name, email, platform across turns
    intent: str

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0
)

def intent_classifier(state: AgentState):
    user_msg = state['messages'][-1].content
    prompt = f"""Classify user intent into: 'greeting', 'inquiry', or 'high_intent'.
    User message: {user_msg}
    Return ONLY the category name."""
    response = llm.invoke(prompt)
    return {"intent": response.content.strip().lower()}

def rag_node(state: AgentState):
    kb = get_knowledge_base()
    user_msg = state['messages'][-1].content
    prompt = f"Use this data: {kb}. Answer accurately: {user_msg}"
    return {"messages": [llm.invoke(prompt)]}

def lead_capture_node(state: AgentState):
    info = state.get("user_info", {"name": None, "email": None, "platform": None})
    user_msg = state['messages'][-1].content.strip()

    # Simple logic to fill missing slots based on conversation flow
    if state['messages'][-2].content.find("name") != -1 and not info["name"]:
        info["name"] = user_msg
    elif state['messages'][-2].content.find("email") != -1 and not info["email"]:
        info["email"] = user_msg
    elif state['messages'][-2].content.find("platform") != -1 and not info["platform"]:
        info["platform"] = user_msg

    # Check for missing info and ask
    if not info["name"]:
        return {"messages": ["I'd love to help! What is your name?"], "user_info": info}
    if not info["email"]:
        return {"messages": [f"Thanks {info['name']}, what's your email?"], "user_info": info}
    if not info["platform"]:
        return {"messages": ["Which platform do you use (YouTube, Instagram)??"], "user_info": info}

    # Requirement 3.3: Call tool ONLY when all details are collected
    mock_lead_capture(info["name"], info["email"], info["platform"])
    return {"messages": ["Details captured! We'll be in touch."], "user_info": info}

# Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("classifier", intent_classifier)
workflow.add_node("rag", rag_node)
workflow.add_node("lead_capture", lead_capture_node)
workflow.set_entry_point("classifier")

def route_intent(state):
    if "inquiry" in state["intent"]: return "rag"
    if "high_intent" in state["intent"]: return "lead_capture"
    return END

workflow.add_conditional_edges("classifier", route_intent)
workflow.add_edge("rag", END)
workflow.add_edge("lead_capture", END)
app = workflow.compile()
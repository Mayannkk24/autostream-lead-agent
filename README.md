# 🚀 AutoStream: Intelligent Lead Gen Agent

**AutoStream** is a stateful, RAG-powered conversational AI agent designed to transform social media inquiries into qualified leads. Built with **LangGraph** and **Gemini**, it handles complex intent switching and maintains multi-turn memory to provide a seamless user experience.

---

## 📺 Project Demo
**[Watch the Full Workflow Demonstration](https://drive.google.com/file/d/19ngasCpT1FXCQA3_BhJiJIrsYeL-d9kc/view?usp=sharing)**
*(Greeting ➡️ Pricing RAG ➡️ Intent Shift ➡️ Lead Qualification ➡️ Tool Execution)*

---

## 🛠️ Tech Stack
* **Brain:** Google Gemini (via LangChain)
* **Orchestration:** LangGraph (Stateful Graph Workflows)
* **Knowledge Base:** Local RAG (JSON-based)
* **Environment:** Python 3.10+, Dotenv

---

## 🧠 Architecture & Design Choices
I chose **LangGraph** over simple linear chains to ensure the agent behaves like a true state machine.

### Key Design Pillars:
* **Stateful Intelligence:** Unlike standard LLM calls, this agent maintains a `TypedDict` state. It tracks conversation history and monitors a `user_info` object (Name, Email, Platform) to ensure no redundant questions are asked.
* **Hardened Intent Routing:** I implemented a **"Memory Lock"** logic in the Classifier Node. This ensures that if the agent asks for an email, the next response is strictly treated as a lead response, preventing the conversation from resetting even if the LLM detects a "Greeting" keyword.
* **Contextual Acknowledgment:** The agent acknowledges specific user details (like their chosen platform) during the transition from inquiry to lead capture, creating a human-like flow rather than a robotic form-filling experience.
* **Guaranteed Tool Execution:** The `mock_lead_capture` tool is strictly gated. It only executes once the state validates that all three mandatory fields (Name, Email, Platform) are present and verified.

---

## 🚀 Local Installation & Setup

Follow these steps to run the agent on your local machine:

### 1. Clone the Repository
```bash
git clone (https://github.com/Mayannkk24/autostream-agent.git)
cd autostream-agent
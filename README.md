🚀 AutoStream: Intelligent Lead Gen Agent
AutoStream is a stateful, RAG-powered conversational AI agent designed to transform social media inquiries into qualified leads. Built with LangGraph and Gemini 1.5 Flash, it handles complex intent switching and maintains multi-turn memory to provide a seamless user experience.

🛠️ Tech Stack
Brain: Google Gemini 1.5 Flash (via LangChain)

Orchestration: LangGraph (Stateful Graph Workflows)

Knowledge Base: Local RAG (JSON-based)

Environment: Python 3.9+, Dotenv

🧠 Architecture & Design Choices
I chose LangGraph over simple linear chains to ensure the agent behaves like a true state machine.

Key Design Pillars:
Stateful Intelligence: Unlike standard LLM calls, this agent maintains a TypedDict state. It tracks conversation history and specifically monitors a user_info object (Name, Email, Platform) to ensure no redundant questions are asked.

Intent-Driven Routing: Every message first hits a Classifier Node. This ensures that "Greetings," "Pricing Inquiries," and "Sign-up Requests" are handled by specialized logic paths, preventing "hallucinations" or irrelevant responses.

Conditional RAG: The agent only accesses the Knowledge Base when an "Inquiry" intent is detected, optimizing token usage and speed.

Guaranteed Tool Execution: The mock_lead_capture tool is strictly gated. It only executes once the state recognizes that all three mandatory fields (Name, Email, Platform) are present.



📱 WhatsApp Deployment Strategy
To move this project from a CLI to a production WhatsApp environment, I would follow this roadmap:

Provider: Integrate the Meta WhatsApp Business API via Twilio or a direct Meta Developer account.

API Gateway: Develop a FastAPI or Flask server to act as a Webhook.

Webhook Logic: * When a user messages on WhatsApp, the Webhook receives a JSON payload.

The server retrieves the existing state for that specific phone number (using a database like Redis or MongoDB).

The message is passed to app.invoke(state).

The resulting response is sent back via a POST request to the WhatsApp API.

Scaling: Deploy the containerized (Docker) application to AWS/GCP with an HTTPS endpoint for secure communication.
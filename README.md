# 🌍 AI-Powered Multilingual Travel Assistant

An advanced, conversational AI travel planner built with **CrewAI**, **Streamlit**, and **ChromaDB**. This application uses autonomous AI agents to research and generate personalized travel itineraries. It features a conversational interface with long-term vector memory and a multilingual Text-to-Speech (TTS) engine.

## 🚀 Features
- **Multi-Agent Orchestration (CrewAI):** Uses specialized agents (Local Guide, Travel Planner, Logistics Expert) to collaborate and plan perfect trips.
- **Conversational Memory (ChromaDB):** Vector database integration that remembers your generated trips so you can ask follow-up questions contextually.
- **Multilingual Voice Output (gTTS):** The AI natively generates text and speaks its responses aloud in English, Hindi, and Marathi.
- **Advanced Observability (LangSmith & OpenTelemetry):** Tracks AI thought processes, token usage, and latency in real-time.
- **Dynamic Web UI:** Interactive, chat-based user interface powered by Streamlit.

## 🛠️ Tech Stack
- **Frameworks:** Streamlit, CrewAI
- **LLM / APIs:** OpenRouter (gpt-4o-mini), SerperDevTool (Live Web Search)
- **Database:** ChromaDB (Vector Database)
- **Audio:** gTTS (Google Text-to-Speech)
- **Observability:** LangSmith, OpenTelemetry

## 📦 Installation & Setup

1. **Navigate to the project directory:**
   ```bash
   cd streamlit_trip_advisor_app

2. Install the required dependencies:
bash
pip install streamlit crewai crewai_tools langchain chromadb gtts opentelemetry-api opentelemetry-sdk openinference-instrumentation-crewai openinference-instrumentation-openai

3.Set up your API Keys: The application requires API keys for OpenRouter, Serper, and LangSmith. These are currently configured at the top of the my_app_2.py file.
Run the Streamlit App:
bash
streamlit run my_app_2.py

💡 How to Use
Expand the Generate New Travel Plan section. Enter your origin city, destination, travel dates, and interests.
Select your preferred Voice Language (English, Hindi, or Marathi) from the sidebar.
Click Generate Travel Plan. Wait for the multi-agent system to collaborate and build your itinerary.
Scroll down to the Conversational Chat interface to ask follow-up questions (e.g., "Can you find cheaper hotels?"). The AI will read the context from ChromaDB, reply in your chosen language, and speak the answer out loud!

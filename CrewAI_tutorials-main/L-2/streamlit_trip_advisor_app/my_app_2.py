import os
import streamlit as st
import chromadb
from gtts import gTTS
import uuid

# Configure LangSmith Tracing and API Keys globally
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = "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"
os.environ["LANGSMITH_PROJECT"] = "project"
os.environ["LANGCHAIN_PROJECT"] = "project"
os.environ["OPENROUTER_API_KEY"] = "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"

# OpenTelemetry and OpenInference Setup
from langsmith.integrations.otel import OtelSpanProcessor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from openinference.instrumentation.crewai import CrewAIInstrumentor
from openinference.instrumentation.openai import OpenAIInstrumentor

# Configure OpenTelemetry
tracer_provider = trace.get_tracer_provider()
if not isinstance(tracer_provider, TracerProvider):
    tracer_provider = TracerProvider()
    trace.set_tracer_provider(tracer_provider)

tracer_provider.add_span_processor(OtelSpanProcessor())
CrewAIInstrumentor().instrument()
OpenAIInstrumentor().instrument()

from TravelAgents import guide_expert, location_expert, planner_expert
from TravelTasks import location_task, guide_task, planner_task
from crewai import Crew, Process, Task

# Initialize ChromaDB Client with the provided API key
try:
    chroma_client = chromadb.HttpClient(
        headers={"x-chroma-token": "ck-2uMhVeFmPxsAoCYdLgTs1XMFnPffRAtfE2CyNZftYKrK"}
    )
    collection = chroma_client.get_or_create_collection(name="travel_conversations")
except Exception as e:
    # Fallback to local persistent DB if host URL is needed and not provided
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(name="travel_conversations")

# Streamlit App Title
st.set_page_config(page_title="Conversational AI Trip Planner", layout="wide")
st.title("🌍 AI-Powered Trip Planner with Voice & Memory")

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_plan" not in st.session_state:
    st.session_state.current_plan = ""

st.markdown("💡 **Plan your next trip, chat conversationally, and listen to the AI speak in Marathi, Hindi, or English!**")

# Settings Sidebar
with st.sidebar:
    st.header("⚙️ Voice Settings")
    tts_lang = st.selectbox("AI Voice Language", ["English", "Hindi", "Marathi"])
    lang_map = {"English": "en", "Hindi": "hi", "Marathi": "mr"}
    lang_code = lang_map[tts_lang]

# Step 1: Form Inputs
with st.expander("📝 1. Generate New Travel Plan", expanded=True):
    from_city = st.text_input("🏡 From City", "India")
    destination_city = st.text_input("✈️ Destination City", "Rome")
    date_from = st.date_input("📅 Departure Date")
    date_to = st.date_input("📅 Return Date")
    interests = st.text_area("🎯 Your Interests", "sightseeing and good food")

    if st.button("🚀 Generate Travel Plan"):
        if not from_city or not destination_city or not date_from or not date_to or not interests:
            st.error("⚠️ Please fill in all fields.")
        else:
            with st.spinner("⏳ AI is preparing your personalized travel itinerary..."):
                loc_task = location_task(location_expert, from_city, destination_city, date_from, date_to)
                guid_task = guide_task(guide_expert, destination_city, interests, date_from, date_to)
                plan_task = planner_task([loc_task, guid_task], planner_expert, destination_city, interests, date_from, date_to)

                crew = Crew(
                    agents=[location_expert, guide_expert, planner_expert],
                    tasks=[loc_task, guid_task, plan_task],
                    process=Process.sequential,
                    verbose=True,
                )
                
                result = crew.kickoff()
                travel_plan_text = str(result)
                st.session_state.current_plan = travel_plan_text

                # Save to memory
                collection.add(
                    documents=[travel_plan_text],
                    metadatas=[{"destination": destination_city, "type": "plan"}],
                    ids=[str(uuid.uuid4())]
                )

# Display Current Plan & Audio
if st.session_state.current_plan:
    st.subheader("✅ Your Travel Plan")
    st.markdown(st.session_state.current_plan)
    
    # Generate TTS Audio
    try:
        tts = gTTS(text="Here is your travel plan summary. " + st.session_state.current_plan[:500], lang=lang_code)
        tts.save("plan_audio.mp3")
        st.audio("plan_audio.mp3", format="audio/mp3")
    except Exception as e:
        st.warning("Could not generate audio for this text.")

# Step 2: Conversational Chat Interface
st.markdown("---")
st.subheader("💬 Chat with your Travel Assistant")
st.caption("Ask anything about your trip, recommendations, or modify your itinerary! The AI remembers your past plans using ChromaDB.")

# Display Chat History
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input("Ask a question about your trip..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Search ChromaDB Memory
            memory_results = collection.query(query_texts=[prompt], n_results=2)
            context = str(memory_results.get("documents", [""]))

            # Create a simple chat task for the guide expert using memory
            chat_task = Task(
                description=f"Answer the user's question conversationally IN {tts_lang}. Use this past memory if relevant: {context}. Question: {prompt}",
                expected_output=f"A conversational, helpful answer to the user's travel question, WRITTEN ENTIRELY IN {tts_lang} (do not use English unless the selected language is English).",
                agent=guide_expert
            )
            chat_crew = Crew(agents=[guide_expert], tasks=[chat_task], verbose=False)
            chat_response = str(chat_crew.kickoff())
            
            st.markdown(chat_response)
            st.session_state.chat_history.append({"role": "assistant", "content": chat_response})
            
            # Voice Response
            try:
                tts = gTTS(text=chat_response, lang=lang_code)
                tts.save("chat_audio.mp3")
                st.audio("chat_audio.mp3", format="audio/mp3", autoplay=True)
            except Exception as e:
                pass

import streamlit as st
import httpx
import os

st.title("Tech RAG Assistant")

backend_url = os.getenv("BACKEND_URL", "http://backend:8000")

st.write(f"Connecting to backend at: {backend_url}")

if st.button("Check Health"):
    try:
        response = httpx.get(f"{backend_url}/health")
        st.write(response.json())
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")

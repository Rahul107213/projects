# AI Document Assistant

A full-stack, AI-powered document assistant built with FastAPI, Streamlit, LangChain, and Google Gemini. 

Upload multiple PDFs (e.g. your resume and a job description), and ask the AI to summarize, find similarities, match skills, or extract specific data across all documents simultaneously using real-time streaming!

## Features
- **Multi-Document Upload:** Analyze and compare multiple PDFs at once.
- **Real-Time Streaming:** The AI types out answers character-by-character for a zero-latency feel.
- **Auto-Healing Fallbacks:** Automatically catches Google API Token/Quota limits and seamlessly falls back to backup models.
- **Glassmorphism UI:** A beautiful, dark-themed modern interface.

## Local Setup

Make sure you have Docker installed.

1. Clone the repository.
2. Create a `.env` file in the root directory and add your API key:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```
3. Run Docker Compose:
   ```bash
   docker-compose up --build
   ```
4. Open your browser to `http://localhost:8501`.

## Deployment (Railway)
This project is pre-configured to be deployed as two separate services (Frontend and Backend) on Railway. 

*See deployment instructions in the guide provided by Antigravity.*

# FinSight

A web-based AI chatbot and forecasting tool to help users make sound investing decisions in the financial markets.

---

## Features

### Frontend

- **Single-page Application:** Clean layout with a stock chart and chatbot side by side.
- **Interactive Chart:** Visualize historical stock prices and forecasting model predictions.
- **AI Chatbot:** Ask for stock predictions, investing advice, or general financial queries.

### Backend & Machine Learning

- **Forecasting Models:** Trained and tuned models for stock price prediction.
- **Intelligent Chatbot:**
  - Provides investing advice.
  - Can perform web searches (e.g., on Investopedia) to enhance responses.
  - Integrates with external APIs for up-to-date financial data.
- **Session Management:** Each user has a unique chat history, managed via session or authentication.

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js & npm
- Redis (for chat history and vector storage)
- Docker

### Setup

#### Backend

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure environment variables:**  
   Create a `.env` file with your API keys and settings (see `.env.sample` for required fields).
3. **Start Redis:**  
   You can use Docker:
   ```bash
   docker run -d -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
   ```
4. **Run FastAPI backend:**
   ```bash
   uvicorn app.backend.main:app --reload
   ```

#### Frontend

1. **Install dependencies:**
   ```bash
   cd app/frontend
   npm install
   ```
2. **Run the frontend:**
   ```bash
   npm run dev
   ```
3. **Open your browser:**  
   Visit [http://localhost:5173](http://localhost:5173)

---

## Tech Stack

**Frontend:**

- [React](https://react.dev/) (in TypeScript) for the frontend
- [Bootstrap 5](https://getbootstrap.com/) & [Bootstrap Icons](https://icons.getbootstrap.com/) for UI
- [Chart.js](https://www.chartjs.org/) via [react-chartjs-2](https://github.com/reactchartjs/react-chartjs-2) for interactive charts

**Backend:**

- [FastAPI](https://fastapi.tiangolo.com/) (Python) for API and server logic
- [Redis Stack](https://redis.io/docs/stack/) for chat history and vector storage
- [Uvicorn](https://www.uvicorn.org/) as the ASGI server

**Machine Learning & NLP:**

- [HuggingFace Transformers](https://huggingface.co/docs/transformers/index) for generating embeddings for the vector store
- [LangChain](https://www.langchain.com/) for creating the agentic workflow that powers the AI chatbot
- [Darts](https://unit8co.github.io/darts/) to train, evaluate and fine-tune time series forecasting models

**Other:**

- [Docker](https://www.docker.com/) (optional, for running Redis Stack)

---

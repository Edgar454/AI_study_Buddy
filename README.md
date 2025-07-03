
# AI Study Buddy

**AI Study Buddy** is an AI-powered companion designed to help you understand and retain content from your study materials (PDFs). It uses an **agentic workflow** (via [CrewAI](https://docs.crewai.com)) to explain documents, generate quizzes, export flashcards, and provide smart summaries.

---

## 🧠 Features

- 📝 In-depth **explanations** of PDFs using researched and structured plans.
- 📊 **Evaluations**: Generate multiple-choice questions from study material.
- 🃏 **Flashcards**: Exportable to Anki to reinforce your learning.
- 🧾 **Summaries**: Get the gist of your material quickly.
- 📦 Fully containerized with **Docker** for portability.
- 📈 **Monitoring** with Prometheus + Grafana.

---

## 📐 Architecture

![Architecture Diagram Placeholder](./assets/architecture.png)

**Main Components:**

- **Frontend**: Vite (React.js)
- **Backend**: FastAPI
- **Queue & Cache**: Celery + Redis
- **Agents** (via CrewAI): Explanation, Evaluation, Flashcard, Summary, Ingestion
- **Monitoring**: Prometheus & Grafana

**Data Flow:**

1. Frontend sends a request to FastAPI.
2. FastAPI sends task to Celery.
3. Redis checks for cache. If found, return result.
4. If not cached, task is processed with CrewAI using OpenAI + Serper.
5. Once ready, Celery notifies FastAPI.
6. Frontend polls for result using file hash.
7. FastAPI returns cached result to frontend.

---

## 🤖 Agent Workflow

![Agent Workflow Placeholder](./assets/agents_summary.png)

1. **Ingestion Agent**: Reads PDF and enriches it with internet research via Serper. Produces an outline.
2. **Explanation Agent**: Generates the full explanation based on the outline.
3. **Evaluation Agent**: Builds multiple-choice questions (QCMs).
4. **Flashcard Agent**: Creates flashcards from the explanation.
5. **Summary Agent**: Produces a concise summary.

---

## 💾 Storage System

![Storage System Placeholder](./assets/study_buddy_db_wb.drawio.png)

- **Redis**: Used as both a task queue and result cache.
- **PostgreSQL**: Persistent storage of:
  - User credentials
  - Processed files metadata
  - Token usage logs

Upon app shutdown, recent results are saved from Redis into PostgreSQL.

---

## 📊 Monitoring

![Monitoring System Placeholder](./images/monitoring.png)

Metrics collected via **Prometheus**:
- Request counts (success/failures)
- Token usage
- Response time
- Connection issues

**Grafana** dashboards allow live monitoring of usage, cost, and health.

---

## ⚙️ Installation

Although you can run this project manually, **Docker Compose** is the recommended way.

### 1. `.env` Configuration

Create a `.env` file in the root directory with the following keys:

```
AGENTOPS_API_KEY=your_agentops_key
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
DATABASE_URL=postgresql://postgres:eded404@postgres:5432/postgres
SERPER_API_KEY=your_serper_key
OPENAI_API_KEY=your_openai_key
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MAIN_MODEL_NAME=openai/gpt-4
OPENAI_EXPLANATION_MODEL=openai/gpt-3.5-turbo
CELERY_SERVICE_ACCESS_PASSWORD=your_custom_password
POSTGRES_USER=postgres
POSTGRES_PASSWORD=eded404
POSTGRES_DB=postgres
```

> 🔐 Get your free keys at:
> - [AgentOps](https://www.agentops.ai/)
> - [Serper.dev](https://serper.dev/)

### 2. Start the app

```bash
docker compose up -d
```

Then open:
- Frontend: http://localhost:3001
- Monitoring: http://localhost:3000

---

## 🎬 Demo

https://github.com/user-attachments/assets/4f99a4f6-9b09-4290-93cd-061d65d69dd5

---

## 📎 License

MIT

---

## 📞 Contact

Created by **Edgar Peggy MEVA’A** – for questions, suggestions or collaborations, feel free to reach out!

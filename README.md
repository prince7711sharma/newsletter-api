# 📚 R.S Education — Newsletter Service

> AI-powered weekly newsletter backend for the Student Counselling platform.
> Automatically sends personalized college, scholarship, and career content to subscribed users every Sunday.

---

## 📁 Folder Structure

```
newsletter_service/
├── main.py             # FastAPI app entry point
├── api.py              # API endpoints (health, unsubscribe, send-test, trigger-now)
├── service.py          # Core business logic (pipeline orchestration)
├── scheduler.py        # APScheduler weekly cron job
├── database.py         # MongoDB connection & queries
├── ai_generator.py     # Groq AI newsletter content generation
├── email_builder.py    # HTML email template builder
├── email_sender.py     # Resend email delivery + retry logic
├── config.py           # Centralized settings (pydantic-settings)
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .env                # Your local secrets (never commit this!)
└── newsletter_service.log  # Auto-generated log file
```

---

## ⚙️ Prerequisites

- Python 3.11+
- MongoDB (local or Atlas)
- [Groq API key](https://console.groq.com) — free tier available
- [Resend API key](https://resend.com) — free tier: 3,000 emails/month
- A verified sender domain in Resend

---

## 🚀 Setup Instructions

### 1. Clone / Navigate to project

```bash
cd newsletter_service
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your real credentials:

| Variable | Description |
|---|---|
| `MONGODB_URI` | Your MongoDB connection string |
| `GROQ_API_KEY` | From console.groq.com |
| `GROQ_MODEL` | `llama3-8b-8192` (fast & cheap) |
| `RESEND_API_KEY` | From resend.com dashboard |
| `EMAIL_FROM` | Must match verified Resend sender domain |
| `BASE_URL` | Your public URL (for CTA & unsubscribe links) |

### 5. Run the service

```bash
python main.py
```

The service starts at `http://localhost:8000` and the scheduler activates automatically.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Service info |
| `GET` | `/health` | DB + scheduler status |
| `GET` | `/unsubscribe?email=...` | Unsubscribe a user (HTML page) |
| `POST` | `/send-test` | Send test newsletter |
| `POST` | `/trigger-now` | Manually run the full pipeline |
| `GET` | `/docs` | Swagger UI |

### Example: Send Test Newsletter

```bash
curl -X POST http://localhost:8000/send-test \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "name": "Priya",
    "interests": ["Medicine", "Biology"],
    "marks": 88,
    "budget": 150000,
    "location": "Mumbai"
  }'
```

### Example: Manually trigger pipeline

```bash
curl -X POST http://localhost:8000/trigger-now
```

---

## 📅 Scheduler

The scheduler runs automatically every **Sunday at 9:00 AM IST**.

To change the schedule, edit `.env`:

```env
SCHEDULER_DAY_OF_WEEK=sun   # mon, tue, wed, thu, fri, sat, sun
SCHEDULER_HOUR=9            # 0–23
SCHEDULER_MINUTE=0          # 0–59
```

Check next scheduled run:

```bash
curl http://localhost:8000/health
```

---

## 🗄️ MongoDB Schema

Your `users` collection documents should look like:

```json
{
  "name": "Priya Sharma",
  "email": "priya@example.com",
  "interests": ["Computer Science", "AI"],
  "marks": 88,
  "budget": 200000,
  "location": "Delhi",
  "newsletter": true,
  "last_sent": null
}
```

The service **only reads** `newsletter: true` users. It **writes** only `last_sent` (timestamp) on success.

---

## 🛡️ Rate Limits

| Endpoint | Limit |
|---|---|
| `GET /health` | 10 req/min per IP |
| `GET /unsubscribe` | 20 req/min per IP |
| `POST /send-test` | 5 req/min per IP |
| `POST /trigger-now` | 2 req/min per IP |

---

## 📊 Duplicate Prevention

The `last_sent` field is updated after every successful email. If `last_sent` is within the past **7 days**, the user is skipped in the next run. This prevents duplicate newsletters even if the job runs multiple times.

---

## 📝 Logs

Logs are written to both the console and `newsletter_service.log`:

```
2025-01-05 09:00:00 | INFO     | scheduler | ⏰ Scheduler triggered: Running weekly newsletter pipeline...
2025-01-05 09:00:01 | INFO     | database  | 📋 Found 42 subscribed users.
2025-01-05 09:00:01 | INFO     | service   | 📬 42 users to process (0 skipped).
2025-01-05 09:00:03 | INFO     | email_sender | ✅ Email sent to priya@example.com | ID: abc123
2025-01-05 09:00:45 | INFO     | service   | ✅ Pipeline complete. Sent: 42 | Skipped: 0 | Failed: 0
```

---

## 🐳 Production Deployment (Optional)

For production, use a process manager like **systemd** or **Docker**:

```bash
# Using gunicorn
gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Or with Docker:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

---

## 💡 Tips

- Use **MongoDB Atlas** free tier for cloud hosting
- Use **Groq's `llama3-8b-8192`** — it's fast, cheap, and great for short content
- Set `EMAIL_BATCH_SIZE=5` and `EMAIL_BATCH_DELAY=2.0` on free Resend tier to avoid rate limits
- Test with `/send-test` before enabling the scheduler in production

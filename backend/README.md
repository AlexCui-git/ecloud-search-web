# ECloud Search API

## Project Structure
```
ecloud_web/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints.py
│   │   ├── core/
│   │   │   ├── models.py
│   │   │   └── scraper/
│   │   │       └── search_automation.py
│   │   └── main.py
│   ├── requirements.txt
│   └── README.md
└── frontend/
    ├── src/
    │   ├── components/
    │   │   └── Search.vue
    │   ├── App.vue
    │   └── main.js
    ├── package.json
    └── index.html
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
python -m playwright install chromium
```

3. Create logs directory:
```bash
mkdir -p logs
```

4. Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

## API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
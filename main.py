import os
from typing import List, Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Magneto AI Jobs Clone")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Basic health/root ---
@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

# --- Database test helper ---
@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# --- Jobs search endpoint ---
SAMPLE_JOBS = [
    {
        "title": "Desarrollador Frontend React",
        "company": "TechNova",
        "location": "Remoto - LATAM",
        "salary": "USD 2.5k - 4k",
        "description": "Construye interfaces modernas con React, Tailwind y Vite.",
        "url": "https://example.com/jobs/frontend-react"
    },
    {
        "title": "Analista de Datos",
        "company": "DataFlow",
        "location": "Bogotá, Colombia (Híbrido)",
        "salary": "COP 8M - 12M",
        "description": "Modelado, dashboards y storytelling con datos.",
        "url": "https://example.com/jobs/data-analyst"
    },
    {
        "title": "Diseñador UI/UX Senior",
        "company": "Magneto Labs",
        "location": "Medellín, Colombia (Remoto)",
        "salary": "A convenir",
        "description": "Crea experiencias limpias y accesibles para productos digitales.",
        "url": "https://example.com/jobs/uiux-senior"
    },
    {
        "title": "Backend Engineer Python",
        "company": "CloudWare",
        "location": "Remoto",
        "salary": "USD 3k - 5k",
        "description": "APIs con FastAPI, MongoDB y arquitectura escalable.",
        "url": "https://example.com/jobs/backend-python"
    },
]

@app.get("/jobs/search")
def search_jobs(q: Optional[str] = Query(None, description="Query de búsqueda por rol, stack o empresa")):
    """Simple search over a sample dataset to emulate listings."""
    if not q:
        return {"jobs": SAMPLE_JOBS}
    q_lower = q.lower()
    filtered = [
        j for j in SAMPLE_JOBS
        if q_lower in j["title"].lower()
        or q_lower in (j.get("company") or "").lower()
        or q_lower in (j.get("description") or "").lower()
        or q_lower in (j.get("location") or "").lower()
    ]
    return {"jobs": filtered}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

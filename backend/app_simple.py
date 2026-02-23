"""
DepoSafety API - Simplified for Deployment
Bug-free, minimal version for Render.com
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="DepoSafety API", version="1.0.0")

# CORS - allow all origins for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "DepoSafety API", "version": "1.0.0", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/api/v1/properties")
def get_properties():
    """Get all properties - demo data"""
    return {
        "properties": [
            {
                "id": "demo-1",
                "address": "123 Main St",
                "city": "New York",
                "state": "NY",
                "status": "active"
            }
        ]
    }

@app.post("/api/v1/auth/register")
def register():
    """User registration - demo"""
    return {"message": "Registration endpoint", "token": "demo-token"}

@app.post("/api/v1/auth/login")
def login():
    """User login - demo"""
    return {"message": "Login endpoint", "token": "demo-token"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

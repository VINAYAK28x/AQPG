"""
Main entrypoint for the Question Paper Generation System backend.

Run with:
    cd backend
    uvicorn main:app --reload --port 8000

Or:
    cd backend
    python main.py
"""

from app.factory import create_app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

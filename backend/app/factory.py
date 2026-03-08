"""
FastAPI Application Factory.

Creates and configures the FastAPI app instance with
all middleware and routers registered.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import CORS_ORIGINS
from app.api import syllabus, textbook, mapping, questions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI app instance with all routers registered.
    """
    app = FastAPI(
        title="Question Paper Generation System",
        description=(
            "An intelligent NLP-based platform for automated "
            "question paper generation using SBERT, Flan-T5, "
            "and Bloom's taxonomy classification."
        ),
        version="1.0.0",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API routers
    app.include_router(syllabus.router)
    app.include_router(textbook.router)
    app.include_router(mapping.router)
    app.include_router(questions.router)

    # Health check route
    @app.get("/")
    def root():
        return {"status": "Backend running successfully"}

    return app

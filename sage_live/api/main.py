"""
sage_live.api.main
~~~~~~~~~~~~~~~~~~~

Main application entry point for SAGE-Live API.

Run with:
    uvicorn sage_live.api.main:app --host 0.0.0.0 --port 8000 --reload

Production:
    gunicorn sage_live.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
"""

from sage_live.api.routes import create_app

app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "sage_live.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

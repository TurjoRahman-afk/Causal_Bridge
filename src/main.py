# control center of the project 
#when i run the command uvicorn src.main:app --reload , it starts this file and makes the entire API available 

from fastapi import FastAPI # web framework for building APIs
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .api.routes import router
from .api.visualization_routes import router as viz_router
from .api.upload_routes import router as upload_router
from .core.config import settings
import os

app = FastAPI(     # this app object is what uvicorn runs to start the API server 
    title="CausalBridge API",
    description="Natural language interface for causal inference analysis with advanced methods",
    version="2.0.0"
)

# CORS middleware, this allows the browser to access the API from different origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # allow requests from any domain
    allow_credentials=True, # allow cookies 
    allow_methods=["*"], # allow all HTTP methods
    allow_headers=["*"], # allow all headers
)

"""connects route modules to the main app,
so that the endpoints defined in those modules become part of the overall API.
>>>>>> IT keeps code organized -- each router file handles its own responsibility."""
app.include_router(router, prefix="/api/v1", tags=["Analysis"])
app.include_router(viz_router, prefix="/api/v1", tags=["Visualization"])
app.include_router(upload_router, prefix="/api/v1", tags=["Upload"])


"""enables URLs  to work 
like /static/filename.ext to serve files from the static directory."""
# Serve static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
"when someone access the root URL, run this function"
"""1.Browser requests 
   2. FastAPI calls 
   3. Function sends dashboard.html file 
   4. Browser displays the HTML page"""
@app.get("/")
def read_root():
    """Redirect to dashboard"""
    return FileResponse(os.path.join(static_dir, "dashboard.html")) # connect the web page here 




"""Shows what the API can do 
New users can see available features,
points to docs and dashboard """
@app.get("/api")
def api_info():
    return {
        "message": "Welcome to CausalBridge API",
        "version": "2.0.0",
        "docs": "/docs",
        "dashboard": "/",
        "features": [
            "Natural language question parsing with Google Gemini AI",
            "Multiple causal methods (Backdoor, PSM, DiD, IV)",
            "Data quality checks",
            "Visualization support",
            "Bootstrap confidence intervals",
            "Web Dashboard"
        ]
    }
    
# to check if the API key is loaded correctly or not 
#Security: shows the key exists but not the actual value 
@app.get("/debug-config")
def debug_config():
    """Debug endpoint to check configuration"""
    return {
        "llm_provider": settings.llm_provider, # shows which AI model is being used 
        "gemini_api_key_configured": bool(settings.gemini_api_key), #shows if API key exists
        "gemini_api_key_length": len(settings.gemini_api_key) if settings.gemini_api_key else 0, # length of the key , if no key returns 0.
        "app_name": settings.app_name # shows app name "CausalBridge"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "CausalBridge"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
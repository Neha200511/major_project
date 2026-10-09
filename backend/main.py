from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config.settings import settings
from backend.database.mongodb import create_indexes
from backend.auth.routes import router as auth_router
from backend.users.routes import router as users_router
from backend.conversations.routes import router as conversations_router
from backend.alerts.routes import router as alerts_router
from backend.chat.websocket import websocket_endpoint
from backend.alerts.websocket import alerts_websocket_endpoint

app = FastAPI(
    title='Child-Safe Digital Environment Manager',
    description='Privacy-first intelligent protection for safer digital conversations',
    version='1.0.0'
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        'http://localhost:5173',
        'http://localhost:3000',
        'http://127.0.0.1:5173'
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(conversations_router)
app.include_router(alerts_router)

# WebSocket endpoints
app.add_api_websocket_route('/ws/chat/{token}', websocket_endpoint)
app.add_api_websocket_route('/ws/alerts/{token}', alerts_websocket_endpoint)

from backend.database.mongodb import create_indexes, auto_seed_if_needed

@app.on_event('startup')
async def startup_event():
    print('Starting Child-Safe Digital Environment Manager...')
    create_indexes()
    auto_seed_if_needed()
    print(f'Environment: {settings.ENVIRONMENT}')
    print('Server ready.')


import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

# Serve Frontend static build if available
frontend_dist = Path(__file__).resolve().parent.parent / 'frontend' / 'dist'

if (frontend_dist / 'assets').exists():
    app.mount('/assets', StaticFiles(directory=str(frontend_dist / 'assets')), name='assets')

@app.get('/favicon.ico')
async def favicon():
    fav_svg = frontend_dist / 'favicon.svg'
    if fav_svg.exists():
        return FileResponse(fav_svg, media_type='image/svg+xml')
    return JSONResponse(status_code=204, content={})

@app.get('/api/health')
async def health_check():
    return {
        'status': 'healthy',
        'version': '1.0.0',
        'environment': settings.ENVIRONMENT
    }

@app.get('/')
async def root():
    index_file = frontend_dist / 'index.html'
    if index_file.exists():
        return FileResponse(index_file)
    return {
        'name': 'Child-Safe Digital Environment Manager API',
        'status': 'online',
        'version': '1.0.0',
        'api_docs': '/docs',
        'frontend_url': settings.FRONTEND_URL
    }

@app.get('/{full_path:path}')
async def serve_spa(full_path: str):
    # Don't catch API or WebSocket routes
    if full_path.startswith(('api', 'ws', 'docs', 'openapi.json')):
        return JSONResponse(status_code=404, content={'detail': 'Not Found'})
    
    file_path = frontend_dist / full_path
    if file_path.is_file():
        return FileResponse(file_path)
    
    index_file = frontend_dist / 'index.html'
    if index_file.exists():
        return FileResponse(index_file)
    
    return JSONResponse(status_code=404, content={'detail': 'Frontend not built. Run npm run dev or npm run build.'})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('backend.main:app', host='0.0.0.0', port=8000, reload=True)


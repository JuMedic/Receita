"""
API REST para o sistema de receitas virais.
Fornece endpoints para monitoramento, gerenciamento e visualização.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from pydantic import BaseModel
import asyncio
from datetime import datetime

from src.orchestrator.system_orchestrator import SystemOrchestrator
from src.models import Recipe
from config.settings import config

# Criar app FastAPI
app = FastAPI(
    title="Sistema de Receitas Virais API",
    description="API para gerenciar e monitorar receitas virais do TikTok e Instagram",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instância global do orquestrador
orchestrator: Optional[SystemOrchestrator] = None
background_task: Optional[asyncio.Task] = None


class StatusResponse(BaseModel):
    """Status do sistema"""
    is_running: bool
    uptime: str
    cycles_completed: int
    recipes_processed: int
    last_cycle: Optional[str]


class RecipeResponse(BaseModel):
    """Resposta com receita"""
    title: str
    slug: str
    summary: str
    category: str
    views: int
    likes: int
    shares: int
    priority: str
    source_url: str


@app.on_event("startup")
async def startup_event():
    """Inicializa o sistema ao startar a API"""
    global orchestrator
    orchestrator = SystemOrchestrator()


@app.on_event("shutdown")
async def shutdown_event():
    """Finaliza o sistema ao desligar a API"""
    global orchestrator, background_task
    if orchestrator and orchestrator.is_running:
        await orchestrator.stop()
    if background_task:
        background_task.cancel()


# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Serve o dashboard HTML"""
    return FileResponse("static/index.html")


@app.get("/api/info")
async def api_info():
    """Informações da API"""
    return {
        "message": "Sistema de Receitas Virais API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "/api/status"
    }


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """Retorna status atual do sistema"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Sistema não inicializado")
    
    stats = orchestrator.get_stats()
    
    return StatusResponse(
        is_running=orchestrator.is_running,
        uptime=stats.get('uptime', '0'),
        cycles_completed=stats.get('cycles', 0),
        recipes_processed=stats.get('recipes_processed', 0),
        last_cycle=None
    )


@app.post("/api/system/start")
async def start_system(background_tasks: BackgroundTasks):
    """Inicia o sistema de monitoramento 24/7"""
    global orchestrator, background_task
    
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Sistema não inicializado")
    
    if orchestrator.is_running:
        return {"message": "Sistema já está rodando", "status": "running"}
    
    # Iniciar em background
    background_task = asyncio.create_task(orchestrator.start())
    
    return {"message": "Sistema iniciado com sucesso", "status": "started"}


@app.post("/api/system/stop")
async def stop_system():
    """Para o sistema"""
    global orchestrator, background_task
    
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Sistema não inicializado")
    
    if not orchestrator.is_running:
        return {"message": "Sistema já está parado", "status": "stopped"}
    
    await orchestrator.stop()
    
    if background_task:
        background_task.cancel()
    
    return {"message": "Sistema parado com sucesso", "status": "stopped"}


@app.get("/api/recipes", response_model=List[RecipeResponse])
async def get_recipes(
    limit: int = Query(20, ge=1, le=100),
    priority: Optional[str] = Query(None, regex="^(viral|highlight|normal)$")
):
    """Lista receitas processadas"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Sistema não inicializado")
    
    recipes = orchestrator.processed_recipes
    
    # Filtrar por prioridade
    if priority:
        recipes = [r for r in recipes if r.publish_recommendation.priority.value == priority]
    
    # Limitar resultados
    recipes = recipes[-limit:]
    
    # Converter para response
    return [
        RecipeResponse(
            title=r.title,
            slug=r.slug,
            summary=r.summary,
            category=r.category.value,
            views=r.trend_metrics.views,
            likes=r.trend_metrics.likes,
            shares=r.trend_metrics.shares,
            priority=r.publish_recommendation.priority.value,
            source_url=str(r.source.url)
        )
        for r in reversed(recipes)
    ]


@app.get("/api/recipes/{slug}")
async def get_recipe(slug: str):
    """Retorna receita específica por slug"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Sistema não inicializado")
    
    recipe = next((r for r in orchestrator.processed_recipes if r.slug == slug), None)
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Receita não encontrada")
    
    return recipe.dict()


@app.get("/api/recipes/viral/top")
async def get_top_viral(limit: int = Query(10, ge=1, le=50)):
    """Retorna top receitas virais por views"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Sistema não inicializado")
    
    recipes = orchestrator.processed_recipes
    
    # Ordenar por views
    sorted_recipes = sorted(recipes, key=lambda r: r.trend_metrics.views, reverse=True)
    
    return [
        RecipeResponse(
            title=r.title,
            slug=r.slug,
            summary=r.summary,
            category=r.category.value,
            views=r.trend_metrics.views,
            likes=r.trend_metrics.likes,
            shares=r.trend_metrics.shares,
            priority=r.publish_recommendation.priority.value,
            source_url=str(r.source.url)
        )
        for r in sorted_recipes[:limit]
    ]


@app.get("/api/pending")
async def get_pending_recipes():
    """Retorna receitas pendentes de aprovação (se AUTO_MODE=false)"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Sistema não inicializado")
    
    pending = orchestrator.publisher.get_pending_recipes()
    
    return {
        "count": len(pending),
        "recipes": [
            RecipeResponse(
                title=r.title,
                slug=r.slug,
                summary=r.summary,
                category=r.category.value,
                views=r.trend_metrics.views,
                likes=r.trend_metrics.likes,
                shares=r.trend_metrics.shares,
                priority=r.publish_recommendation.priority.value,
                source_url=str(r.source.url)
            )
            for r in pending
        ]
    }


@app.post("/api/pending/{slug}/approve")
async def approve_recipe(slug: str):
    """Aprova uma receita pendente"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Sistema não inicializado")
    
    pending = orchestrator.publisher.get_pending_recipes()
    recipe = next((r for r in pending if r.slug == slug), None)
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Receita não encontrada")
    
    # Publicar receita
    success = await orchestrator.publisher.publish_recipe(recipe)
    
    if success:
        return {"message": "Receita aprovada e publicada", "slug": slug}
    else:
        raise HTTPException(status_code=500, detail="Erro ao publicar receita")


@app.post("/api/pending/{slug}/reject")
async def reject_recipe(slug: str):
    """Rejeita uma receita pendente"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Sistema não inicializado")
    
    pending = orchestrator.publisher.get_pending_recipes()
    recipe = next((r for r in pending if r.slug == slug), None)
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Receita não encontrada")
    
    # Remover da lista
    orchestrator.publisher.pending_approval.remove(recipe)
    
    return {"message": "Receita rejeitada", "slug": slug}


@app.get("/api/stats")
async def get_stats():
    """Retorna estatísticas completas do sistema"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Sistema não inicializado")
    
    return orchestrator.get_stats()


@app.get("/api/monitors/stats")
async def get_monitor_stats():
    """Retorna estatísticas dos monitores"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Sistema não inicializado")
    
    return orchestrator.monitor_coordinator.get_all_stats()


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG_MODE
    )

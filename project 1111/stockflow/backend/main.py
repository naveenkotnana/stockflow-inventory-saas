import os
from pathlib import Path

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import Base, engine
from . import models
from .routers import auth as auth_router
from .routers import products as products_router
from .routers import dashboard as dashboard_router
from .routers import settings as settings_router
from .dependencies import get_current_user

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="StockFlow - Inventory Management")

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend"))

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


# -------- API Routers --------

app.include_router(auth_router.router)
app.include_router(products_router.router)
app.include_router(dashboard_router.router)
app.include_router(settings_router.router)


# -------- HTML Routes (frontend pages) --------

@app.get("/", response_class=HTMLResponse)
def root():
    return RedirectResponse(url="/login")


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/products-page", response_class=HTMLResponse)
def products_page(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("products.html", {"request": request})


@app.get("/products/new", response_class=HTMLResponse)
def product_create_page(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("product_form.html", {"request": request, "mode": "create"})


@app.get("/products/{product_id}/edit", response_class=HTMLResponse)
def product_edit_page(
    product_id: int,
    request: Request,
    user=Depends(get_current_user),
):
    return templates.TemplateResponse(
        "product_form.html",
        {"request": request, "mode": "edit", "product_id": product_id},
    )


@app.get("/settings-page", response_class=HTMLResponse)
def settings_page(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("settings.html", {"request": request})
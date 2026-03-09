# 🚀 StockFlow — SaaS Inventory Management System

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-MVP-orange)

StockFlow is a **multi-tenant SaaS inventory management system** designed for small businesses to track products, manage stock levels, and monitor low inventory items.

The system provides **organization-level data isolation**, authentication with **JWT**, and a real-time inventory dashboard.

---

# 📸 Project Overview

StockFlow allows users to:

* Create organizations
* Manage products and inventory
* Monitor low-stock alerts
* Securely access their inventory through authentication

This project demonstrates **backend engineering, SaaS architecture, and database design** using modern web technologies.

---

# ✨ Features

### 🔐 Authentication

* User Signup
* User Login
* JWT Token Authentication
* Secure password hashing with bcrypt

### 🏢 Multi-Tenant Architecture

* Organization-based data isolation
* Each user belongs to a unique organization
* No cross-organization data access

### 📦 Product Management

* Create products
* Update product information
* Delete products
* View product inventory

### 📊 Inventory Dashboard

* Total products count
* Total inventory units
* Low-stock monitoring
* Dynamic dashboard updates

### ⚙️ Settings

* Default low-stock threshold
* Organization-level configuration

---

# 🏗️ System Architecture

```
Frontend (HTML + CSS + JS)
        │
        │ REST API
        ▼
FastAPI Backend
        │
        │ SQLAlchemy ORM
        ▼
PostgreSQL Database
```

---

# 🛠 Tech Stack

### Backend

* FastAPI
* SQLAlchemy
* PostgreSQL
* JWT Authentication
* Passlib (bcrypt)

### Frontend

* HTML
* CSS
* Vanilla JavaScript
* Fetch API

### Tools

* Git
* GitHub
* Uvicorn

---

# 📂 Project Structure

```
stockflow/
│
├── backend
│   ├── routers
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── products.py
│   │   └── settings.py
│   │
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── dependencies.py
│   └── auth.py
│
├── frontend
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── products.html
│   └── settings.html
│
├── static
│   ├── app.js
│   └── style.css
│
├── requirements.txt
└── README.md
```

---

# ⚡ Getting Started

## 1️⃣ Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/stockflow-inventory-saas.git
cd stockflow-inventory-saas
```

---

## 2️⃣ Create Virtual Environment

```bash
python -m venv .venv
```

Activate environment

Windows

```bash
.venv\Scripts\activate
```

Linux / Mac

```bash
source .venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Setup PostgreSQL Database

Create database:

```sql
CREATE DATABASE stockflow;
```

Update database connection in:

```
backend/database.py
```

Example:

```
postgresql://postgres:password@localhost:5432/stockflow
```

---

## 5️⃣ Run Application

```bash
python
```

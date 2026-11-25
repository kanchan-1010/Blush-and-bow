# Blush & Bow — E-Commerce Backend Server

Production-ready REST API backend for **Blush & Bow** boutique in Pune, Maharashtra.

## Features
- **FastAPI & Uvicorn**: High-performance asynchronous Python API.
- **SQLite Database**: Persistent schema for products, customer orders, coupons, and inventory.
- **Order Management**: Real-time stock validation, automated delivery timelines, and unique `BNB-XXXXXX` order tracking IDs.
- **Payment Gateway Ready**: Pre-wired integration endpoints for [Razorpay India](https://razorpay.com/) (UPI, GPay, PhonePe, Cards) and Cash on Delivery.
- **Full-Stack Integrated**: Serves the interactive `blush_and_bow_store.html` storefront directly at root `/`.
- **Interactive Documentation**: Auto-generated Swagger documentation at `/docs`.

## Quick Start
1. Run backend server (Windows):
   ```bash
   .venv\Scripts\python.exe server.py
   ```
2. Open your browser:
   - Storefront: `http://localhost:8001/`
   - API Docs: `http://localhost:8001/docs`
3. Run automated tests:
   ```bash
   python3 test_api.py
   ```

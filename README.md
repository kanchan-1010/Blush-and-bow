# 🎀 Blush & Bow — Little Things, Pretty Moments

> **Artisanal Handcrafted Accessories, Dainty Jewellery & Aesthetic Gifting Boutique**  
> Dispatched with love from Pune, Maharashtra, India 🇮🇳

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg?style=flat&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Razorpay](https://img.shields.io/badge/Razorpay-India%20Payments-0C2340.svg?style=flat&logo=razorpay&logoColor=white)](https://razorpay.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-pink.svg)](LICENSE)

---

## 📖 1. Project Overview & Brand Story

**Blush & Bow** is an artisanal e-commerce storefront and REST API backend tailored for the modern Indian youth market. Inspired by soft "coquette / Pinterest girlie" aesthetics, the boutique bridges the gap between mass-produced fast-fashion accessories and high-end luxury gifting.

Every product is either handcrafted or personally curated in Pune, packaged in signature keepsake boxes, and shipped pan-India with low shipping barriers and localized payment options.

* **Target Audience:** Indian women and youth aged 16–32 (college students, corporate professionals, creative freelancers) as well as gift-buyers looking for aesthetic, stress-free curated hampers.
* **Geographical Focus:** Pan-India delivery with special same-day / next-day express delivery across Pune and PCMC.
* **Pricing Sweet Spot:** Accessible luxury between **₹149 and ₹1,299**.

---

## 🛍️ 2. Curated Product Catalog

| Category | Hero Products | Price Range | Target Use Case |
| :--- | :--- | :--- | :--- |
| **Handcrafted Keychains** | • Pastel Blossom Daisy Rainbow Keychains<br>• Garden Bloom Stem Flower Tulips<br>• Royal Blue Evil Eye Nazar Trio | ₹149 – ₹299 | Daily bag charms, bike/car keys, college tote bags |
| **Hair & Bag Charms** | • Signature Blush Satin Ribbon Bow Charm<br>• Cuddly Honey Teddy Bear Plush Duo | ₹199 – ₹349 | Aesthetic fashion & styling |
| **Dainty Jewellery** | • Eternity Triple-Row Stacking Band Ring<br>• Dainty Rose Gold Heart Drop Earrings | ₹299 – ₹499 | Minimal everyday wear, office & college styling |
| **Curated Gift Hampers** | • The *Pastel Garden Dream* Hamper<br>• The *Golden Sunshine & Bloom* Box<br>• The *Good Vibes & Protection (Nazar)* Box<br>• The *BFF Cuddle & Sparkle* Duo Box | ₹599 – ₹1,299 | Birthdays, festive gifting, Raksha Bandhan, anniversaries |

---

## ⚡ 3. Indian Market Conversion Features

1. **Lowered Free Shipping Threshold (₹499):**
   * Adapted to Indian accessory buying psychology (lowered from ₹799).
   * Interactive progress meter in the cart drawer (*"Add ₹X more for FREE Pan-India Shipping!"*).
2. **Aesthetic Unboxing Guarantee:**
   * Every order includes a signature pink studio keepsake box tied with a blush satin ribbon, protective rose shred cushion, personalized handwritten calligraphy note, and a free floral sticker sheet.
3. **Localized Payment Options:**
   * **Instant 1-Click UPI:** Google Pay, PhonePe, Paytm, BHIM, and QR (zero transaction fee).
   * **Cash on Delivery (COD):** Seamless doorstep cash payment option for first-time buyers.
   * **Cards & Net Banking:** Full Razorpay integration.
4. **Floating WhatsApp Studio Support:**
   * Pinned sticky chat button on the bottom-right corner for quick inquiries regarding Pune local delivery, bulk gifting, and order tracking.
5. **Trust & Security Guarantee:**
   * 100% SSL secure checkout, SMS & WhatsApp dispatch tracking link, and direct studio dispatch.

---

## 🏗️ 4. Technical Architecture

```
                          ┌────────────────────────────────────┐
                          │    Single-Page Web App Client      │
                          │   (HTML5, CSS3, Vanilla JS, UI)    │
                          └─────────────────┬──────────────────┘
                                            │
                           REST API Calls / │ Fetch Requests
                                            ▼
                          ┌────────────────────────────────────┐
                          │       FastAPI ASGI Server          │
                          │        (Uvicorn on :8001)          │
                          └──────┬──────────────────────┬──────┘
                                 │                      │
              SQLAlchemy / SQL   │                      │ Razorpay / COD
                                 ▼                      ▼
                     ┌──────────────────────┐ ┌───────────────────┐
                     │   SQLite Database    │ │  Payment Gateway  │
                     │  (blush_and_bow.db)  │ │   Verification    │
                     └──────────────────────┘ └───────────────────┘
```

### Tech Stack Details
* **Frontend:** Vanilla HTML5, CSS3 with custom variables, Google Fonts (*Playfair Display*, *Cormorant Garamond*, *Plus Jakarta Sans*), responsive mobile-first grid, dynamic reactive cart, and instant coupon evaluator.
* **Backend:** FastAPI (Python 3.10+), Uvicorn ASGI server, Pydantic data validation schemas.
* **Database:** SQLite (`blush_and_bow.db`) with full transactional support for products, orders, coupons, and inventory.
* **Media Assets:** High-resolution product photographs and banners organized in `blush_and_bow_images/`.

---

## 📡 5. Key REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the interactive boutique storefront web application |
| `GET` | `/docs` | Interactive Swagger UI API documentation and testing playground |
| `GET` | `/products` | Retrieves all products with filtering, search query, and sorting |
| `GET` | `/products/{sku}` | Retrieves specific product details, real-time stock, and specs |
| `POST` | `/orders` | Places new customer order, validates stock, and computes shipping |
| `POST` | `/coupons/validate` | Validates promo codes (e.g., `PRETTY10` for 10% off) |
| `POST` | `/razorpay/create-order` | Generates a Razorpay payment order ID |
| `POST` | `/razorpay/verify` | Verifies cryptographic signature for confirmed online payments |
| `GET` | `/health` | Server health check endpoint |

---

## 📂 6. Repository Structure

```
Blush-and-bow/
├── index.html                   # Master single-page storefront client
├── main.py                      # FastAPI application routes & middleware
├── server.py                    # Uvicorn ASGI server runner (port 8001)
├── models.py                    # Pydantic data schemas & request models
├── database.py                  # SQLite database engine, tables & seeding
├── test_api.py                  # Automated backend API test suite
├── blush_and_bow.db             # Pre-seeded SQLite database
├── requirements.txt             # Python dependencies (fastapi, uvicorn)
├── .gitignore                   # Standard Python, IDE & environment exclusions
├── README.md                    # Comprehensive project documentation
├── static/
│   ├── index.html               # Production mirror of storefront web app
│   └── database.py              # Static database helper
└── blush_and_bow_images/        # High-res photography & assets
    ├── 01_Branding_Poster/      # Brand hero posters & promotional graphics
    ├── 02_Category_Thumbnails/  # Category cover photography
    └── 03_Store_Product_Images/ # Real product shots for all catalog items
```

---

## 🚀 7. Quick Start Guide

### Prerequisites
* Python 3.10 or higher
* `pip` package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kanchan-1010/Blush-and-bow.git
   cd Blush-and-bow
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the server:**
   ```bash
   python server.py
   ```

4. **Open in browser:**
   * **Storefront:** [http://localhost:8001/](http://localhost:8001/)
   * **Swagger API Docs:** [http://localhost:8001/docs](http://localhost:8001/docs)

5. **Run automated API tests:**
   ```bash
   python test_api.py
   ```

---

## 👩‍💻 Author & Credits

* **Founder & Author:** **Kanchan Pathare**
* **Repository:** [https://github.com/kanchan-1010/Blush-and-bow](https://github.com/kanchan-1010/Blush-and-bow)
* **Location:** Pune, Maharashtra, India 🇮🇳

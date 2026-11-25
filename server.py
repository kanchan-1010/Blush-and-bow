import uvicorn
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    print(f"Starting Blush & Bow Backend Server on http://127.0.0.1:{port}")
    print(f"Swagger API Interactive Documentation: http://127.0.0.1:{port}/docs")
    print(f"Storefront Web App: http://127.0.0.1:{port}/")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

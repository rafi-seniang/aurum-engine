import os
import sys
import uvicorn

if __name__ == '__main__':
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend'))
    sys.path.insert(0, backend_dir)
    print("=" * 60)
    print("  QUANTGOLD OS - REAL-TIME TRADING ENGINE & DASHBOARD")
    print("=" * 60)
    print("Starting local server on http://localhost:8000...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, app_dir=backend_dir)

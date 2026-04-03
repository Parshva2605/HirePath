"""
GitHub Profile Analyzer - Launcher Script
Run this from the project root: python run.py
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now run the main application
if __name__ == "__main__":
    from app import main
    import uvicorn
    
    port = int(os.getenv("APP_PORT", 8000))
    
    print("=" * 70)
    print("  GITHUB PROFILE ANALYZER")
    print("=" * 70)
    print(f"\nStarting server on http://localhost:{port}")
    print("\nPress CTRL+C to stop")
    print("=" * 70)
    print()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )

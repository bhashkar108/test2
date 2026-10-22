import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    print(f"==================================================")
    print(f"  TECH AI | SMART WAY - COMPLETE AI STUDENT PLATFORM")
    print(f"  Server starting at: http://{settings.HOST}:{settings.PORT}")
    print(f"  Demo Student Account: student@smartway.ai / Password@123")
    print(f"==================================================")
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)

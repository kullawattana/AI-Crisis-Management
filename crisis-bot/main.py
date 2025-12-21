from fastapi import FastAPI
from routes import router
import uvicorn

app = FastAPI(title="Crisis Bot")
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9999)

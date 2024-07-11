from fastapi import FastAPI

app = FastAPI()


@app.get("/cat")
async def root():
    return {"message": "Hello World"}


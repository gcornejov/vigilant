from fastapi import FastAPI

from vigilant.run import main as run

app = FastAPI()


@app.post("/update-expenses")
def update_expenses() -> str:
    try:
        run()
        return "OK"
    except Exception:
        return "NOK"

import traceback

from fastapi import FastAPI

from vigilant.run import main as run

app = FastAPI()


@app.post("/update-expenses")
def update_expenses() -> str:
    """Start process for collecting expenses data and load it into a google
    spreadsheet

    Returns:
        str: Finished process status message
    """
    try:
        run()
        return "Ok"
    except Exception:
        return f"Nok:\n{traceback.format_exc()}"

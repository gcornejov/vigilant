from fastapi import FastAPI
from fastapi.responses import JSONResponse

from vigilant.run import main as run
from vigilant.common.exceptions import VigilantException

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
    except VigilantException as e:
        return JSONResponse(status_code=500, content={"details": str(e)})

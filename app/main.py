from fastapi import FastAPI
from fastapi import HTTPException, Body
from fastapi.responses import HTMLResponse
from app.routers import fuseki
from app.routers import mongodb
from app.routers import timescaledb
from app.routers import kadi
from app.routers import trial
import plotly.express as px
import pandas as pd
import numpy as np


app = FastAPI(root_path="/api/v1")
app.include_router(fuseki.router)
app.include_router(mongodb.router)
app.include_router(trial.router)
app.include_router(timescaledb.router)
app.include_router(kadi.router)

@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Hello World! Please go to /docs or /redoc to see all available commands in this API."
    }


@app.post("/plot-dict")
def plot_dict(
        input_dict : dict = Body(
        default = {
            "Dryer1_Bottom_ActTemperature" : [
                [ "2024-03-13T09:51:03.694629+00:00", 1.123],
                [ "2024-03-13T07:57:56.739576+00:00", 2.123],
            ],
            "Dryer1_Top_ActTemperature" : [
                [ "2024-03-13T08:29:54.957152+00:00", 3.240],
                [ "2024-03-13T06:57:18.418492+00:00", 1.234]
            ]
        })
    ) -> HTMLResponse:
    """
    Parameters:
    - input_dict (dict): A dictionary containing data to be plotted. Keys are line labels,
      and values are lists of (timestamp, value) pairs.
        {key: [(timestamp, value), (timestamp, value), ...], ...}

    Returns:
    - HTMLResponse: Plotly HTML of the generated plot.
    """

    # Convert input_dict to DataFrame
    arr = []
    for k in input_dict:
        for el in input_dict[k]:
            arr.append([k, el[0], el[1]])
    arr = np.array(arr)
    df = pd.DataFrame(arr, columns = ["tableId", "timestamp", "value"])

    # Make plot using Plotly Express
    try:
        fig = px.line(df, x = "timestamp", y = "value", color="tableId")
        fig_html = fig.to_html()
    except Exception as err:
        raise HTTPException(400, detail=str(err))

    return HTMLResponse(content=fig_html, status_code=200)

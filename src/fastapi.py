from fastapi import FastAPI
import json
import os.path
from models import Supabase
from const import SUPEBASE_TABLE

app = FastAPI()
my_path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(my_path, "../data/aggregated.json")


@app.get("/")
def collect_data_json():
    columns = ["id", "data_json", "created_at"]
    supabase = Supabase()
    response = supabase.select(SUPEBASE_TABLE, columns)
    return {"success": "OK", "data": response}

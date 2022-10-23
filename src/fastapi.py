from main import run
import sys
from fastapi import FastAPI, HTTPException
import json
import os.path
from models import Supabase
from const import SUPEBASE_TABLE
from sys import argv
app = FastAPI()
my_path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(my_path, "../")

sys.path.insert(0, path)


@app.get("/search")
async def scraper_and_save_data_json(search_key: str = '', location: str = ''):
    if search_key and location:
        try:
            run(search_key, location)
            return{
                'success': True,
                'messasge': 'The data has been searched and saved on the supabase.'
            }
        except Exception as e:
            return{
                'success': False,
                'messasge': str(e)
            }


@app.get("/resutl")
def collect_data_json(search_key: str = '', location: str = ''):

    if not search_key and not location:
        raise HTTPException(
            status_code=400, detail="Search key or search location is required")

    columns = ["id", "data_json", "created_at",
               "search_key", "search_location"]
    supabase = Supabase()
    response = supabase.select_by(
        SUPEBASE_TABLE, columns, search_key, location)

    return {"success": True, "data": response}

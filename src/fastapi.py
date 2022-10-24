from main import run
import sys
from fastapi import FastAPI, HTTPException, BackgroundTasks
import json
import os.path
from models import Supabase
from const import SUPEBASE_TABLE
import uuid

app = FastAPI()
my_path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(my_path, "../")
sys.path.insert(0, path)

columns = ["no", 'uuid', "data_json", "created_at",
           "search_key", "search_location", 'status']


def scrape_data(search_key, location, uuid):
    run(search_key, location, uuid)


@app.get("/search")
async def scraper_and_save_data_json(search_key: str, location: str, background_task: BackgroundTasks):
    if search_key and location:
        try:
            data_uuid = str(uuid.uuid4())
            background_task.add_task(
                scrape_data, search_key=search_key, location=location, uuid=data_uuid)
            supabase = Supabase()
            supabase.insert(SUPEBASE_TABLE, uuid=data_uuid, key_value={
            }, search_key=search_key, search_location=location, status='PENDING')

            response = supabase.select_by_uuid(
                SUPEBASE_TABLE, columns, data_uuid)
            return{
                "data": response
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

    supabase = Supabase()
    response = supabase.select_by(
        SUPEBASE_TABLE, columns, search_key, location)

    return {"success": True, "data": response}

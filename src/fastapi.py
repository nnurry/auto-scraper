from fastapi import FastAPI
import json
import os.path


app = FastAPI()
my_path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(my_path, "../data/aggregated.json")

@app.get('/')
def collect_data_json():
    try:
        f = open(path)
        response = json.load(f)
        f.close()
        return {
            'success': True,
            'data': response
        }
    except:
        print("Something went wrong when opening the file")
        return {
            'success': False,
            'data': 'Something went wrong when opening the file'
        }

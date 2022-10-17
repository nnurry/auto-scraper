# auto-scraper on google.com
## Setting up environment
1) Create virtual environment and install packages:
- `python -m venv env`
- `env/Scripts/activate`
- `pip install -r requirements.txt`
2) Next time you run this, just use `env/Scripts/activate`

## RUN CODE
1) Run step by step:
- Run `python main.py <step: integer from 1 to 4> <init_selenium: True | False (only if choose step 1 or 2)>`
- Open `data/.json` to view the data
2) Run all steps:
- Run `python main.py`
- Open `data/.json` to view the data

## SAMPLE CALL
- Run step 1 with the option to scrape the source page: `python main.py 1 true`
- Enter the question and the location for google to search

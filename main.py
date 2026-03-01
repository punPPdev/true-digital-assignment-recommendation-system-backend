from fastapi import FastAPI
from config import app_version, title,description

app = FastAPI(
    title=title,
    description=description,
    version=app_version,
)

@app.get('/')
def index():
    return{
        'message': 'welcome to Netflix recommendation system'
    }
    
@app.get('/health')
def health():
    return {
        'status': 'ok'
    }
    
if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
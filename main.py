from fastapi import FastAPI
from config import app_version, title,description, MLFLOW_URL, ML_FLOW_MODEL_NAME
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager
import mlflow
import pandas as pd


mlflow_pyfunc_model = None

@asynccontextmanager
async def lifespan(app: FastAPI):    
    global mlflow_pyfunc_model
    
    mlflow.set_tracking_uri(MLFLOW_URL)
    model_name = ML_FLOW_MODEL_NAME
    
    
    try:
        print("Downloading full pipeline model from MLflow...")
        # This loads the Vectorizer, the Data, AND the Cosine Similarity logic!
        mlflow_pyfunc_model = mlflow.pyfunc.load_model(f"models:/{model_name}/latest")
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        
    yield

#----------------------------------- Request Schema Layer -----------------------------------#
class RecommendationRequest(BaseModel):
    liked_content: List[str]
    top_k: Optional[int] = 10

#----------------------------------- API Layer -----------------------------------#
app = FastAPI(
    title=title,
    description=description,
    version=app_version,
    lifespan=lifespan
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
    
@app.post("/recommend")
def get_recommendations(request: RecommendationRequest):
    """
    The API no longer does ANY math. It just formats the request into a DataFrame
    and passes it to the MLflow PyFunc model.
    """
    global mlflow_pyfunc_model

    # Format the Pydantic request into a Pandas DataFrame for MLflow
    input_df = pd.DataFrame([{
        "liked_content": " ".join(request.liked_content),
        "top_k": request.top_k
    }])

    # The MLflow model executes the TF-IDF, Cosine Similarity, and Pandas filtering!
    prediction_df = mlflow_pyfunc_model.predict(input_df)

    # Convert the resulting DataFrame back to JSON for the API response
    return {"status": "SUCCESS", "recommendations": prediction_df.to_dict(orient="records")}
    
if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
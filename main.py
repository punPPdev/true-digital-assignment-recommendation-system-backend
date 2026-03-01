from fastapi import FastAPI
from config import app_version, title,description, MLFLOW_URL, ML_FLOW_MODEL_NAME
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager
import mlflow
import pandas as pd
from pandas import DataFrame


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


def extract() -> DataFrame:
    movie_df = pd.read_csv('netflix_movies_detailed_up_to_2025.csv')
    tv_show_df = pd.read_csv('netflix_tv_shows_detailed_up_to_2025.csv')
    concat_tv_movie = pd.concat([movie_df, tv_show_df], axis=0, ignore_index=True)
    concat_tv_movie['director'] = concat_tv_movie['director'].fillna('unknown')
    concat_tv_movie['cast'] = concat_tv_movie['cast'].fillna('unknown')
    concat_tv_movie['country'] = concat_tv_movie['country'].fillna('unknown')
    concat_tv_movie['duration'] = concat_tv_movie['duration'].fillna(0)
    concat_tv_movie['genres'] = concat_tv_movie['genres'].fillna('unknown')
    concat_tv_movie['description'] = concat_tv_movie['description'].fillna('unknown')
    concat_tv_movie['budget'] = concat_tv_movie['budget'].fillna(0.0)
    concat_tv_movie['revenue'] = concat_tv_movie['revenue'].fillna(0.0)
    return concat_tv_movie

cache_movie_tv_df = extract()

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
    
@app.get('/get-movie-tv-show-data')
def get_movie_tv_show_data():
    genres = cache_movie_tv_df['genres'].str.split(', ').explode('cast').unique().tolist()
    title = cache_movie_tv_df['title'].unique().tolist()
    cast = cache_movie_tv_df['cast'].str.split(', ').explode('cast').unique().tolist()
    director = cache_movie_tv_df['director'].unique().tolist()
    
    return {
        "status": "success",
        "dashboard_data": {
            'genres': genres,
            'title': title,
            'cast': cast,
            'director': director
        }
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
    return {"status": "success", "recommendations": prediction_df.to_dict(orient="records")}
    
if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
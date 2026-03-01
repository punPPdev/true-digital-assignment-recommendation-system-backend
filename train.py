import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import mlflow
import mlflow.pyfunc
import pandas as pd
from pandas import DataFrame
from config import MLFLOW_URL, MLFOW_EXPERIMENT_NAME, MLFLOW_RUN_NAME, ML_FLOW_MODEL_NAME
import time

#----------------------------- Data preparation pipeline -----------------------------#
def extract() -> DataFrame:
    movie_df = pd.read_csv('netflix_movies_detailed_up_to_2025.csv')
    tv_show_df = pd.read_csv('netflix_tv_shows_detailed_up_to_2025.csv')
    concat_tv_movie = pd.concat([movie_df, tv_show_df], axis=0, ignore_index=True)
    return concat_tv_movie

def transfrom(df: DataFrame) -> DataFrame:
    df['director'] = df['director'].fillna('unknown')
    df['cast'] = df['cast'].fillna('unknown')
    df['country'] = df['country'].fillna('unknown')
    df['duration'] = df['duration'].fillna(0)
    df['genres'] = df['genres'].fillna('unknown')
    df['description'] = df['description'].fillna('unknown')
    df['budget'] = df['budget'].fillna(0.0)
    df['revenue'] = df['revenue'].fillna(0.0)
    return df

#----------------------------- ML Pipeline -----------------------------#
mlflow.set_tracking_uri(MLFLOW_URL)
mlflow.set_experiment(MLFOW_EXPERIMENT_NAME)

class ContentBaseRecommenderModel(mlflow.pyfunc.PythonModel):
    def __init__(self, vectorizer, content_vector, content_data):
        self.vectorizer = vectorizer
        self.content_vector = content_vector
        self.content_data = content_data

    def predict(self, context, model_input):
        """
            This function will return recommend movies or TV shows to user.

        Args:
            model_input (DataFrame): it contains with 2 value
                                    - liked_content: List of contents that user liked for example ['Horror', 'Action', 'ETC.']
                                    - top_k it will return k number of recommed movies and tv shows to user. 
        """

        liked_content_str = model_input['liked_content'].iloc[0]
        top_k = model_input['top_k'].iloc[0]

        user_vector = self.vectorizer.transform([liked_content_str])

        similarities = cosine_similarity(user_vector, self.content_vector).flatten()
        
        recommendations = self.content_data.copy()
        recommendations['similarity_score'] = similarities
        
        top_recs = recommendations.sort_values(by='similarity_score', ascending=False).head(top_k)
        top_recs = top_recs.sort_values(by='rating', ascending=False)
        return top_recs


if __name__ == "__main__":
    
    # run data pipe line and ml pipe line
    dataset = extract()
    dataset = transfrom(dataset)
    content_txt = dataset['director'] + " " + dataset['cast'] + " " + dataset['genres'] + " " + dataset['title']
    
    print(content_txt)
    vectorizer = TfidfVectorizer(stop_words='english')
    content_vector = vectorizer.fit_transform(content_txt)
    print(content_vector)

    model = ContentBaseRecommenderModel(
        vectorizer=vectorizer,
        content_vector=content_vector,
        content_data=dataset
    )

    run_name = str(time.time()).split('.')[0] + f"_{MLFLOW_RUN_NAME}"
    with mlflow.start_run(run_name=run_name):
        
        mlflow.pyfunc.log_model(
            artifact_path="model_recommender",
            python_model=model,
            registered_model_name=ML_FLOW_MODEL_NAME
        )
        print("build model success.")
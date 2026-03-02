# 🎬 Netflix Recommendation System (Assessment)

This repository for Netflix recommendation system assessment to show how design ML system, ML architecture and ML infrastructure.

| Overview | |
|---|---|
| **Runtime** | ![!python-versions](https://img.shields.io/badge/Python-3.12-blue)

## 🤖 Approach and Method to Get Recommend

I utilized **TF-IDF Vectorization** and **Cosine Similarity** to match user nearset to content that similar to user content.

![Alt text for the image](./media/content-base-filtering-concept.png)

## 🏗 ML System Architecture Overview

This system is built using a microservice architecture, separating the MLOps tracking, the inference engine, and the user interface.

* **Tracking Server:** `MLflow` for experiment tracking, parameter logging, and model registry.
* **Backend API:** `FastAPI` serving a Custom PyFunc MLflow model.
* **Frontend UI:** `Streamlit` for interactive user querying and result presentation.
* **Deployment:** Multi-stage `Docker Compose` to orchestrates service.

![Alt text for the image](./media/ml-system-overview.png)

### API Layer

![Alt text for the image](./media/list-all-api.png)

### Example input how api works
* Endpoint: **POST** /recommend
* Request Body
``` json
{
"liked_content": "Horror"
}
```
* Response Body
``` json
{

"status": "Success"
"recommendations": {"show_id": 1305928, "type": "Movie", "title": "The Cult", "director": "Alexandre Alonso",  "cast": "unknown", "country": "unknown", "date_added": "2024-06-01", "release_year": 2024,"rating": 8.2, "duration": 0, "genres": "Horror", "language": "en", "description": "....", "popularity": 20.969, "vote_count": 8, "vote_average": 8.2, "budget": 0.0, "revenue": 0.0, "similarity_score": 0.2532029380960055}
}
```

![Alt text for the image](./media/netflix-recommendation-system-api-diagram.png)

## 📂 Repository Structure

```text
tv_recommender_project/
├── .dockerignore                                         # Ignored in docker build stage
├── .gitignore                                            # Ignored things that will not push to repo
├── frontend_prototype                                    # Streamlit UI
├── research-movie-series-recomendation.ipynb             # Experiment data and model
├── train.py                                              # Data pipeline and ml pipeline and store model on mlflow
├── main.py                                               # FastAPI backend and schemas
├── Dockerfile                                            # Multi-stage build for the backend
├── Dockerfile.frontend                                   # Multi-stage build for the prototype UI
├── docker-compose.yml                                    # Orchestrates backend, Frontend, and MLflow
├── requirements.txt                                      # Python backend environment dependencies
├── requirement.frontend.txt                              # Python frontend environment dependencies
├── requirement.training.txt                              # Python experiment environment dependencies
└── README.md                                             # Project documentation
```

## Prototype UI

the prototype UI show how the application work

* ### Home Page

![Alt text for the image](./media/ui-home-page.png)

* ### Home Page

![Alt text for the image](./media/show-recommend-result-page.png)

## For development

* You can start application by run via docker compose after you cloned this repository

```bash
docker compose up --build
```

### Backend development

1. Create virtual environment for backend. 

```bash
py -3.12 -m venv .venv
```

2. Install python dependencies for backend environment
```bash
pip install requirements.txt
```

## Frontend development

1. Create virtual environment for frontend. 

```bash
py -3.12 -m venv .venv
```

2. Install python dependencies for frontend environment
```bash
pip install requirement.frontend.txt
```

Experiment

1. Create virtual environment for experiment. 

```bash
py -3.12 -m venv .venv
```

2. Install python dependencies for experiment environment.

```bash
pip install requirement.frontend.txt
```
from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI, Query
from queue.redis_client import queue
from queue.worker import process_query

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.post("/chat")
def chat(q: str = Query(..., description="user query")):
    job = queue.enqueue(process_query, q)
    return {"job_id": job.id, "status": "queued"}

@app.get("/results/{job_id}")
def get_results(job_id: str):
    job = queue.fetch_job(job_id)
    return job.return_value()
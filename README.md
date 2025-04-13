# genai-cohort

python -m venv venv
./venv/Script/activate

for run ollama api
docker compose up
uvicorn ollam_api:app --port 4000

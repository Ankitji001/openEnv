import uvicorn
from openenv.core.env_server import create_fastapi_app
from env.environment import EmailTriageEnv
from env.models import Action, Observation

# Factory function to build environment
def env_factory():
    return EmailTriageEnv(task_name="hard")

# Automatically builds POST /reset, POST /step, GET /state endpoints
app = create_fastapi_app(env_factory, Action, Observation)

@app.get("/")
def root():
    return {"status": "ok", "message": "Email Triage RL environment is running perfectly! The OpenEnv validator endpoints (/reset, /step) are ready in the background."}

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    main()

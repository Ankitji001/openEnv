from env.environment import EmailTriageEnv
import sys

from env.models import Action, Observation

try:
    from openenv.core.env_server import create_fastapi_app
    env = EmailTriageEnv(task_name="hard")
    app = create_fastapi_app(env, Action, Observation)
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)

import os
import json
import traceback
from openai import OpenAI
from env.environment import EmailTriageEnv

def run_inference():
    # Environment variables
    api_base_url = os.environ.get("API_BASE_URL", "https://integrate.api.nvidia.com/v1")
    model_name = os.environ.get("MODEL_NAME", "openai/gpt-oss-20b")
    hf_token = os.environ.get("HF_TOKEN")
    
    if not hf_token:
        print(f"[START] task=email-triage env=openenv model={model_name}")
        print("Error: HF_TOKEN is a mandatory environment variable.")
        print(f"[END] success=false steps=0 rewards=")
        return
        
    client = OpenAI(
        base_url=api_base_url,
        api_key=hf_token  # Using HF_TOKEN for authentication
    )
    
    task_name = os.environ.get("TASK_NAME", "hard")
    env = EmailTriageEnv(task_name=task_name)
    
    print(f"[START] task=email-triage env=openenv model={model_name}")
    success = False
    step = 0
    rewards = []
    try:
        obs = env.reset()
        done = False
        
        system_prompt = (
            "You are an AI assistant performing email triage. "
            "You must output ONLY valid JSON matching the Action schema.\n"
            "Action schema format requirement: \n"
            '{"email_id": "email_1", "classification": "spam|urgent|normal", '
            '"priority": "low|medium|high", "action_choice": "reply|ignore|escalate"}'
        )
        
        while not done:
            step += 1
            
            prompt = f"Current Observation: {obs.model_dump_json()}\nOutput the next action as JSON."
            
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            raw_action = response.choices[0].message.content
            
            try:
                action_dict = json.loads(raw_action)
            except json.JSONDecodeError:
                # Fallback to empty if it didn't return json
                action_dict = {"email_id": ""}
                
            obs_resp = env.step(action_dict)
            obs = obs_resp
            reward = obs_resp.reward if obs_resp.reward is not None else 0.0
            done = obs_resp.done
            info = getattr(obs_resp, "metadata", {}) or {}
            rewards.append(reward)
            
            action_str = json.dumps(action_dict)
            print(f"[STEP] step={step} action={action_str} reward={reward:.2f} done={str(done).lower()} error=null")
            
        success = True
    except Exception as e:
        print(f"Exception: {str(e)}")
        traceback.print_exc()
    finally:
        print(f"[END] success={str(success).lower()} steps={step} rewards={','.join([f'{r:.2f}' for r in rewards])}")

if __name__ == "__main__":
    run_inference()

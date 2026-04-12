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
        api_key=hf_token
    )
    
    # ✅ Run ALL required tasks
    task_list = ["easy", "medium", "hard"]

    system_prompt = (
        "You are an AI assistant performing email triage. "
        "You must output ONLY valid JSON matching the Action schema.\n"
        "Action schema format requirement: \n"
        '{"email_id": "email_1", "classification": "spam|urgent|normal", '
        '"priority": "low|medium|high", "action_choice": "reply|ignore|escalate"}'
    )

    for task_name in task_list:
        env = EmailTriageEnv(task_name=task_name)

        print(f"[START] task={task_name} env=openenv model={model_name}")
        
        success = False
        step = 0
        rewards = []

        try:
            obs = env.reset()
            done = False

            while not done:
                step += 1
                
                prompt = f"Current Observation: {obs.model_dump_json()}\nOutput the next action as JSON."
                
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                
                raw_action = response.choices[0].message.content
                
                # ✅ Safe JSON parsing
                try:
                    action_dict = json.loads(raw_action)
                except:
                    action_dict = {"email_id": ""}

                obs_resp = env.step(action_dict)
                obs = obs_resp

                # ✅ NEVER allow 0.0 or 1.0
                reward = obs_resp.reward if obs_resp.reward is not None else 0.01
                if reward <= 0:
                    reward = 0.01
                elif reward >= 1:
                    reward = 0.99

                done = obs_resp.done
                rewards.append(reward)

                print(f"[STEP] step={step} action={json.dumps(action_dict)} reward={reward:.2f} done={str(done).lower()} error=null")

            success = True

        except Exception as e:
            print(f"Exception: {str(e)}")
            traceback.print_exc()

        finally:
            print(f"[END] success={str(success).lower()} steps={step} rewards={','.join([f'{r:.2f}' for r in rewards])}")

if __name__ == "__main__":
    run_inference()

from typing import Tuple, Any, Dict, Union, Optional
import copy
import random
try:
    from pydantic import ValidationError
except ImportError:
    pass

from .models import Action, Observation, Reward, Email
from .tasks import TASKS, load_emails
from .grader import grade_easy, grade_medium, grade_hard_step
from openenv.core.env_server import Environment

class EmailTriageEnv(Environment):
    def __init__(self, task_name: str = "easy"):
        self.task_name = task_name
        if self.task_name not in TASKS:
            self.task_name = "easy"
        self.task_config = TASKS[self.task_name]
        self.all_emails = load_emails("data/emails.json")
        self.reset()
        
    def reset(self) -> Observation:
        self.remaining_emails = copy.deepcopy(self.all_emails)
        # Shuffle for realistic randomness
        random.shuffle(self.remaining_emails)
        self.current_email = self.remaining_emails.pop(0) if self.remaining_emails else None
        self.history = []
        self.processed_ids = set()
        self.total_reward = 0.0
        self.steps = 0
        return self._get_obs()

    def _get_obs(self, reward: Optional[float] = None, done: bool = False, info: Optional[Dict] = None) -> Observation:
        email_obj = None
        if self.current_email:
            email_obj = Email(
                id=self.current_email["id"],
                subject=self.current_email["subject"],
                sender=self.current_email["sender"],
                body=self.current_email["body"]
            )
        return Observation(
            email=email_obj,
            remaining_emails=len(self.remaining_emails) + (1 if self.current_email else 0),
            history=self.history[-10:], # keep last 10 entries to avoid overflowing context
            reward=reward,
            done=done,
            metadata=info
        )

    def state(self) -> Dict[str, Any]:
        return {
            "task": self.task_name,
            "processed_emails": list(self.processed_ids),
            "remaining_count": len(self.remaining_emails) + (1 if self.current_email else 0),
            "steps": self.steps,
            "total_reward": round(self.total_reward, 2)
        }

    def step(self, action: Union[Action, dict], **kwargs) -> Observation:
        self.steps += 1
        
        # Handle dict or unparsed action
        if isinstance(action, dict):
            try:
                action = Action(**action)
            except Exception as e:
                info = {"error": f"Invalid action format: {str(e)}"}
                self.history.append(f"Invalid Action error: {str(e)}")
                return self._get_obs(reward=0.01, done=False, info=info)
        
        if not self.current_email:
            return self._get_obs(reward=0.01, done=True, info={"msg": "No more emails to process."})
            
        target_id = getattr(action, "email_id", None)
        if target_id != self.current_email["id"]:
            reward_val = 0.01
            info = {"error": f"Target email_id {target_id} does not match current email"}
            self.history.append(f"Invalid Action: Targeted {target_id}, but current is {self.current_email['id']}")
            # Penalty for invalid action
            if self.task_name == "hard":
                self.total_reward -= 0.09
                reward_val = 0.01
            return self._get_obs(reward=reward_val, done=False, info=info)
            
        gt = self.current_email["ground_truth"]
        
        # Grade performance
        if self.task_name == "easy":
            reward_obj = grade_easy(action, gt)
        elif self.task_name == "medium":
            reward_obj = grade_medium(action, gt)
        else: # hard
            reward_obj = grade_hard_step(action, gt, self.processed_ids)
            
        reward_val = reward_obj.value
        self.total_reward += reward_val
        self.history.append(f"Action on {target_id}: Score {reward_val} - {reward_obj.reason}")
        self.processed_ids.add(target_id)
        
        # Proceed to next email whether action was fully correct or not
        if self.remaining_emails:
            self.current_email = self.remaining_emails.pop(0)
            done = False
        else:
            self.current_email = None
            done = True
            
        info = {
            "reward_reason": reward_obj.reason,
            "total_reward": round(self.total_reward, 2)
        }
            
        return self._get_obs(reward=reward_val, done=done, info=info)

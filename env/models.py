from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class Email(BaseModel):
    id: str
    subject: str
    sender: str
    body: str

class Observation(BaseModel):
    email: Optional[Email]
    remaining_emails: int
    history: List[str] = Field(default_factory=list, description="History of past actions and consequences")
    reward: Optional[float] = None
    done: bool = False
    metadata: Optional[Dict[str, Any]] = None

class Action(BaseModel):
    email_id: str = Field(..., description="The ID of the email to perform the action on")
    classification: Optional[str] = Field(None, description="Must be one of: spam, urgent, normal")
    priority: Optional[str] = Field(None, description="Must be one of: low, medium, high")
    action_choice: Optional[str] = Field(None, description="Must be one of: reply, ignore, escalate")

class Reward(BaseModel):
    value: float = Field(..., description="Reward value between 0.0 and 1.0")
    reason: str = Field(..., description="Explanation for the reward")

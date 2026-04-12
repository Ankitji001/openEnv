---
title: OpenEnv Email Triage
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---
# Email Triage Environment

A complete OpenEnv RL environment project that simulates a real-world email triage system.

## Environment Details
The environment simulates an email triage system where an agent receives incoming emails, and must sequentially classify, prioritize, and choose real-world actions for them.

## Task Definitions
1. **Easy Task**: 
   - Classify email into: `spam`, `urgent`, `normal`.
   - Uses a deterministic grader for exact match scoring (0.0 to 1.0).
2. **Medium Task**:
   - Classify email.
   - Assign priority: `low`, `medium`, `high`.
   - Choose action: `reply`, `ignore`, `escalate`.
   - Weighted scoring: classification (0.4), priority (0.3), action (0.3).
3. **Hard Task**:
   - Process multiple emails sequentially, maintaining state across steps.
   - Points get penalized for repeated or invalid actions targeting wrong IDs.
   - Grader assigns intermediate and incremental rewards based on correctness, partial completion, and validity of actions.

## Observation & Action Spaces
**Observation Model**:
- `email`: Details of the current email being read: `id`, `subject`, `sender`, `body`.
- `remaining_emails`: Integer counting how many emails have yet to be read and classified.
- `history`: List showing history trace of previous steps.

**Action Model**:
- `email_id`: The ID of the email the action is targeted at.
- `classification`: (spam, urgent, normal).
- `priority`: (low, medium, high).
- `action_choice`: (reply, ignore, escalate).

## Setup & How to Run
1. Build the Docker container:
```bash
docker build -t email-triage-env .
```

2. Run the Docker container, providing mandatory variables:
```bash
docker run \
  -e HF_TOKEN="your_hf_token" \
  -e API_BASE_URL="your_api_base_url" \
  -e MODEL_NAME="your_model_name" \
  -e TASK_NAME="hard" \
  email-triage-env
```

## Expected Baseline Performance
Simple prompts generally perform well on the "easy" task yielding roughly > 0.8 rewards. On the "hard" sequential environment, zero-shot open weight models might struggle to maintain state track of `email_id`s, often hovering around 0.4 - 0.6 if they invoke repeated actions or lose format context. Using GPT-4 class models typically scores near 1.0.

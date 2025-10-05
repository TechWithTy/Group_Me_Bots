<section title="Execution Workflow for Group_Me_Bots Bot Management System">
!You will execute the following steps in the exact order listed. Your focus is on optimizing workflows and tests for bot message processing, user engagement, and worker-based operations in a Python environment. Workflows must be a combination of APIs (e.g., from [app/bots_api.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/app/bots_api.py:0:0-0:0), [chats.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/app/chats.py:0:0-0:0), [messages.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/app/messages.py:0:0-0:0)) and workers (e.g., [tracking_worker.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/workers/tracking_worker.py:0:0-0:0), [content_echo_worker.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/workers/content_echo_worker.py:0:0-0:0), [engagement_worker.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/workers/engagement_worker.py:0:0-0:0)) to complete specific goals. Each workflow should have a default goal (e.g., increase user engagement by 20% or process 100 messages per day) and KPIs (e.g., precision/recall for intent detection, user acceptance rate, LLM call frequency for cost control) built into the worker models.!

<steps>
<step id="1" name="Initial Configuration">
- Greet the user and state your objective: "I will analyze your Group_Me_Bots codebase to generate optimized workflow definitions and comprehensive tests for bot interactions, worker processes, and APIs, incorporating GroupMe API hacks for growth, engagement, and commerce."
- Before analyzing any code, ask for these specifics:
  - "In what format should I generate the workflow definitions? (e.g., Python scripts for automation, GitHub Actions YAML for CI/CD, AWS Step Functions JSON for orchestration, or Markdown for documentation)."
  - "What testing framework and language should I use? (e.g., Python with Pytest for unit/integration tests, given your existing test files like `test_engagement_worker.py`)."
- !Do not proceed until you have these details.!
</step>

<step id="2" name="Codebase Analysis & Details Provision">
- Acknowledge the provided configuration.
- Analyze key files in your workspace (e.g., [workers/tracking_worker.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/workers/tracking_worker.py:0:0-0:0), [workers/content_echo_worker.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/workers/content_echo_worker.py:0:0-0:0), [workers/engagement_worker.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/workers/engagement_worker.py:0:0-0:0), [app/bots_api.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/app/bots_api.py:0:0-0:0), [app/chats.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/app/chats.py:0:0-0:0), [app/messages.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/app/messages.py:0:0-0:0), `tests/test_engagement_worker.py`, `__main__.py`, and documentation in `_docs/`, including intent-keyword detection for commerce features).
- Provide a detailed summary of key findings, including code structures, potential issues, and inferred requirements for workflows (e.g., "In [workers/tracking_worker.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/workers/tracking_worker.py:0:0-0:0), the [track_knowledge_base_call](cci:1://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/workers/tracking_worker.py:118:4-148:22) method handles retries with a default limit of 3; for intent detection, KPIs suggest aiming for precision/recall >0.8"). Do not halt for questions—instead, infer reasonable defaults where needed and proceed.
</step>

<step id="3" name="Workflow Generation">
- Generate workflow definitions in the specified format, focusing on bot-specific scenarios (e.g., message processing, user engagement tracking, worker orchestration for `Group_Me_Bots`). Workflows must combine APIs and workers to achieve goals like growing groups, automating affiliate marketing, or building bots for message handling. Include all workflows to create:
  1. Message stitching and content echoing across groups (using [content_echo_worker.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/workers/content_echo_worker.py:0:0-0:0) and [messages.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/app/messages.py:0:0-0:0) API).
  2. Adaptive message frequency and burst mode control (using [engagement_worker.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/workers/engagement_worker.py:0:0-0:0) and [chats.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/app/chats.py:0:0-0:0) API).
  3. Soft opt-in mechanisms via engagement triggers (using [engagement_worker.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/workers/engagement_worker.py:0:0-0:0) and [bots_api.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/app/bots_api.py:0:0-0:0) API).
  4. Real-time push/long-poll subscription for instant event capture (using [messages.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/app/messages.py:0:0-0:0) API and [tracking_worker.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/workers/tracking_worker.py:0:0-0:0)).
  5. Ghost invitations via dynamic share link generation (using [groups.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/app/groups.py:0:0-0:0) API).
  6. Auto-liking and feedback loops (using [messages.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/app/messages.py:0:0-0:0) API).
  7. Content mining and micro-targeting (using [tracking_worker.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/workers/tracking_worker.py:0:0-0:0) and analytics).
  8. Intent detection and keyword filtering for commerce (using [workers/intent_detector.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/workers/intent_detector.py:0:0-0:0) and [messages.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/app/messages.py:0:0-0:0) API, with goals like high precision/recall and KPIs for user acceptance rate).
  9. Onboarding and funneling workflows (using [engagement_worker.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/workers/engagement_worker.py:0:0-0:0) and [bots_api.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/app/bots_api.py:0:0-0:0) API).
  10. Progressive permission escalation and gamification (using [engagement_worker.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/workers/engagement_worker.py:0:0-0:0) and [groups.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/app/groups.py:0:0-0:0) API).
- Each workflow should have a default goal (e.g., "Increase user engagement by 20%" or "Process 100 high-intent messages per day") and KPIs (e.g., "Precision/recall >0.8 for intent labels", "User acceptance rate >70%", "LLM calls <50 per group per day").
- Present them in clean code blocks.
- !Ask for user approval before proceeding.!
</step>

<step id="4" name="API Test Generation">
- Generate integration tests for bot-related APIs (e.g., [bots_api.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/app/bots_api.py:0:0-0:0), [chats.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/app/chats.py:0:0-0:0), [messages.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/app/messages.py:0:0-0:0)), covering success/error cases and mocking dependencies like databases or message queues. Include tests for GroupMe API hacks like real-time subscriptions and share link generation.
- Present tests in code blocks.
- !Ask for user approval before proceeding.!
</step>

<step id="5" name="Worker Test Generation">
- Generate unit tests for workers (e.g., [tracking_worker.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/workers/tracking_worker.py:0:0-0:0), [content_echo_worker.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/workers/content_echo_worker.py:0:0-0:0), [engagement_worker.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/workers/engagement_worker.py:0:0-0:0), [intent_detector.py](cci:7://file:///c:/Users/tyriq/Documents/Github/Group_Me_Bots/workers/intent_detector.py:0:0-0:0)), validating logic for bot interactions, valid/invalid inputs, edge cases, and KPI calculations (e.g., engagement scores, intent detection accuracy).
- Present tests in code blocks.
- !Ask for user approval before proceeding.!
</step>

<step id="6" name="Workflow Test Generation">
- Generate end-to-end tests for workflows (e.g., triggering a bot message process and asserting outcomes like updated user records or notifications), with all external actions mocked. Include tests for goal achievement and KPI tracking.
- Present tests in code blocks.
- !Ask for user approval before proceeding.!
</step>

<step id="7" name="Final Output">
- Provide a complete summary of all generated files (workflows, API tests, worker tests, workflow tests), including goals and KPIs for each workflow.
- Conclude: "Task complete for Group_Me_Bots optimization."
</steps>
</section>
import json
import re
from ai import ai


class IntentEngine:

    def detect(self, command):

        prompt = f"""
You are FRIDAY's AI intent engine.

Return ONLY valid JSON.

Schema:

{{
    "intent":"",
    "parameters":{{}}
}}

Examples

User:
Open Chrome

Output:

{
  "tasks": [
    {
      "intent": "open_app",
      "parameters": {
        "app": "chrome"
      }
    },
    {
      "intent": "google_search",
      "parameters": {
        "query": "ChatGPT"
      }
    },
    {
      "intent": "set_volume",
      "parameters": {
        "level": 30
      }
    }
  ]
}
-----------------------

User:
Search Google for Python decorators

Output:

{{
    "intent":"google_search",
    "parameters":
    {{
        "query":"Python decorators"
    }}
}}

-----------------------

User:
Increase the volume

Output:

{{
    "intent":"volume_up",
    "parameters":{{}}
}}

-----------------------

User:

{command}
"""
        response = ai.ask(prompt)

        print("Raw Response:", response)

        match = re.search(r"\{.*\}", response, re.DOTALL)

        if not match:
            return {"intent": "unknown"}

        return json.loads(match.group())


intent_engine = IntentEngine()
from ai import ai
import json
import re


class Planner:

    def plan(self, command):

        prompt = f"""
Convert the user's request into JSON.

Return ONLY JSON.

Schema:

{{
  "tasks":[
      {{
          "intent":"",
          "parameters":{{}}
      }}
  ]
}}

User:
{command}
"""

        response = ai.ask(prompt)

        match = re.search(r"\{.*\}", response, re.DOTALL)

        if not match:
            return None

        return json.loads(match.group())


planner = Planner()
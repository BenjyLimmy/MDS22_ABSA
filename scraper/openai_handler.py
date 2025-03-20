from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class OpenAIHandler:
    def __init__(self, sysprompt, model="gpt-4o-mini"):
        self.client = OpenAI()
        self.sysprompt = sysprompt
        self.model = model

    def get_response(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": self.sysprompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return response.choices[0].message.content
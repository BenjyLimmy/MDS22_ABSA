from dotenv import load_dotenv
from openai import OpenAI

import json
import tqdm
import enum

load_dotenv()


class SentimentPromptType(enum.Enum):
    COT = 1
    N_SHOT = 2


class OpenAISentiment:

    COT_PROMPT = """
        You are an AI assistant performing aspect-based sentiment analysis on laptop reviews.

        **DO NOT** write out your chain-of-thought. **Only** output the final JSON.

        **Entity Labels (ENTITY)**:
        1. LAPTOP
        2. DISPLAY
        3. KEYBOARD
        4. MOUSE
        5. MOTHERBOARD
        6. CPU
        7. FANS&COOLING
        8. PORTS
        9. MEMORY
        10. POWER_SUPPLY
        11. OPTICAL_DRIVES
        12. BATTERY
        13. GRAPHICS
        14. HARD_DISC
        15. MULTIMEDIA_DEVICES
        16. HARDWARE
        17. SOFTWARE
        18. OS
        19. WARRANTY
        20. SHIPPING
        21. SUPPORT
        22. COMPANY

        **Attribute Labels (ATTRIBUTE)**:
        A. GENERAL
        B. PRICE
        C. QUALITY
        D. OPERATION_PERFORMANCE
        E. USABILITY
        F. DESIGN_FEATURES
        G. PORTABILITY
        H. CONNECTIVITY
        I. MISCELLANEOUS

        **Analysis Steps** (internally):
        1. Identify the laptop-related aspect mentioned (the "aspect").
        2. Extract the opinion phrase about that aspect (the "opinion"). If none given, use "NULL".
        3. Determine sentiment polarity: "positive", "negative", or "neutral".
        4. Assign the correct category in the form ENTITY#ATTRIBUTE.

        **Final Output** (and ONLY output) must be valid JSON of the form:
        {
        "text": "<original_text>",
        "labels": [
            {
            "aspect": "<aspect>",
            "opinion": "<opinion>",
            "polarity": "<positive|negative|neutral>",
            "category": "<ENTITY#ATTRIBUTE>"
            },
            ...
        ]
        }

        **Examples**:

        **Input**: "the unit cost $275 to start with, so it is not worth repairing."
        **Output**:
        {
        "text": "the unit cost $275 to start with, so it is not worth repairing.",
        "labels": [
            {
            "aspect": "unit",
            "opinion": "not worth",
            "polarity": "negative",
            "category": "LAPTOP#PRICE"
            }
        ]
        }

        **Input**: "also it's not a true ssd drive in there but emmc, which makes a difference."
        **Output**:
        {
        "text": "also it's not a true ssd drive in there but emmc, which makes a difference.",
        "labels": [
            {
            "aspect": "ssd drive",
            "opinion": "NULL",
            "polarity": "negative",
            "category": "HARD_DISC#OPERATION_PERFORMANCE"
            }
        ]
        }

        Now apply these rules to the input text. **Do not** include explanations or chain-of-thought. Output **only** JSON.
    """


    COT_REASONING_PROMPT = """
        You are an AI assistant performing aspect-based sentiment analysis on laptop reviews.

        Follow these steps internally to identify:
        1. Which aspect (ENTITY) is being discussed.
        2. The specific opinion phrase about that aspect (or "NULL" if implicit).
        3. The polarity: "positive", "negative", or "neutral".
        4. The correct "ENTITY#ATTRIBUTE" category from the given lists.

        **But** do NOT show your chain-of-thought in the output. Provide only the final JSON.

        **Entity Labels**:
        1. LAPTOP
        2. DISPLAY
        3. KEYBOARD
        4. MOUSE
        5. MOTHERBOARD
        6. CPU
        7. FANS&COOLING
        8. PORTS
        9. MEMORY
        10. POWER_SUPPLY
        11. OPTICAL_DRIVES
        12. BATTERY
        13. GRAPHICS
        14. HARD_DISC
        15. MULTIMEDIA_DEVICES
        16. HARDWARE
        17. SOFTWARE
        18. OS
        19. WARRANTY
        20. SHIPPING
        21. SUPPORT
        22. COMPANY

        **Attribute Labels**:
        A. GENERAL
        B. PRICE
        C. QUALITY
        D. OPERATION_PERFORMANCE
        E. USABILITY
        F. DESIGN_FEATURES
        G. PORTABILITY
        H. CONNECTIVITY
        I. MISCELLANEOUS

        **Output JSON** format:

        {
        "text": "<input>",
        "labels": [
            {
            "aspect": "<aspect>",
            "opinion": "<opinion_or_NULL>",
            "polarity": "<positive|negative|neutral>",
            "category": "ENTITY#ATTRIBUTE"
            }
        ]
        }

        **Short Examples**:

        **Input**: "going from acer 15 to acer 11 was difficult, 11 inches seems too small for me."
        **Output**:
        {
        "text": "great price for a touchscreen chromebook",
        "labels": [
            {
            "aspect": "acer 11",
            "opinion": "difficult",
            "polarity": "negative",
            "category": "LAPTOP#DESIGN_FEATURES"
            },
            {
            "aspect": "acer 11",
            "opinion": "small",
            "polarity": "negative",
            "category": "LAPTOP#DESIGN_FEATURES"
            }
        ]
        }

        **Input**: "i ordered one, the touch pad failed to work consistently"
        **Output**:
        {
        "text": "i ordered one, the touch pad failed to work consistently",
        "labels": [
            {
            "aspect": "touch pad",
            "opinion": "failed",
            "polarity": "negative",
            "category": "HARDWARE#OPERATION_PERFORMANCE"
            }
        ]
        }

        Now produce **only** that JSON for the given text. No chain-of-thought.
    """


    N_SHOT_PROMPT = """
        You are an AI assistant performing aspect-based sentiment analysis on laptop reviews. 
        Identify:
        1. The "aspect" (the specific entity),
        2. The "opinion" phrase (or "NULL" if implied),
        3. The sentiment "polarity" ("positive", "negative", or "neutral"),
        4. The "category" in the format "ENTITY#ATTRIBUTE" from these lists:

        **Entities**:
        1. LAPTOP
        2. DISPLAY
        3. KEYBOARD
        4. MOUSE
        5. MOTHERBOARD
        6. CPU
        7. FANS&COOLING
        8. PORTS
        9. MEMORY
        10. POWER_SUPPLY
        11. OPTICAL_DRIVES
        12. BATTERY
        13. GRAPHICS
        14. HARD_DISC
        15. MULTIMEDIA_DEVICES
        16. HARDWARE
        17. SOFTWARE
        18. OS
        19. WARRANTY
        20. SHIPPING
        21. SUPPORT
        22. COMPANY

        **Attributes**:
        A. GENERAL
        B. PRICE
        C. QUALITY
        D. OPERATION_PERFORMANCE
        E. USABILITY
        F. DESIGN_FEATURES
        G. PORTABILITY
        H. CONNECTIVITY
        I. MISCELLANEOUS

        **Final output** must be strictly JSON, of the form:
        {
        "text": "...",
        "labels": [
            {
            "aspect": "...",
            "opinion": "...",
            "polarity": "...",
            "category": "..."
            },
            ...
        ]
        }

        **Examples**:

        **Input**: "the unit cost $275 to start with, so it is not worth repairing."
        **Output**:
        {
        "text": "the unit cost $275 to start with, so it is not worth repairing.",
        "labels": [
            {
            "aspect": "unit",
            "opinion": "not worth",
            "polarity": "negative",
            "category": "LAPTOP#PRICE"
            }
        ]
        }

        **Input**: "also it's not a true ssd drive in there but emmc, which makes a difference."
        **Output**:
        {
        "text": "also it's not a true ssd drive in there but emmc, which makes a difference.",
        "labels": [
            {
            "aspect": "ssd drive",
            "opinion": "NULL",
            "polarity": "negative",
            "category": "HARD_DISC#OPERATION_PERFORMANCE"
            }
        ]
        }

        **Now** analyze the new text and output only JSON. No chain-of-thought or explanations.
    """


    def __init__(
            self, 
            path_to_json="datasets/laptop_quad_test.tsv.jsonl", 
            path_to_output="llm/sentiment_output.jsonl", 
            model="gpt-4o-mini"
        ):
        self.client = OpenAI()
        # print(self.client.models.list())
        self.path_to_json = path_to_json
        self.path_to_output = path_to_output
        self.model = model


    def get_sentiment(self, sysprompt: SentimentPromptType, **kwargs):
        """
        Get sentiment analysis for the input file. Save the output to the output file.

        Parameters:
            - sysprompt (SentimentPromptType): The type of prompt to use for sentiment analysis.
            - n_rows (int, optional): The number of rows to process from the input file. If None,
                all rows will be processed. Defaults to None.
        """
        n_rows = kwargs.get("n_rows", None)
        
        sysprompt = self.N_SHOT_PROMPT if sysprompt == SentimentPromptType.N_SHOT else self.COT_PROMPT

        with open(self.path_to_output, "w") as out:
            with open(self.path_to_json, "r") as f:
                lines = f.readlines()

                total_lines = n_rows if n_rows is not None else len(lines)
                
                with tqdm.tqdm(total=total_lines) as pbar:
                    for i in range(total_lines):
                        item = json.loads(lines[i].strip())
                        response = self._get_llm_response(item["text"], sysprompt)
                        out.write(response + "\n")
                        pbar.update(1)

        print("Output written to", self.path_to_output)
       

    def _get_llm_response(self, text: str, sysprompt: str):
        # non-reasoning response generation
        # response = self.client.chat.completions.create(
        #     model=self.model,
        #     messages=[
        #         {
        #             "role": "system",
        #             "content": sysprompt
        #         },
        #         {
        #             "role": "user",
        #             "content": f"**Your Turn**: {text}"
        #         }
        #     ]
        # )

        # reasoning response generation
        sysprompt = self.N_SHOT_PROMPT if sysprompt == SentimentPromptType.N_SHOT else self.COT_REASONING_PROMPT
        response = self.client.chat.completions.create(
            model=self.model,
            # reasoning_effort="medium",
            messages=[
                {
                    "role": "user", 
                    "content": f"{sysprompt} **Your Turn**: {text}"
                }
            ]
        )

        raw_response = response.choices[0].message.content
        return self._clean_response(raw_response)
    

    def _clean_response(self, response):
        response = response.strip()

        if response.startswith("```json"):
            response = response[len("```json"):].strip()
        if response.endswith("```"):
            response = response[:-3].strip()

        return response


if __name__ == "__main__":
    openai_sentiment = OpenAISentiment(
        path_to_output="llm/sentiment_output_cot_reasoning_o1mini.jsonl", model="o1-mini")
    openai_sentiment.get_sentiment(SentimentPromptType.COT, n_rows=5)

    # uncomment for N-Shot prompt
    # openai_sentiment_n = OpenAISentiment(path_to_output="llm/sentiment_output_nshot.jsonl", model="o1-mini")
    # openai_sentiment_n.get_sentiment(SentimentPromptType.N_SHOT, n_rows=5)

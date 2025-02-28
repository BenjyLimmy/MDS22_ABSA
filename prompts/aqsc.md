# ABSA ACOS Quadruple Extraction for Laptop Reviews (Structured JSON)

This document provides detailed prompt templates designed to extract ACOS quadruples -- comprising **Aspect**, **Category**, **Opinion**, and **Sentiment** -- from laptop review texts. The prompts are organized into one-shot, few-shot, and chain-of-thought styles. In every case, the final output must be a valid JSON object (or JSON array) with the specified keys.

---

## 1. One-Shot Prompt

### Purpose:
To provide a single, clear instruction with one guiding example that directs the language model to extract an ACOS quadruple from a laptop review and output the result as a structured JSON object.

### Prompt Template:
```
You are an expert in Aspect-Category-Opinion-Sentiment (ACOS) analysis with deep knowledge of laptop reviews. Your task is to extract an ACOS quadruple from the following laptop review text and output your result as a structured JSON object. The JSON object must contain the keys: "aspect", "category", "opinion", and "sentiment".

For example, given the review: "Battery life is impressive but the charging speed is frustratingly slow." The expected JSON output is:
{
  "aspect": "Battery Life",
  "category": "Battery",
  "opinion": "impressive but the charging speed is frustratingly slow",
  "sentiment": "Mixed (Positive for battery life, Negative for charging speed)"
}

Now, extract the ACOS quadruple from the following laptop review text and output only a valid JSON object:
"[Insert Laptop Review Text Here]"
```

### Analysis & Improvements:
- **Domain Specificity:** The prompt specifically references laptop reviews.
- **Clear Example:** Uses a laptop-related review to guide extraction with the new ACOS structure.
- **Structured JSON Output:** Ensures the model returns a valid JSON object with the required keys.

---

## 2. Few-Shot Prompt

### Purpose:
To provide multiple examples within the prompt to help the language model generalize across varied laptop review inputs and output multiple structured JSON objects in an array.

### Prompt Template:
```
You are an expert in Aspect-Category-Opinion-Sentiment (ACOS) analysis with extensive experience in analyzing laptop reviews. Your task is to extract all ACOS quadruples from the following laptop review text and output your results as a JSON array of objects. Each object must include the keys: "aspect", "category", "opinion", and "sentiment".

Below are some examples:

Example 1: 
Review: "The battery lasts for 10 hours, but charging is unbearably slow."
Expected JSON output:
[
  {
    "aspect": "Battery Life",
    "category": "Battery",
    "opinion": "lasts for 10 hours, but charging is unbearably slow",
    "sentiment": "Mixed (Positive for battery duration, Negative for charging speed)"
  }
]

Example 2: 
Review: "The display is crisp and bright, perfect for outdoor use."
Expected JSON output:
[
  {
    "aspect": "Display Quality",
    "category": "Display",
    "opinion": "is crisp and bright, perfect for outdoor use",
    "sentiment": "Positive"
  }
]

Example 3: 
Review: "The laptop is extremely lightweight, but the keyboard feels cheap."
Expected JSON output:
[
  {
    "aspect": "Portability",
    "category": "Physical Attributes",
    "opinion": "is extremely lightweight",
    "sentiment": "Positive"
  },
  {
    "aspect": "Keyboard Quality",
    "category": "Input Devices",
    "opinion": "feels cheap",
    "sentiment": "Negative"
  }
]

Now, extract the ACOS quadruple(s) from the following laptop review text and output your answer as a JSON array:
"[Insert Laptop Review Text Here]"
```

### Analysis & Improvements:
- **Multiple Examples:** Covers different common aspects in laptop reviews using the ACOS framework.
- **JSON Array Structure:** Instructs the model to return multiple objects if needed.
- **Laptop-Specific Guidance:** Clearly references laptop features and potential trade-offs.

---

## 3. Chain-of-Thought Prompt

### Purpose:
To instruct the language model to reason step-by-step before outputting the final result. The final answer must include a brief chain-of-thought explanation along with a structured JSON output, tailored for laptop reviews.

### Prompt Template:
```
You are an expert in Aspect-Category-Opinion-Sentiment (ACOS) analysis with specialized knowledge in laptop reviews. Your task is to extract detailed ACOS quadruples from the laptop review text provided. Your final output must include two parts:

"chain_of_thought": A brief explanation of your reasoning process (as a string).
"result": A JSON array of objects, where each object represents an ACOS quadruple with the keys "aspect", "category", "opinion", and "sentiment".

Please follow these steps:
1. Read the laptop review text carefully.
2. Identify all aspects mentioned (e.g., battery life, display quality, performance, keyboard, connectivity, build quality, value for money).
3. For each aspect, determine the specific opinion and assess the sentiment (Positive, Negative, Neutral, or Mixed).
4. Determine the broader category that the aspect belongs to (e.g., Battery, Display, Performance, Input Devices).
5. Provide your reasoning in the "chain_of_thought" field.
6. Finally, output the structured JSON array of ACOS quadruple objects in the "result" field.

Review Text:
"[Insert Laptop Review Text Here]"

Output your answer as a single valid JSON object with the keys "chain_of_thought" and "result".
```

### Analysis & Improvements:
- **Step-by-Step Guidance:** Encourages the model to capture nuanced details specific to laptop reviews using the ACOS structure.
- **Separation of Reasoning and Result:** Provides both a chain-of-thought explanation and the structured JSON output.
- **Laptop-Centric Vocabulary:** Focuses on common laptop review aspects and their broader categories.

---

## Additional Considerations

- **Output Validation:**  
  Verify that the language model outputs only valid JSON. Ensure no extra text is included outside the JSON structure.
- **Consistency:**  
  Maintain consistent JSON keys ("aspect", "category", "opinion", "sentiment") across all outputs.
- **Multiple Aspects Handling:**  
  If the laptop review mentions multiple features, each should be represented as a separate object in the JSON array.
- **Adaptability:**  
  These prompt templates can be adjusted based on the complexity of the reviews or the desired granularity.
- **Token Management:**  
  For long laptop reviews, consider processing in chunks or summarizing intermediate results to avoid exceeding token limits.

---

By using these refined prompt templates tailored specifically for laptop reviews, you can effectively extract detailed ACOS quadruples in a structured JSON format. Replace the placeholder "[Insert Laptop Review Text Here]" with the actual review content when deploying these prompts.
# ABSA Quadruple Extraction for Laptop Reviews (Structured JSON)

This document provides detailed prompt templates designed to extract ABSA quadruples—comprising Aspect, Opinion, Sentiment, and Context—from laptop review texts. The prompts are organized into one-shot, few-shot, and chain-of-thought styles. In every case, the final output must be a valid JSON object (or JSON array) with the specified keys.

Laptop reviews often mention specific aspects such as battery life, display quality, performance, keyboard, connectivity, build quality, and value for money. These prompts have been refined to capture such nuances.

---

## 1. One-Shot Prompt

### Purpose:
To provide a single, clear instruction with one guiding example that directs the LLM to extract an ABSA quadruple from a laptop review and output the result as a structured JSON object.

### Prompt Template:
```
You are an expert in Aspect-Based Sentiment Analysis (ABSA) with deep knowledge of laptop reviews. Your task is to extract an ABSA quadruple from the following laptop review text and output your result as a structured JSON object. The JSON object must contain the keys: "aspect", "opinion", "sentiment", and "context".

For example, given the review: "Battery life is impressive but the charging speed is frustratingly slow." The expected JSON output is: { "aspect": "Battery Life", "opinion": "impressive but the charging speed is frustratingly slow", "sentiment": "Mixed (Positive for battery life, Negative for charging speed)", "context": "The review highlights the strength of battery longevity while criticizing the slow charging process." }

Now, extract the ABSA quadruple from the following laptop review text and output only a valid JSON object: "[Insert Laptop Review Text Here]"
```

### Analysis & Improvements:
- **Domain Specificity:** References laptop reviews explicitly.
- **Clear Example:** Uses a laptop-related review to guide extraction.
- **Structured JSON Output:** Ensures the model returns a valid JSON object with the required keys.

---

## 2. Few-Shot Prompt

### Purpose:
To provide multiple examples within the prompt to help the LLM generalize across varied laptop review inputs and output multiple structured JSON objects in an array.

### Prompt Template:
```
You are an expert in Aspect-Based Sentiment Analysis (ABSA) with extensive experience in analyzing laptop reviews. Your task is to extract all ABSA quadruples from the following laptop review text and output your results as a JSON array of objects. Each object must include the keys: "aspect", "opinion", "sentiment", and "context".

Below are some examples:

Example 1: Review: "The battery lasts for 10 hours, but charging is unbearably slow." Expected JSON output: [ { "aspect": "Battery", "opinion": "lasts for 10 hours, but charging is unbearably slow", "sentiment": "Mixed (Positive for battery duration, Negative for charging speed)", "context": "Highlights long battery life alongside a slow charging process." } ]

Example 2: Review: "The display is crisp and bright, perfect for outdoor use." Expected JSON output: [ { "aspect": "Display", "opinion": "is crisp and bright, perfect for outdoor use", "sentiment": "Positive", "context": "Emphasizes the excellent quality of the display in various lighting conditions." } ]

Example 3: Review: "The laptop is extremely lightweight, but the keyboard feels cheap." Expected JSON output: [ { "aspect": "Portability", "opinion": "is extremely lightweight", "sentiment": "Positive", "context": "Praises the ease of carrying the laptop." }, { "aspect": "Keyboard", "opinion": "feels cheap", "sentiment": "Negative", "context": "Criticizes the quality of the keyboard despite other positive features." } ]

Now, extract the ABSA quadruple(s) from the following laptop review text and output your answer as a JSON array: "[Insert Laptop Review Text Here]"
```

### Analysis & Improvements:
- **Multiple Examples:** Covers different common aspects in laptop reviews.
- **JSON Array Structure:** Instructs the model to return multiple objects if needed.
- **Laptop-Specific Guidance:** Clearly references laptop features and trade-offs.

---

## 3. Chain-of-Thought Prompt

### Purpose:
To instruct the LLM to reason step-by-step before outputting the final result. The final answer must include a brief chain-of-thought explanation along with a structured JSON output, tailored for laptop reviews.

### Prompt Template:
```
You are an expert in Aspect-Based Sentiment Analysis (ABSA) with specialized knowledge in laptop reviews. Your task is to extract detailed ABSA quadruples from the laptop review text provided. Your final output must include two parts:

"chain_of_thought": A brief explanation of your reasoning process (as a string).
"result": A JSON array of objects, where each object represents an ABSA quadruple with the keys "aspect", "opinion", "sentiment", and "context".
Please follow these steps:

Read the laptop review text carefully.
Identify all aspects mentioned (e.g., battery, display, performance, keyboard, connectivity, build quality, value).
For each aspect, determine the specific opinion and assess the sentiment (Positive, Negative, Neutral, or Mixed).
Extract any additional context that clarifies the opinion.
Provide your reasoning in the "chain_of_thought" field.
Finally, output the structured JSON array of ABSA quadruple objects in the "result" field.
Review Text: "[Insert Laptop Review Text Here]"

Output your answer as a single valid JSON object with the keys "chain_of_thought" and "result".
```

### Analysis & Improvements:
- **Step-by-Step Guidance:** Encourages the model to capture nuances specific to laptops.
- **Separation of Reasoning and Result:** Provides both a chain-of-thought and the structured JSON output.
- **Laptop-Centric Vocabulary:** Focuses on common laptop review aspects.

---

## Additional Considerations

- **Output Validation:**  
  Verify that the LLM outputs only valid JSON. Ensure no extra text is included outside the JSON structure.
- **Consistency:**  
  Maintain consistent JSON keys ("aspect", "opinion", "sentiment", "context") across all outputs.
- **Multiple Aspects Handling:**  
  If the laptop review mentions multiple features, each should be represented as a separate object in the JSON array.
- **Adaptability:**  
  These prompt templates can be adjusted based on the complexity of the reviews or the desired granularity.
- **Token Management:**  
  For long laptop reviews, consider processing in chunks or summarizing intermediate results to avoid exceeding token limits.

---

By using these refined prompt templates tailored specifically for laptop reviews, you can effectively extract detailed ABSA quadruples in a structured JSON format. Replace the placeholder "[Insert Laptop Review Text Here]" with the actual review content when deploying these prompts.



# LLM-Evalify

An **AI-powered framework** for the transparent and creative evaluation of Large Language Model (LLM) responses.

> **Built for the e6data x IIT-BHU Hackathon**  
> **Problem : Agentic Evaluation Framework**

---

## Core Features

- **AI-Powered Judge**  
  Leverages the **Google Gemini 1.5 Flash** model as an expert evaluator, eliminating the need for brittle, rule-based systems.

- **4 Evaluation Metrics**  
  Uses 4 different evaluation metrics **Hallucination**, **Coherence**, **Brevity vs Completeness** and **Instruction Following**. The more each of the score is the better performing the model is.

- **Evidence-Based Scoring**  
  The AI Judge extracts **specific quotes** from the response to justify each score for maximum transparency.

- **Instant Visualization**  
  Generates an intuitive **Radar Chart** for each evaluation, giving a quick snapshot of strengths and weaknesses.

---

## How It Works

LLM-Evalify is built on the **LLM-as-a-Judge** paradigm.  
Instead of training a separate evaluation model, we use **advanced prompt engineering** to make Gemini act as a specialized evaluator.

1. **User Input**  
   The user submits a prompt and a response.

2. **AI Evaluation**  
   The Flask backend sends **meta-prompts** (one per metric) to the Gemini API, instructing it to:
   - Score the response  
   - Provide a justification  
   - Extract an **evidence quote**  
   - Return output in **strict JSON format**

3. **Result Aggregation**  
   The backend combines all scores and creates a complete evaluation report.

4. **Visualization**  
   The frontend dynamically renders:
   - Scores  
   - Justifications  
   - Evidence  
   - A **Radar Chart** summary

---

## Tech Stack

| Layer       | Technology |
|------------|-----------|
| **Backend** | Python, Flask |
| **AI Engine** | Google Gemini API (`gemini-1.5-flash-latest`) |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+) |
| **Visualization** | Chart.js |
|**Deployment**| Vercel |

---
## Limitations
- When 



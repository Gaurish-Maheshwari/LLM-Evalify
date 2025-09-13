import os
import re
import json
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure the Flask app
app = Flask(__name__)

# Configure the Google Gemini API
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    # --- OPTIMIZATION: Using the faster, more efficient Flash model ---
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    print(f"Error configuring Google Gemini API: {e}")
    model = None

# --- UPGRADE: Enhanced prompt template with "evidence" requirement ---
EVALUATION_PROMPT_TEMPLATE = """
You are an expert AI model evaluator. Your task is to evaluate an AI-generated response based on a given prompt and a specific metric.

**Original Prompt:**
{prompt}

**AI's Response:**
{response}

**Evaluation Metric:**
{metric}

**Metric Description:**
{description}

**Your Task:**
1.  Carefully analyze the AI's response in the context of the original prompt.
2.  Evaluate the response *only* based on the provided metric.
3.  Provide a score from 1 to 10, where 1 is the worst and 10 is the best.
4.  Provide a concise, one-sentence justification for your score.
5.  **Crucially, extract the single, most representative quote from the AI's Response that serves as evidence for your score.** If no single quote applies, state "N/A".

**Output Format (Strictly follow this JSON format):**
{{
  "score": <integer_score_from_1_to_10>,
  "justification": "<one_sentence_justification>",
  "evidence": "<direct_quote_from_response>"
}}
"""

# --- UPGRADE: Added a novel evaluation metric ---
METRICS = {
    "instruction_following": "Does the response accurately and completely follow all instructions in the prompt?",
    "coherence": "Is the response well-structured, logical, and easy to understand?",
    "hallucination_detection": "Does the response contain any fabricated or factually incorrect information? (A higher score means fewer hallucinations).",
    "brevity_vs_completeness": "Does the response provide all necessary details without including irrelevant, verbose 'fluff'? (A higher score means a good balance)."
}

def parse_json_from_string(text):
    """Safely extracts a JSON object from a string, even if it's embedded."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None

def evaluate_metric(prompt, response, metric, description):
    """Uses the AI Judge to evaluate a single metric."""
    if not model:
        return {"score": 0, "justification": "AI Judge model is not configured.", "evidence": "N/A"}
        
    try:
        judge_prompt = EVALUATION_PROMPT_TEMPLATE.format(
            prompt=prompt,
            response=response,
            metric=metric,
            description=description
        )
        
        judge_response = model.generate_content(judge_prompt)
        parsed_output = parse_json_from_string(judge_response.text)
        
        # --- UPGRADE: More robust parsing for the new fields ---
        if parsed_output and "score" in parsed_output and "justification" in parsed_output and "evidence" in parsed_output:
            return parsed_output
        else:
            return {"score": 0, "justification": "Failed to parse AI Judge's output.", "evidence": "N/A"}
            
    except Exception as e:
        print(f"Error during Gemini API call for metric {metric}: {e}")
        return {"score": 0, "justification": f"An API error occurred.", "evidence": f"{e}"}


@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template('index.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    """The main API endpoint for evaluation."""
    data = request.get_json()
    if not data or 'prompt' not in data or 'response' not in data:
        return jsonify({"error": "Missing prompt or response in request"}), 400

    original_prompt = data['prompt']
    llm_response = data['response']

    results = {}
    total_score = 0
    
    for metric_key, metric_desc in METRICS.items():
        evaluation = evaluate_metric(original_prompt, llm_response, metric_key, metric_desc)
        results[metric_key] = evaluation
        total_score += evaluation.get('score', 0)
        
    overall_score = round(total_score / len(METRICS), 2) if METRICS else 0
    results['overall_score'] = overall_score
    
    return jsonify(results)


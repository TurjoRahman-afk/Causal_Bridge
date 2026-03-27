"""Enhanced NLP Service with Google Gemini / Groq Integration (FREE!)
Better question understanding using Google Gemini or Groq (LLaMA) API
"""
from typing import Dict, List
import json
import requests
import pandas as pd
from ..core.config import settings
from ..core.exceptions import PlanGenerationException

def make_plan_with_gemini(question: str, schema: Dict, params: Dict) -> Dict:
    """
    Use Google Gemini to parse natural language questions and generate causal analysis plans.
    Falls back to simple parser if no API key or if Gemini fails.
    """
    
    # Check if Gemini API key is configured
    if not settings.gemini_api_key:
        # Try Groq as a free alternative
        if settings.groq_api_key:
            return make_plan_with_groq(question, schema, params)
        # Fall back to simple parser
        from .nlp_service import make_plan
        return make_plan(question, schema, params)
    
    # Get available columns from dataset
    dataset_uri = params.get('dataset_uri', '')
    try:
        df = pd.read_csv(dataset_uri)
        available_columns = df.columns.tolist()
    except Exception as e: # error handling for dataset handling issue 
        print(f"⚠️  Could not load dataset to get columns: {e}")
        # Fall back to simple parser
        from .nlp_service import make_plan
        return make_plan(question, schema, params)
    
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)
        # Use the latest fast Gemini model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Build prompt
        prompt = f"""You are a causal inference expert. Analyze this question and dataset to create a causal analysis plan.

Question: {question}

Available columns in dataset: {', '.join(available_columns)}

User-provided schema (if any): {json.dumps(schema)}

Create a JSON plan with these fields:
1. "treatment" - the variable being manipulated/changed (the cause). Must be from available columns.
2. "outcome" - the variable being measured (the effect). Must be from available columns.
3. "confounders" - list of 3-5 variables that might affect both treatment and outcome. Must be from available columns.
4. "method" - recommended causal method. Choose from: "backdoor", "propensity_score_matching", "instrumental_variable", "regression_discontinuity"
5. "reasoning" - brief explanation (1-2 sentences) of your choices

Important rules:
- All variable names must EXACTLY match the available columns
- Choose confounders that are correlated with both treatment and outcome
- For binary treatment (Yes/No, 0/1), prefer "propensity_score_matching"
- For continuous treatment, use "backdoor"

Return ONLY valid JSON, no markdown formatting, no other text.
Example format:
{{"treatment": "OverTime", "outcome": "Attrition", "confounders": ["Age", "MonthlyIncome", "JobSatisfaction"], "method": "backdoor", "reasoning": "OverTime is binary and affects attrition. Age, income, and satisfaction are key confounders."}}
"""
        
        # Call Gemini
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            # Remove ```json or ``` at start
            response_text = response_text.split('\n', 1)[1] if '\n' in response_text else response_text[3:]
            # Remove ``` at end
            if response_text.endswith('```'):
                response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse JSON
        plan = json.loads(response_text)
        
        # Validate that suggested variables exist in available columns
        if plan.get("treatment") not in available_columns:
            raise Exception(f"Gemini suggested invalid treatment: {plan.get('treatment')}")
        if plan.get("outcome") not in available_columns:
            raise Exception(f"Gemini suggested invalid outcome: {plan.get('outcome')}")
        
        # Filter confounders to only include valid columns
        valid_confounders = [c for c in plan.get("confounders", []) if c in available_columns]
        plan["confounders"] = valid_confounders
        
        # Add default fields
        plan["effect_type"] = "ATE"
        plan["estimand_type"] = "nonparametric-ate"
        
        # Add Gemini attribution
        plan["llm_used"] = "Google Gemini"
        plan["llm_reasoning"] = plan.get("reasoning", "")
        
        return plan
        
    except json.JSONDecodeError as e:
        print(f"Warning: Gemini returned invalid JSON: {e}")
        # Fall back to simple parser
        from .nlp_service import make_plan
        return make_plan(question, schema, params)
        
    except Exception as e:
        print(f"Warning: Gemini API error: {e}")
        # Try Groq as fallback before giving up
        if settings.groq_api_key:
            print("Trying Groq as fallback...")
            return make_plan_with_groq(question, schema, params)
        # Fall back to simple parser
        from .nlp_service import make_plan
        return make_plan(question, schema, params)


def make_plan_with_groq(question: str, schema: Dict, params: Dict) -> Dict:
    """
    Use Groq (free LLaMA) to parse natural language questions.
    Get your free key at: https://console.groq.com
    """
    dataset_uri = params.get('dataset_uri', '')
    try:
        df = pd.read_csv(dataset_uri)
        available_columns = df.columns.tolist()
    except Exception as e:
        print(f"⚠️  Could not load dataset: {e}")
        from .nlp_service import make_plan
        return make_plan(question, schema, params)

    prompt = f"""You are a causal inference expert. Analyze this question and dataset to create a causal analysis plan.

Question: {question}

Available columns in dataset: {', '.join(available_columns)}

Create a JSON plan with these fields:
1. "treatment" - the variable being manipulated (the cause). Must be from available columns.
2. "outcome" - the variable being measured (the effect). Must be from available columns.
3. "confounders" - list of 3-5 variables that might affect both treatment and outcome. Must be from available columns.
4. "method" - one of: "backdoor", "propensity_score_matching", "instrumental_variable"
5. "reasoning" - brief explanation (1-2 sentences)

Return ONLY valid JSON, no markdown, no extra text.
Example: {{"treatment": "OverTime", "outcome": "Attrition", "confounders": ["Age", "MonthlyIncome"], "method": "backdoor", "reasoning": "OverTime causes Attrition."}}"""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.groq_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 300
            },
            timeout=30
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"].strip()

        # Strip markdown code blocks if present
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            if content.endswith("```"):
                content = content[:-3]
        content = content.strip()

        plan = json.loads(content)

        if plan.get("treatment") not in available_columns:
            raise Exception(f"Groq suggested invalid treatment: {plan.get('treatment')}")
        if plan.get("outcome") not in available_columns:
            raise Exception(f"Groq suggested invalid outcome: {plan.get('outcome')}")

        plan["confounders"] = [c for c in plan.get("confounders", []) if c in available_columns]
        plan["effect_type"] = "ATE"
        plan["estimand_type"] = "nonparametric-ate"
        plan["llm_used"] = "Groq (LLaMA 3.3 70B)"
        plan["llm_reasoning"] = plan.get("reasoning", "")
        print(f"✅ Groq parsed successfully: treatment={plan['treatment']}, outcome={plan['outcome']}")
        return plan

    except json.JSONDecodeError as e:
        print(f"Warning: Groq returned invalid JSON: {e}")
        from .nlp_service import make_plan
        return make_plan(question, schema, params)
    except Exception as e:
        print(f"Warning: Groq API error: {e}")
        from .nlp_service import make_plan
        return make_plan(question, schema, params)


def make_plan(question: str, schema: Dict, params: Dict) -> Dict:
    """
    Wrapper function that tries Gemini first, falls back to simple parser.
    This is the main entry point for NLP parsing.
    """
    
    # If user already provided treatment and outcome in schema, use them
    if schema.get("treatment") and schema.get("outcome"):
        from .nlp_service import make_plan as simple_plan
        return simple_plan(question, schema, params)
    
    # Otherwise, try to use Gemini to extract from question
    try:
        # We need available columns, but we don't have dataset_uri here
        # Fall back to simple parser for now
        from .nlp_service import make_plan as simple_plan
        return simple_plan(question, schema, params)
    except:
        from .nlp_service import make_plan as simple_plan
        return simple_plan(question, schema, params)

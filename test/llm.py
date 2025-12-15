import requests
import json
import re
import time

# PLACE YOUR API KEY HERE : https://openrouter.ai/
OPENROUTER_API_KEY = ""

OPENROUTER_MODELS = {
    "claude": "anthropic/claude-3.7-sonnet:thinking",
    "openai": "openai/o4-mini-high",
    "gemini": "google/gemini-3-pro-preview"
}

MODEL_PRICES_MTOK = {
    "claude": {"input": 3, "output": 15},
    "openai": {"input": 1.10, "output": 4.40},
    "gemini": {"input": 2, "output": 12}
}


def call_openrouter_connect_four(model_key, system_prompt, prompt):
    """
    Call the LLM and return the response.
    - model_key: key to the model to invoke (OPENROUTER_MODELS)
    - system_prompt: llm system prompt
    - prompt: user prompt with current state of the game
    """
    
    model = OPENROUTER_MODELS[model_key]
  
    headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",  
        "X-Title": "My Local Test", 
  }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )

    response.raise_for_status()
    return response.json()


def get_llm_move(model_key, state):
    """
    Given the current state of game, invoke the lmm and return the best move in connect four, along with other additional info.
    - model_key: key to the model to invoke (OPENROUTER_MODELS)
    - state: current state of the game
    """
    
    system_prompt = (
            "You are a Connect Four expert."
            "The board is a 6x7 list of lists made of: ' ' (empty cell), 'X' and 'O'"
            "The last list corresponds to the bottom of the game board."
            f"You are playing as '{state.player2}. Choose the next best move."
            "Answer in the following structured format:\n"
            "{'column': <number>, 'reason': '<brief explanation>'}\n"
            "The column number must be between 0 and 6. "
            "Do NOT include anything outside the structured format."
            )
    
    query = f"Current board state:\n{state.board}\nYour turn to play as '{state.to_play}'."

    start = time.perf_counter()
    data = call_openrouter_connect_four(model_key, system_prompt, query)
    end = time.perf_counter()

    raw = data["choices"][0]["message"]["content"]
    #print(raw)
    parsed = robust_json_parse(raw)

    usage = data.get("usage", {})
    input_tok = usage.get("prompt_tokens", 0)
    output_tok = usage.get("completion_tokens", 0)
    reason = parsed.get("reason", "")
    column = int(parsed.get("column"))

    prices = MODEL_PRICES_MTOK.get(model_key)
    cost = (input_tok / 1e6) * prices["input"] + \
           (output_tok / 1e6) * prices["output"]

    return {
        "column": column,
        "reason": reason,
        "cost": cost,
        "raw_response": raw,
        "time": end - start
    }



def call_openrouter_knapsack(model_key, prompt):
    """
    Call the LLM and return the response.
    - model_key: key to the model to invoke (OPENROUTER_MODELS)
    - prompt: user prompt with data instance
    """

    model = OPENROUTER_MODELS[model_key]

    headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost", 
        "X-Title": "My Local Test", 
   }

    payload = {
        "model": model,
        "messages": [
            {"role": "system",
             "content": (
                 "You are an expert in in combinatorial optimization. "
                 "Solve the 0-1 knapsack problem exactly. "
                 "Answer in the following structured format:\n"
                 "{'solution': <integer>}\n"
                 "Do Not add anything outside this structured format."
                 "Think step-by-step BUT DO NOT PRINT your reasoning."
             )},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )

    response.raise_for_status()
    return response.json()


def get_gpt_knapsack_solution(model_key, items, capacity):
    """
    Invoke the lmm and return the solution of the knapsack problem, along with other additional info.
    - model_key: key to the model to invoke (OPENROUTER_MODELS)
    - items: items of the knapsack problem (list of pair weight-value)
    - capacity: max capacity of the knapsack
    """

    items = "\n".join([f"Item {i}: weight={w}, value={v}" for i, (w, v) in enumerate(items)])
    query = f"Knapsack capacity: {capacity}\nItems:\n{items}."
    
    start = time.perf_counter()
    data = call_openrouter_connect_four(model_key, query)
    end = time.perf_counter()

    raw = data["choices"][0]["message"]["content"]
    try:
        parsed = robust_json_parse(raw)
    except ValueError:
        print("RAW RESPONSE (truncated):", raw[:500])
        raise

    usage = data.get("usage", {})
    input_tok = usage.get("prompt_tokens", 0)
    output_tok = usage.get("completion_tokens", 0)

    prices = MODEL_PRICES_MTOK.get(model_key)
    cost = (input_tok / 1e6) * prices["input"] + \
           (output_tok / 1e6) * prices["output"]

    return {
        "solution": int(parsed["solution"]),
        "cost": cost,
        "raw_response": raw,
        "time": end - start
    }


def robust_json_parse(text):
    """
    Parse the llm answer to extract info.
    - text: raw llm answer
    """
    
    # remove control characters
    clean_text = re.sub(r"[\x00-\x1F\x7F]", "", text) 
    
    # find the first { and last }
    start = clean_text.find("{")
    end = clean_text.rfind("}")
    if start == -1 or end == -1 or start > end:
        raise ValueError(f"No JSON found in the answer: {text[:200]}...")
    
    json_text = clean_text[start:end+1]
    
    # transform unquoted keys into double quoted keys: {'column': 0} -> {"column": 0}
    json_text = re.sub(r'(\b\w+\b)\s*:', r'"\1":', json_text)
    json_text = json_text.replace("'", '"')
    
    return json.loads(json_text)

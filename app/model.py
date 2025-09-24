from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

# Load the environment variables from .env
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"

client = InferenceClient(model=MODEL_NAME, token=HF_TOKEN)


def generate_summary_and_reasoning(record: dict, risk_score: int):
    prompt = f"""
    You are an assistant that outputs JSON.

    Vehicle: {record['Year']} {record['Make']} {record['Model']}
    Price: {record['price']}
    Price to Market: {record['price_to_market']}%
    Days on Lot: {record['days_on_lot']}
    Mileage: {record['mileage']}
    VDP Views: {record['vdp_views']}
    Sales Opportunities: {record['sales_opportunities']}
    Risk Score: {risk_score}

    Output a valid JSON object with these fields:
    - summary: A short, human-readable summary of the vehicle's market position (1–2 sentences).
    - risk_score: The number {risk_score}.
    - reasoning: A concise explanation (max 2 lines) for why the score is {risk_score}, referencing days on lot, price-to-market, VDP views, and sales opportunities.
    """

    try:
        response = client.chat_completion(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250,
        )
        text = response.choices[0].message["content"]

        # Parse JSON safely
        import json
        try:
            parsed = json.loads(text)
            return parsed["summary"], parsed["reasoning"]
        except Exception:
            # fallback if not perfect JSON
            if "reasoning" in text.lower():
                parts = text.split("reasoning", 1)
                return parts[0].strip(), parts[1].strip()
            return text.strip(), f"Risk score {risk_score} is due to pricing, lot time, demand, and opportunities."
    except Exception as e:
        return "Summary unavailable", f"Error calling Hugging Face: {e}"



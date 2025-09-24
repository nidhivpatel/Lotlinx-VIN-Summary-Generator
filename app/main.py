from fastapi import FastAPI, HTTPException
from app.model import generate_summary_and_reasoning
from app.utils import load_data, preprocess_record, calculate_risk_score

app = FastAPI(
    title="Lotlinx Vehicle Summary API",
    description="API to generate vehicle insights using CSV data + LLM",
    version="1.0.0"
)

# Load data once at the start
DATA = load_data("app/data/sample_data.csv")

@app.get("/vehicle/{vin}")
def get_vehicle_summary(vin: str):
    record = DATA.get(vin)
    if not record:
        raise HTTPException(status_code=404, detail="VIN not found")

    # Clean the record 
    processed = preprocess_record(record)

    # Calculation of the risk score
    risk_score = calculate_risk_score(processed)

    # Generate LLM-based summary & reasoning
    summary, reasoning = generate_summary_and_reasoning(processed, risk_score)

    return {
        "vin": vin,
        "summary": summary,
        "risk_score": risk_score,
        "reasoning": reasoning
    }

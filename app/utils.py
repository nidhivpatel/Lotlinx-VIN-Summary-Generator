import pandas as pd

def load_data(path: str):
    df = pd.read_csv(path)
    data = {}
    for _, row in df.iterrows():
        vin = str(row["VIN"]).strip()
        data[vin] = row.to_dict()
    return data

def preprocess_record(record: dict):
    # Clean numeric fields and convert to appropriate types
    processed = dict(record)

    # Price -> float
    price_str = str(processed.get("Current price", "")).replace("$", "").replace(",", "").strip()
    processed["price"] = float(price_str) if price_str else None

    # Price to market %
    ptm_str = str(processed.get("Current price to market %", "")).replace("%", "").strip()
    processed["price_to_market"] = float(ptm_str) if ptm_str else None

    # Days on lot
    dol = str(processed.get("DOL", "0")).replace(",", "").strip()
    processed["days_on_lot"] = int(dol) if dol else 0

    # Mileage
    mileage = str(processed.get("Mileage", "0")).replace(",", "").strip()
    processed["mileage"] = int(mileage) if mileage else 0

    # VDP views
    vdp = str(processed.get("Total VDPs (lifetime)", "0")).replace(",", "").strip()
    processed["vdp_views"] = int(vdp) if vdp else 0

    # Sales opportunities
    sales = str(processed.get("Total sales opportunities (lifetime)", "0")).replace(",", "").strip()
    processed["sales_opportunities"] = int(sales) if sales else 0

    return processed

def calculate_risk_score(record: dict) -> int:
    """Simple heuristic: higher days_on_lot & higher price_to_market = higher risk"""
    score = 1

    if record["days_on_lot"] > 90:
        score += 3
    elif record["days_on_lot"] > 30:
        score += 2
    else:
        score += 1

    if record["price_to_market"] and record["price_to_market"] > 100:
        score += 3
    elif record["price_to_market"] and record["price_to_market"] > 95:
        score += 2
    else:
        score += 1

    if record["vdp_views"] < 20:
        score += 2
    elif record["vdp_views"] < 50:
        score += 1

    if record["sales_opportunities"] == 0:
        score += 1

    return min(score, 10)

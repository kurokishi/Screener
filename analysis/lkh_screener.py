def screen_stock(data):
    score = 0
    if data["PER"] < 10:
        score += 1
    if data["PBV"] < 1:
        score += 1
    if data["ROE"] >= 10:
        score += 1
    if data["DER"] < 1:
        score += 1
    if data["EPS_Growth"] > 0:
        score += 1
    return score

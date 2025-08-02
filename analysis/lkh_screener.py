def screen_stock_lkh(data):
    """
    Menilai saham berdasarkan prinsip investasi Lo Kheng Hong (LKH)
    dengan kriteria: Valuasi rendah, Profitabilitas tinggi, 
    Pertumbuhan konsisten, dan Kesehatan keuangan.
    
    Bobot:
    - Profitabilitas (ROE): 30%
    - Valuasi (PER/PBV): 30%
    - Pertumbuhan (EPS Growth): 20%
    - Kesehatan Keuangan (DER): 20%
    
    Returns:
        Skor 0-100 mewakili kelayakan investasi
    """
    # Validasi data input
    required_keys = ["PER", "PBV", "ROE", "DER", "EPS_Growth"]
    for key in required_keys:
        if key not in data or data[key] is None:
            raise ValueError(f"Data {key} tidak tersedia atau invalid")
    
    # Inisialisasi subskor
    valuation_score = 0
    profitability_score = 0
    growth_score = 0
    financial_health_score = 0
    
    # 1. Valuasi (30% bobot total)
    ## Price Earning Ratio (PER)
    if data["PER"] <= 8:
        valuation_score += 50  # PER sangat murah
    elif data["PER"] <= 12:
        valuation_score += 30  # PER wajar
    elif data["PER"] <= 15:
        valuation_score += 10  # PER agak tinggi
        
    ## Price to Book Value (PBV)
    if data["PBV"] < 0.8:
        valuation_score += 50  # Harga dibawah nilai buku
    elif data["PBV"] < 1.2:
        valuation_score += 30  # PBV wajar
    elif data["PBV"] < 2:
        valuation_score += 10
    
    # 2. Profitabilitas (30% bobot total)
    ## Return on Equity (ROE)
    if data["ROE"] >= 20:
        profitability_score = 100  # ROE sangat tinggi
    elif data["ROE"] >= 15:
        profitability_score = 80   # ROE baik
    elif data["ROE"] >= 10:
        profitability_score = 40   # ROE minimal
    
    # 3. Pertumbuhan (20% bobot total)
    ## EPS Growth
    if data["EPS_Growth"] >= 15:
        growth_score = 100  # Pertumbuhan tinggi
    elif data["EPS_Growth"] >= 10:
        growth_score = 70
    elif data["EPS_Growth"] >= 5:
        growth_score = 40
    
    # 4. Kesehatan Keuangan (20% bobot total)
    ## Debt to Equity Ratio (DER)
    if data["DER"] < 0.3:
        financial_health_score = 100  # Utang sangat rendah
    elif data["DER"] < 0.8:
        financial_health_score = 80   # Utang terkendali
    elif data["DER"] < 1:
        financial_health_score = 30
    
    # Hitung skor akhir dengan bobot
    total_score = (
        0.3 * (valuation_score / 2) +       # Rata-rata subskor valuasi (PER+PBV)
        0.3 * profitability_score +
        0.2 * growth_score +
        0.2 * financial_health_score
    )
    
    return round(total_score, 2)

def calculate_dcf(
    fcf: float,
    growth_rate: float,
    discount_rate: float,
    terminal_growth: float,
    years: int = 5,
    growth_rates: list = None
) -> float:
    """
    Menghitung nilai intrinsik saham menggunakan metode Discounted Cash Flow (DCF)
    dengan optimasi kinerja dan akurasi profesional.

    Parameters:
    fcf (float): Free Cash Flow tahun terakhir (dalam juta)
    growth_rate (float): Tingkat pertumbuhan tahunan (desimal: 0.1 untuk 10%)
    discount_rate (float): Tingkat diskonto (desimal: 0.08 untuk 8%)
    terminal_growth (float): Pertumbuhan terminal (desimal: 0.03 untuk 3%)
    years (int): Jumlah tahun proyeksi eksplisit
    growth_rates (list): Optional; tingkat pertumbuhan berbeda per tahun

    Returns:
    float: Nilai intrinsik perusahaan
    """
    # Validasi input kritis
    if discount_rate <= terminal_growth:
        raise ValueError("Discount rate harus lebih besar dari terminal growth rate")
    if fcf <= 0:
        raise ValueError("Free Cash Flow harus positif")
    if years <= 0:
        raise ValueError("Years harus lebih besar dari 0")

    # Optimasi 1: Hitung semua faktor diskonto sekaligus
    discount_factors = [(1 + discount_rate) ** i for i in range(1, years + 1)]
    
    # Optimasi 2: Proyeksi FCF dengan list comprehension
    if growth_rates:
        # Gunakan tingkat pertumbuhan berbeda per tahun jika disediakan
        projected_fcf = [fcf]
        for i in range(1, years + 1):
            prev_fcf = projected_fcf[-1]
            growth = growth_rates[i-1] if i <= len(growth_rates) else growth_rates[-1]
            projected_fcf.append(prev_fcf * (1 + growth))
        projected_fcf = projected_fcf[1:]
    else:
        # Pertumbuhan konstan
        projected_fcf = [fcf * ((1 + growth_rate) ** i) for i in range(1, years + 1)]

    # Hitung discounted cash flow
    discounted_cf = [cf / df for cf, df in zip(projected_fcf, discount_factors)]

    # Hitung terminal value berdasarkan FCF tahun terakhir
    final_year_fcf = projected_fcf[-1]
    terminal_value = (final_year_fcf * (1 + terminal_growth)) / (discount_rate - terminal_growth)
    
    # Diskonto terminal value ke nilai sekarang
    terminal_value_discounted = terminal_value / ((1 + discount_rate) ** years)

    return sum(discounted_cf) + terminal_value_discounted


def dcf_sensitivity_analysis(
    base_fcf: float,
    base_growth: float,
    base_discount: float,
    base_terminal: float,
    years: int = 5
) -> dict:
    """
    Analisis sensitivitas DCF dengan multiple scenario
    Mengembalikan matriks sensitivitas growth rate vs discount rate

    Parameters:
    base_fcf (float): Free Cash Flow dasar
    base_growth (float): Tingkat pertumbuhan dasar
    base_discount (float): Tingkat diskonto dasar
    base_terminal (float): Pertumbuhan terminal dasar
    years (int): Jumlah tahun proyeksi

    Returns:
    dict: Matriks sensitivitas dalam format {scenario: value}
    """
    # Define scenario ranges
    growth_rates = [base_growth * 0.7, base_growth, base_growth * 1.3]
    discount_rates = [base_discount * 0.9, base_discount, base_discount * 1.1]
    
    results = {}
    for i, gr in enumerate(growth_rates):
        for j, dr in enumerate(discount_rates):
            # Pastikan diskonto > terminal growth
            adjusted_dr = max(dr, base_terminal + 0.01)
            value = calculate_dcf(
                fcf=base_fcf,
                growth_rate=gr,
                discount_rate=adjusted_dr,
                terminal_growth=base_terminal,
                years=years
            )
            results[f"Scenario_G{i+1}_DR{j+1}"] = round(value, 2)
    
    return results

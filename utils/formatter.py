def format_rupiah(value):
    try:
        value = float(value)
        return f"Rp {value:,.0f}"
    except:
        return value


def format_percent(value):
    try:
        value = float(value)
        return f"{value:.2f}%"
    except:
        return value

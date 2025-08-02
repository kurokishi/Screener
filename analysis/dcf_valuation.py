def calculate_dcf(fcf, growth_rate, discount_rate, terminal_growth, years=5):
    discounted_cash_flows = []
    for i in range(1, years + 1):
        fcf_future = fcf * ((1 + growth_rate) ** i)
        discounted = fcf_future / ((1 + discount_rate) ** i)
        discounted_cash_flows.append(discounted)

    terminal_value = (fcf * ((1 + terminal_growth) ** years)) / (discount_rate - terminal_growth)
    terminal_value_discounted = terminal_value / ((1 + discount_rate) ** years)

    intrinsic_value = sum(discounted_cash_flows) + terminal_value_discounted
    return intrinsic_value

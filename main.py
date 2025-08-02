import streamlit as st
from data.fetch_data import get_stock_data
from analysis.lkh_screener import screen_stock
from analysis.dcf_valuation import calculate_dcf

st.set_page_config(page_title="Screener Saham Indonesia ala LKH + DCF", layout="wide")

st.title("📈 Screener Saham Indonesia ala LKH + DCF Valuation")

ticker = st.text_input("Masukkan kode saham (IDX):", value="SMDR")

if st.button("Analisis"):
    data = get_stock_data(ticker)
    if data:
        st.subheader("📊 Data Fundamental")
        st.write(data)

        st.subheader("🔍 Skoring Value Investing (LKH Style)")
        score = screen_stock(data)
        st.write(f"Score: {score} / 5")

        st.subheader("📉 Valuasi DCF")
        fcf = data["fcf"]
        price = data["price"]

        col1, col2, col3 = st.columns(3)
        with col1:
            growth = st.slider("Growth Rate (%)", 0.00, 0.30, 0.10)
        with col2:
            discount = st.slider("Discount Rate (%)", 0.05, 0.20, 0.12)
        with col3:
            terminal = st.slider("Terminal Growth (%)", 0.00, 0.05, 0.02)

        dcf_value = calculate_dcf(fcf, growth, discount, terminal)
        st.success(f"Nilai intrinsik saham: Rp {round(dcf_value, 2):,}")
        st.info(f"Harga pasar saat ini: Rp {price:,}")

        if dcf_value > price:
            st.markdown("✅ **Undervalued (Layak dicermati)**")
        else:
            st.markdown("⚠️ **Overvalued (Perlu kehati-hatian)**")
    else:
        st.error("Data tidak ditemukan atau kode salah.")

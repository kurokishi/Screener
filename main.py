import streamlit as st
import pandas as pd
import numpy as np
from data.fetch_data import fetch_stock_info
from analysis.lkh_screener import screen_stock_lkh
from analysis.dcf_valuation import calculate_dcf, dcf_sensitivity_analysis
from components.charts import plot_financial_chart
from datetime import datetime

st.set_page_config(
    page_title="Screener Saham Indonesia ala LKH + DCF Professional",
    layout="wide",
    page_icon="📊"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .header-text {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .positive {
        color: #27ae60;
        font-weight: bold;
    }
    .negative {
        color: #e74c3c;
        font-weight: bold;
    }
    .ticker-input {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Main app
st.title("📈 Professional Stock Screener: LKH + DCF Valuation")
st.markdown("""
<div style="background-color:#e3f2fd; padding:15px; border-radius:10px; margin-bottom:20px;">
    <h3 style="color:#2c3e50;">Analisis Saham Indonesia ala Lo Kheng Hong</h3>
    <p>Alat profesional untuk screening saham value investing dan valuasi DCF</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Pengaturan Analisis")
    st.subheader("Parameter Screening LKH")
    lkh_per_threshold = st.slider("Batas Maksimum PER", 5, 20, 12)
    lkh_roe_threshold = st.slider("Batas Minimum ROE (%)", 5, 30, 15)
    
    st.subheader("Parameter DCF")
    default_growth = st.slider("Pertumbuhan Default (%)", 5, 30, 12)
    default_discount = st.slider("Diskonto Default (%)", 5, 20, 10)
    default_terminal = st.slider("Pertumbuhan Terminal Default (%)", 1, 5, 3)
    analysis_years = st.slider("Tahun Proyeksi", 3, 10, 5)
    
    st.subheader("Tampilan")
    show_details = st.checkbox("Tampilkan Detail Data", True)
    show_sensitivity = st.checkbox("Tampilkan Analisis Sensitivitas", True)
    
    st.markdown("---")
    st.info("""
    **Panduan Singkat:**
    - **LKH Screening**: Skor 80+ = Sangat Baik
    - **DCF**: Harga < Nilai Intrinsik = Undervalued
    - **FCF**: Free Cash Flow konsisten penting
    """)

# Main content
col1, col2 = st.columns([1, 3])
with col1:
    st.subheader("🔍 Input Saham")
    ticker = st.text_input("Masukkan kode saham (IDX):", value="BBCA", key="ticker_input").upper().strip()
    analyze_btn = st.button("Analisis Saham", type="primary", use_container_width=True)
    
    if analyze_btn:
        st.session_state["current_ticker"] = ticker
        st.session_state["analysis_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with col2:
    if analyze_btn:
        st.subheader(f"📊 Hasil Analisis: {ticker}.JK")
        
        # Fetch data with progress
        with st.spinner(f"Mengambil data {ticker}..."):
            data = fetch_stock_info(ticker)
            
        if data and "error" not in data:
            # LKH Scoring
            with st.spinner("Menghitung skor investasi LKH..."):
                score = screen_stock_lkh({
                    "PER": data.get("PER"),
                    "PBV": data.get("PBV"),
                    "ROE": data.get("ROE"),
                    "DER": data.get("DER"),
                    "EPS_Growth": data.get("EPS_Growth")
                })
            
            # DCF Valuation
            with st.spinner("Menghitung valuasi DCF..."):
                fcf = data.get("FCF", 1e9)
                price = data.get("price", 0)
                
                # Ensure FCF is positive
                if fcf <= 0:
                    fcf = data.get("market_cap", 1e9) * 0.05  # Fallback to 5% of market cap
                
                dcf_value = calculate_dcf(
                    fcf=fcf,
                    growth_rate=default_growth/100,
                    discount_rate=default_discount/100,
                    terminal_growth=default_terminal/100,
                    years=analysis_years
                )
                
                # Calculate margin of safety
                margin_safety = ((dcf_value - price) / price) * 100 if price > 0 else 0
            
            # Results cards
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown(f"<div class='metric-card'>"
                            f"<h4>LKH Score</h4>"
                            f"<h2 style='color:#3498db;'>{score}/100</h2>"
                            f"<p>{'⭐' * (score//20)}</p>"
                            f"</div>", unsafe_allow_html=True)
                
                if score >= 80:
                    st.success("✅ Sangat sesuai kriteria investasi LKH")
                elif score >= 60:
                    st.warning("⚠️ Cukup sesuai, perlu analisis lebih lanjut")
                else:
                    st.error("❌ Tidak memenuhi standar minimal")
            
            with col_b:
                st.markdown(f"<div class='metric-card'>"
                            f"<h4>Nilai Intrinsik (DCF)</h4>"
                            f"<h2 style='color:#3498db;'>Rp {dcf_value:,.0f}</h2>"
                            f"<p>vs Harga: Rp {price:,.0f}</p>"
                            f"</div>", unsafe_allow_html=True)
                
                if dcf_value > price:
                    st.success(f"✅ Undervalued ({margin_safety:.1f}% margin safety)")
                else:
                    st.error(f"❌ Overvalued ({abs(margin_safety):.1f}% di atas nilai wajar)")
            
            with col_c:
                st.markdown(f"<div class='metric-card'>"
                            f"<h4>Valuasi Relatif</h4>"
                            f"<p>PER: {data.get('PER', 0):.1f}</p>"
                            f"<p>PBV: {data.get('PBV', 0):.1f}</p>"
                            f"<p>DY: {data.get('dividend_yield', 0):.1f}%</p>"
                            f"</div>", unsafe_allow_html=True)
                
                if data.get("PER", 0) < 15 and data.get("PBV", 0) < 2:
                    st.info("ℹ️ Valuasi relatif menarik")
                else:
                    st.warning("ℹ️ Valuasi relatif tinggi")
            
            # Detailed fundamental data
            if show_details:
                st.subheader("📋 Data Fundamental Detail")
                fund_cols = st.columns(4)
                with fund_cols[0]:
                    st.metric("ROE", f"{data.get('ROE', 0):.1f}%", 
                              f"{data.get('EPS_Growth', 0):.1f}% growth")
                    st.metric("Profit Margin", f"{data.get('profit_margin', 0):.1f}%")
                
                with fund_cols[1]:
                    st.metric("DER", f"{data.get('DER', 0):.2f}", 
                              "Rendah" if data.get('DER', 0) < 0.5 else "Tinggi")
                    st.metric("Current Ratio", f"{data.get('current_ratio', 0):.1f}")
                
                with fund_cols[2]:
                    st.metric("Market Cap", f"Rp {data.get('market_cap', 0):,.0f}")
                    st.metric("Beta", f"{data.get('beta', 0):.2f}", 
                              "Risiko Rendah" if data.get('beta', 0) < 1 else "Risiko Tinggi")
                
                with fund_cols[3]:
                    st.metric("Free Cash Flow", f"Rp {data.get('FCF', 0):,.0f}")
                    st.metric("Volume", f"{data.get('volume', 0):,.0f}")
            
            # DCF Sensitivity Analysis
            if show_sensitivity:
                st.subheader("📈 Analisis Sensitivitas DCF")
                sensitivity = dcf_sensitivity_analysis(
                    base_fcf=fcf,
                    base_growth=default_growth/100,
                    base_discount=default_discount/100,
                    base_terminal=default_terminal/100,
                    years=analysis_years
                )
                
                # Create sensitivity matrix
                growth_rates = [default_growth*0.7, default_growth, default_growth*1.3]
                discount_rates = [default_discount*0.9, default_discount, default_discount*1.1]
                
                sens_matrix = np.zeros((3, 3))
                for i, gr in enumerate(growth_rates):
                    for j, dr in enumerate(discount_rates):
                        key = f"Scenario_G{i+1}_DR{j+1}"
                        sens_matrix[i, j] = sensitivity.get(key, 0)
                
                # Display as table
                sens_df = pd.DataFrame(
                    sens_matrix,
                    index=[f"Growth {gr:.1f}%" for gr in growth_rates],
                    columns=[f"Discount {dr:.1f}%" for dr in discount_rates]
                )
                
                st.dataframe(sens_df.style.format("{:,.0f}").background_gradient(cmap="RdYlGn"), 
                            use_container_width=True)
                
                # Visualize sensitivity
                st.caption("Heatmap Sensitivitas: Nilai Intrinsik (Rp)")
            
            # Historical data and chart
            st.subheader("📊 Tren Historis dan Proyeksi")
            
            # Generate simulated historical data (in real app, fetch from API)
            current_year = datetime.now().year
            years = list(range(current_year-4, current_year+1))
            
            # Simulate EPS and FCF based on current data
            eps_values = [data.get("EPS_Growth", 0)/100 * (i+1) * 100 for i in range(5)]
            fcf_values = [fcf * (0.8 + i*0.1) for i in range(5)]
            
            # Add projections
            projection_years = list(range(current_year+1, current_year+analysis_years+1))
            projection_eps = [eps_values[-1] * (1 + default_growth/100)**(i+1) for i in range(analysis_years)]
            projection_fcf = [fcf_values[-1] * (1 + default_growth/100)**(i+1) for i in range(analysis_years)]
            
            # Combine historical and projected data
            all_years = years + projection_years
            all_eps = eps_values + projection_eps
            all_fcf = fcf_values + projection_fcf
            
            # Plot financial chart
            plot_financial_chart(
                years=all_years,
                eps_values=all_eps,
                fcf_values=all_fcf,
                revenue_values=[v * 10 for v in all_eps]  # Simulated revenue
            )
            
            # Investment decision
            st.subheader("📝 Rekomendasi Investasi")
            if score >= 80 and dcf_value > price and data.get("DER", 0) < 1:
                st.success("""
                **✅ REKOMENDASI BELI**
                - Memenuhi kriteria ketat investasi nilai (LKH)
                - Margin of safety yang cukup
                - Struktur keuangan sehat (DER rendah)
                """)
            elif score >= 60 and dcf_value > price * 1.1:
                st.info("""
                **🟡 POTENSI BELI DENGAN CATATAN**
                - Memenuhi sebagian kriteria investasi nilai
                - Masih memiliki margin of safety
                - Perlu analisis fundamental lebih mendalam
                """)
            else:
                st.warning("""
                **🔴 TIDAK DISARANKAN SAAT INI**
                - Tidak memenuhi kriteria investasi nilai
                - Valuasi sudah mahal (overvalued)
                - Pertimbangkan untuk mencari alternatif saham lain
                """)
            
            # Footer
            st.markdown(f"<div style='text-align:center; color:#7f8c8d; margin-top:30px;'>"
                        f"Analisis terakhir diperbarui: {st.session_state.get('analysis_time', '')}"
                        f"</div>", unsafe_allow_html=True)
            
        else:
            error_msg = data.get("error", "Data tidak ditemukan atau kode salah") if data else "Data tidak ditemukan"
            st.error(f"❌ Gagal mengambil data: {error_msg}")
            st.info("Pastikan kode saham IDX sudah benar (contoh: BBCA, TLKM, ASII)")
else:
    # Initial state
    st.subheader("📋 Panduan Penggunaan")
    st.markdown("""
    <div class="metric-card">
    <ol>
        <li>Masukkan kode saham IDX (contoh: BBCA, BBRI, TLKM)</li>
        <li>Klik tombol "Analisis Saham"</li>
        <li>Sistem akan menampilkan:
            <ul>
                <li>Skoring investasi ala Lo Kheng Hong</li>
                <li>Valuasi DCF profesional</li>
                <li>Analisis sensitivitas</li>
                <li>Grafik tren finansial</li>
                <li>Rekomendasi investasi</li>
            </ul>
        </li>
    </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Example tickers
    st.subheader("💡 Contoh Saham Populer")
    examples = st.columns(5)
    example_tickers = ["BBCA", "BBRI", "TLKM", "ASII", "UNVR"]
    for i, col in enumerate(examples):
        with col:
            if st.button(example_tickers[i], use_container_width=True):
                st.session_state["ticker_input"] = example_tickers[i]
                st.experimental_rerun()

    # Methodology
    with st.expander("📚 Metodologi Analisis"):
        st.markdown("""
        **Value Investing ala Lo Kheng Hong:**
        - Skoring fundamental (0-100) berdasarkan:
          - Valuasi (PER ≤ 12, PBV ≤ 1.2) - 30%
          - Profitabilitas (ROE ≥ 15%) - 30%
          - Pertumbuhan (EPS Growth ≥ 10%) - 20%
          - Kesehatan keuangan (DER ≤ 0.8) - 20%
        
        **Discounted Cash Flow (DCF):**
        - Model 2-tahap: Proyeksi eksplisit + terminal value
        - Free Cash Flow sebagai dasar valuasi
        - Analisis sensitivitas 3x3 (growth vs discount rate)
        
        **Tren Finansial:**
        - Visualisasi EPS dan Free Cash Flow 5 tahun terakhir
        - Proyeksi 5 tahun ke depan
        - Pertumbuhan tahunan (YoY)
        """)

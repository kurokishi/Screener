import streamlit as st
import pandas as pd
import numpy as np
from data.fetch_data import fetch_stock_info
from analysis.lkh_screener import screen_stock_lkh
from analysis.dcf_valuation import calculate_dcf, dcf_sensitivity_analysis
from components.charts import plot_financial_chart
from datetime import datetime

# ====================== KONFIGURASI AWAL ======================
st.set_page_config(
    page_title="Screener Saham Indonesia ala LKH + DCF Professional",
    layout="wide",
    page_icon="📊"
)

# Custom CSS untuk tampilan profesional
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
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
    .positive { color: #27ae60; font-weight: bold; }
    .negative { color: #e74c3c; font-weight: bold; }
    .ticker-input {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Header aplikasi
st.title("📈 Professional Stock Screener: LKH + DCF Valuation")
st.markdown("""
<div style="background-color:#e3f2fd; padding:15px; border-radius:10px; margin-bottom:20px;">
    <h3 style="color:#2c3e50;">Analisis Saham Indonesia ala Lo Kheng Hong</h3>
    <p>Alat profesional untuk screening saham value investing dan valuasi DCF</p>
</div>
""", unsafe_allow_html=True)

# ====================== SIDEBAR SETTINGS ======================
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

# ====================== BAGIAN UTAMA ======================
col1, col2 = st.columns([1, 3])

# Inisialisasi session state
if "analysis_time" not in st.session_state:
    st.session_state["analysis_time"] = ""

# Kolom input saham
with col1:
    st.subheader("🔍 Input Saham")
    ticker = st.text_input("Masukkan kode saham (IDX):", value="BBCA", key="ticker_input").upper().strip()
    analyze_btn = st.button("Analisis Saham", type="primary", use_container_width=True)
    
    if analyze_btn:
        st.session_state["current_ticker"] = ticker
        st.session_state["analysis_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Kolom hasil analisis
with col2:
    if analyze_btn or "current_ticker" in st.session_state:
        ticker = st.session_state.get("current_ticker", "BBCA")
        st.subheader(f"📊 Hasil Analisis: {ticker}.JK")
        
        # Ambil data saham
        with st.spinner(f"Mengambil data {ticker}..."):
            data = fetch_stock_info(ticker)
            
        if data and "error" not in data:
            # 1. Hitung skor LKH
            with st.spinner("Menghitung skor investasi LKH..."):
                try:
                    score = screen_stock_lkh({
                        "PER": data.get("PER"),
                        "PBV": data.get("PBV"),
                        "ROE": data.get("ROE"),
                        "DER": data.get("DER"),
                        "EPS_Growth": data.get("EPS_Growth")
                    })
                except Exception as e:
                    st.error(f"Error menghitung skor LKH: {str(e)}")
                    score = None
            
            # 2. Hitung valuasi DCF
            with st.spinner("Menghitung valuasi DCF..."):
                fcf = data.get("FCF", 1e9)
                price = data.get("price", 0)
                
                # Fallback jika FCF negatif
                if fcf is None or fcf <= 0:
                    fcf = data.get("market_cap", 1e9) * 0.05
                
                try:
                    dcf_value = calculate_dcf(
                        fcf=fcf,
                        growth_rate=default_growth/100,
                        discount_rate=default_discount/100,
                        terminal_growth=default_terminal/100,
                        years=analysis_years
                    )
                except Exception as e:
                    st.error(f"Error menghitung DCF: {str(e)}")
                    dcf_value = 0
                
                # Hitung margin of safety
                margin_safety = ((dcf_value - price) / price) * 100 if price > 0 else 0
            
            # ================= TAMPILAN METRIK UTAMA =================
            col_a, col_b, col_c = st.columns(3)
            
            # Kartu 1: Skor LKH
            with col_a:
                if score is not None:
                    star_count = int(score // 20)
                    stars = '⭐' * star_count
                    
                    st.markdown(f"<div class='metric-card'>"
                                f"<h4>LKH Score</h4>"
                                f"<h2 style='color:#3498db;'>{score}/100</h2>"
                                f"<p>{stars}</p>"
                                f"</div>", unsafe_allow_html=True)
                    
                    if score >= 80:
                        st.success("✅ Sangat sesuai kriteria investasi LKH")
                    elif score >= 60:
                        st.warning("⚠️ Cukup sesuai, perlu analisis lebih lanjut")
                    else:
                        # Jika skor rendah karena data tidak lengkap
                        if (data.get("PER") is None or 
                            data.get("PBV") is None or 
                            data.get("ROE") is None or 
                            data.get("DER") is None):
                            st.error("❌ Data tidak lengkap untuk penilaian menyeluruh")
                        else:
                            st.error("❌ Tidak memenuhi standar minimal")
                else:
                    st.markdown(f"<div class='metric-card'>"
                                f"<h4>LKH Score</h4>"
                                f"<h2 style='color:#3498db;'>N/A</h2>"
                                f"<p>Data tidak tersedia</p>"
                                f"</div>", unsafe_allow_html=True)
                    st.error("❌ Data tidak tersedia untuk penilaian")
            
            # Kartu 2: Valuasi DCF
            with col_b:
                st.markdown(f"<div class='metric-card'>"
                            f"<h4>Nilai Intrinsik (DCF)</h4>"
                            f"<h2 style='color:#3498db;'>Rp {dcf_value:,.0f}</h2>"
                            f"<p>vs Harga: Rp {price:,.0f}</p>"
                            f"</div>", unsafe_allow_html=True)
                
                valuation_status = (
                    f"✅ Undervalued ({margin_safety:.1f}% margin safety)" 
                    if dcf_value > price 
                    else f"❌ Overvalued ({abs(margin_safety):.1f}% di atas nilai wajar)"
                )
                if dcf_value > price:
                    st.success(valuation_status)
                else:
                    st.error(valuation_status)
            
            # Kartu 3: Valuasi Relatif
            with col_c:
                st.markdown(f"<div class='metric-card'>"
                            f"<h4>Valuasi Relatif</h4>"
                            f"<p>PER: {data.get('PER', 0):.1f}</p>"
                            f"<p>PBV: {data.get('PBV', 0):.1f}</p>"
                            f"<p>DY: {data.get('dividend_yield', 0):.1f}%</p>"
                            f"</div>", unsafe_allow_html=True)
                
                valuation_comment = (
                    "ℹ️ Valuasi relatif menarik" 
                    if data.get("PER", 0) < 15 and data.get("PBV", 0) < 2 
                    else "ℹ️ Valuasi relatif tinggi"
                )
                st.info(valuation_comment)
            
            # ================= DETAIL FUNDAMENTAL =================
            if show_details:
                st.subheader("📋 Data Fundamental Detail")
                fund_cols = st.columns(4)
                
                with fund_cols[0]:
                    st.metric("ROE", f"{data.get('ROE', 0):.1f}%", f"{data.get('EPS_Growth', 0):.1f}% growth")
                    st.metric("Profit Margin", f"{data.get('profit_margin', 0):.1f}%")
                
                with fund_cols[1]:
                    der_value = data.get('DER')
                    if der_value is None:
                        der_value = 0.0  # Konversi None menjadi float 0.0
                        st.metric("DER", f"{der_value:.2f}", 
                        "Rendah" if der_value < 0.5 else "Tinggi")
                        current_ratio = data.get('current_ratio')
                        if current_ratio is None:
                           current_ratio = 0.0
                           st.metric("Current Ratio", f"{current_ratio:.1f}")
                
                with fund_cols[2]:
                    st.metric("Market Cap", f"Rp {data.get('market_cap', 0):,.0f}")
                    st.metric("Beta", f"{data.get('beta', 0):.2f}", 
                              "Risiko Rendah" if data.get('beta', 0) < 1 else "Risiko Tinggi")
                
                with fund_cols[3]:
                    fcf_value = data.get('FCF')
                    if fcf_value is None:
                        fcf_value = 0
                    st.metric("Free Cash Flow", f"Rp {fcf_value:,.0f}")

                    volume_value = data.get('volume')
                    if volume_value is None:
                       volume_value = 0
                    st.metric("Volume", f"{volume_value:,.0f}")
            
            # ================= ANALISIS SENSITIVITAS =================
            if show_sensitivity:
                st.subheader("📈 Analisis Sensitivitas DCF")
                
                with st.spinner("Menghitung sensitivitas..."):
                    try:
                        sensitivity = dcf_sensitivity_analysis(
                            base_fcf=fcf,
                            base_growth=default_growth/100,
                            base_discount=default_discount/100,
                            base_terminal=default_terminal/100,
                            years=analysis_years
                        )
                        
                        # Format hasil sensitivitas
                        growth_rates = [default_growth*0.7, default_growth, default_growth*1.3]
                        discount_rates = [default_discount*0.9, default_discount, default_discount*1.1]
                        
                        sens_matrix = np.zeros((3, 3))
                        for i, gr in enumerate(growth_rates):
                            for j, dr in enumerate(discount_rates):
                                key = f"Scenario_G{i+1}_DR{j+1}"
                                sens_matrix[i, j] = sensitivity.get(key, 0)
                        
                        # Tabel sensitivitas
                        sens_df = pd.DataFrame(
                            sens_matrix,
                            index=[f"Growth {gr:.1f}%" for gr in growth_rates],
                            columns=[f"Discount {dr:.1f}%" for dr in discount_rates]
                        )
                        
                        st.dataframe(
                            sens_df.style.format("{:,.0f}").background_gradient(cmap="RdYlGn"), 
                            use_container_width=True
                        )
                        st.caption("Heatmap Sensitivitas: Nilai Intrinsik (Rp)")
                    except Exception as e:
                        st.error(f"Gagal menghitung analisis sensitivitas: {str(e)}")
            
            # ================= VISUALISASI DATA =================
            st.subheader("📊 Tren Historis dan Proyeksi")
            
            # Data simulasi (di aplikasi nyata ambil dari API)
            current_year = datetime.now().year
            years = list(range(current_year-4, current_year+1))
            
            # Simulasi data historis
            eps_values = [100, 120, 110, 150, 180]
            fcf_values = [800, 950, 900, 1200, 1500]
            revenue = [3000, 3500, 3200, 4000, 4800]
            
            # Proyeksi masa depan
            projection_years = list(range(current_year+1, current_year+analysis_years+1))
            projection_eps = [eps_values[-1] * (1 + default_growth/100)**(i+1) for i in range(analysis_years)]
            projection_fcf = [fcf_values[-1] * (1 + default_growth/100)**(i+1) for i in range(analysis_years)]
            projection_revenue = [revenue[-1] * (1 + default_growth/100)**(i+1) for i in range(analysis_years)]
            
            # Gabungkan data
            all_years = years + projection_years
            all_eps = eps_values + projection_eps
            all_fcf = fcf_values + projection_fcf
            all_revenue = revenue + projection_revenue
            
            # Plot grafik
            try:
                plot_financial_chart(
                    years=all_years,
                    eps_values=all_eps,
                    fcf_values=all_fcf,
                    revenue_values=all_revenue
                )
            except Exception as e:
                st.error(f"Gagal menampilkan grafik: {str(e)}")
            
            # ================= REKOMENDASI INVESTASI =================
            st.subheader("📝 Rekomendasi Investasi")
            
            if score and score >= 80 and dcf_value > price and data.get("DER", 0) < 1:
                st.success("""
                **✅ REKOMENDASI BELI**
                - Memenuhi kriteria ketat investasi nilai (LKH)
                - Margin of safety yang cukup
                - Struktur keuangan sehat (DER rendah)
                """)
            elif score and score >= 60 and dcf_value > price * 1.1:
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
            error_msg = data.get("error", "Data tidak ditemukan") if data else "Data tidak ditemukan"
            st.error(f"❌ Gagal mengambil data: {error_msg}")
            st.info("Pastikan kode saham IDX sudah benar (contoh: BBCA, TLKM, ASII)")
    
    else:
        # Tampilan awal sebelum analisis
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
        
        # Contoh saham populer
        st.subheader("💡 Contoh Saham Populer")
        example_cols = st.columns(5)
        example_tickers = ["BBCA", "BBRI", "TLKM", "ASII", "UNVR"]
        
        for i, col in enumerate(example_cols):
            with col:
                if st.button(example_tickers[i], use_container_width=True, key=f"btn_{i}"):
                    st.session_state["current_ticker"] = example_tickers[i]
                    st.session_state["analysis_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.experimental_rerun()

        # Metodologi analisis
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

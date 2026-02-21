import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# ==========================================
# 1. SETUP & DESIGN (CODE-SYNTAX GRÜN)
# ==========================================
st.set_page_config(page_title="Stock Sniper PRO", layout="wide", page_icon="🎯")

# CODE-SYNTAX GRÜN: #7CE38B (Typisches String-Grün in Dark-Mode Editoren)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #cfd8dc; }
    
    /* Mobile-Optimierte Sidebar */
    .sidebar-metric { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #2d3239; font-size: 0.85rem; }
    .sidebar-label { color: #90a4ae; }
    /* HIER: Code-Syntax Grün für die Werte */
    .sidebar-value { font-weight: bold; color: #7CE38B; } 
    .risiko-legende { font-size: 0.75rem; color: #78909c; margin-top: 12px; line-height: 1.3; border-top: 1px solid #2d3239; padding-top: 8px; }
    
    /* Button im Code-Grün-Design */
    div.stButton > button:first-child { 
        background-color: #7CE38B; /* Syntax-Grüner Hintergrund */
        color: #0e1117; /* Dunkle Schrift für perfekten Kontrast */
        font-weight: bold; width: 100%; border: none; border-radius: 4px;
    }
    
    .info-box { background-color: #1c1f24; padding: 15px; border-left: 5px solid #7CE38B; margin-bottom: 10px; color: #cfd8dc;}
    .disclaimer { font-size: 0.8em; color: #546e7a; margin-top: 50px; border-top: 1px solid #2d3239; padding-top: 10px; }
    .stExpander { border: 1px solid #2d3239 !important; background-color: #1c1f24 !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. TICKER ENGINE (WIKI MIT FALLBACK-NETZ)
# ==========================================
@st.cache_data(ttl=86400)
def get_full_universe():
    tickers = []
    em_stocks = ["TSM", "BABA", "TCEHY", "MELI", "ASML", "PDD", "BIDU", "JD", "INFY", "VALE", "PBR", "SE", "CPNG", "NVO"]
    
    try:
        # 1. VERSUCH: Dynamischer Abruf
        sp5 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
        tickers.extend(sp5['Symbol'].tolist())
        dax = pd.read_html('https://en.wikipedia.org/wiki/DAX')[4]
        tickers.extend([t if t.endswith('.DE') else f"{t}.DE" for t in dax['Ticker symbol'].tolist()])
        tickers.extend(em_stocks)
    except:
        # 2. FALLBACK: Wird NUR genutzt, wenn Wiki fehlschlägt (Vollständige harte Liste)
        backup_sp500 = [
            "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "BRK-B", "JPM", "UNH", "JNJ", "V", "XOM", "PG", "MA", 
            "HD", "CVX", "ABBV", "LLY", "MRK", "PEP", "KO", "AVGO", "BAC", "TMO", "COST", "MCD", "CSCO", "WMT", "CRM", 
            "ABT", "DHR", "LIN", "ACN", "PFE", "NKE", "CMCSA", "ADBE", "TXN", "VZ", "UPS", "PM", "NEE", "RTX", "MS", 
            "HON", "INTC", "BMY", "ORCL", "BA", "QCOM", "LMT", "UNP", "IBM", "AMD", "SPGI", "GS", "GE", "INTU", "DE", 
            "NOW", "CAT", "PLD", "AMAT", "EL", "ISRG", "T", "BLK", "MDLZ", "BKNG", "SYK", "TJX", "GILD", "C", "ADI", 
            "AXP", "ZTS", "MDT", "SBUX", "CB", "LRCX", "MMC", "AMT", "SCHW", "VRTX", "BDX", "CI", "MO", "CVS", "GPN", 
            "PNC", "TGT", "SO", "BSX", "ITW", "SLB", "EQIX", "DUK", "EOG", "AON", "CL", "APD", "PYPL", "KMB", "NOC", 
            "WM", "FCX", "AEP", "CSX", "ICE", "MCK", "MCO", "CDW", "FDX", "SHW", "PSA", "ORLY", "TFC", "EMR", "VLO", 
            "NXPI", "ROP", "MAR", "ETN", "MPC", "F", "KLAC", "PGR", "NSC", "PH", "PCAR", "CMG", "SNPS", "OXY", "HCA", 
            "TRV", "ADSK", "CTAS", "MNST", "TT", "TEL", "WMB", "AIG", "MSI", "YUM", "HLT", "AFL", "ROST", "NUE", "WELL", 
            "DHI", "KMI", "SPG", "O", "PAYX", "AZO", "IQV", "DXCM", "STZ", "MTD", "KDP", "EA", "A", "CTSH", "GWW", 
            "MCHP", "SRE", "CARR", "NEM", "EXC", "CTVA", "BIIB", "WBA", "ON", "HAL", "K", "DD", "RMD", "VRSK", "BKR", 
            "ED", "PPG", "PEG", "FAST", "AWK", "ALB", "EXR", "DLTR", "FANG", "WEC", "FITB", "ROK", "GPC", "ECL", "FTV", 
            "DLR", "EFX", "VRSN", "ZBH", "ODFL", "WST", "BBY", "CAH", "CBRE", "KHC", "ES", "TSCO", "GLW", "CPRT", "FMC", 
            "VMC", "CDNS", "RSG", "ANET", "ANSS", "XYL", "KEYS", "STE", "WTW", "CHD", "HIG", "CINF", "NTRS", "DOV", 
            "NTAP", "STX", "PTC", "CBOE", "RF", "FDS", "EXPD", "CF", "BXP", "PFG", "LNT", "MAS", "MRO", "PPL", "CMS", 
            "CMA", "NDSN", "KEY", "HBAN", "AES", "CFG", "SYF", "DPZ", "MGM", "SJM", "LUV", "WRK", "HPE", "TAP", "MOS", 
            "TPR", "AAL", "NI", "NRG", "IP", "PNW", "BEN", "CNP", "KIM", "CPB", "JNPR", "WHR", "HRL", "MHK", "UHS", 
            "RHI", "AEE", "EVRG", "HST", "PNR", "ATO", "NCLH", "SEE", "VFC", "NWL", "DISH", "ALK"
        ]
        backup_dax = [
            "ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BEI.DE", "BMW.DE", "BNR.DE", "CBK.DE", "CON.DE", 
            "1COV.DE", "DTG.DE", "DTE.DE", "DB1.DE", "DBK.DE", "DPW.DE", "DHL.DE", "ENR.DE", "EOAN.DE", "FRE.DE", 
            "FME.DE", "HNR1.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "MBG.DE", "MTX.DE", "MUV2.DE", "PAH3.DE", "PUM.DE", 
            "QIA.DE", "RHM.DE", "RWE.DE", "SAP.DE", "SRT3.DE", "SIE.DE", "SY1.DE", "VOW3.DE", "VNA.DE", "ZAL.DE"
        ]
        tickers = backup_sp500 + backup_dax + em_stocks

    return sorted(list(set([t.replace('.', '-') if ('.DE' not in t and '.' in t) else t for t in tickers])))

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ==========================================
# 3. SIDEBAR (FINAL & SYNTAX-GRÜN)
# ==========================================
with st.sidebar:
    st.title("🎯 Sniper Settings")
    min_marge = st.slider("Min. Marge %", 0, 50, 12)
    min_roe = st.slider("Min. ROE %", 0, 50, 15)
    
    st.divider()
    st.markdown("### 🛡️ Makro Risiko-Radar")
    try:
        vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
        t10y = yf.Ticker("^TNX").history(period="1d")['Close'].iloc[-1]
        t2y = yf.Ticker("^IRX").history(period="1d")['Close'].iloc[-1]
        gold_h = yf.Ticker("GC=F").history(period="5d")
        gold_ch = ((gold_h['Close'].iloc[-1] / gold_h['Close'].iloc[0]) - 1) * 100
        oil_h = yf.Ticker("CL=F").history(period="5d")
        oil_ch = ((oil_h['Close'].iloc[-1] / oil_h['Close'].iloc[0]) - 1) * 100

        m_score = 0
        if t10y < t2y: m_score += 40
        if vix > 30: m_score += 30
        if oil_ch > 5: m_score += 20
        if gold_ch > 3: m_score += 10

        st.markdown(f"""
            <div class="sidebar-metric"><span class="sidebar-label">VIX (Panik)</span><span class="sidebar-value">{vix:.2f}</span></div>
            <div class="sidebar-metric"><span class="sidebar-label">10J Zins US</span><span class="sidebar-value">{t10y:.2f}%</span></div>
            <div class="sidebar-metric"><span class="sidebar-label">Gold (5T %)</span><span class="sidebar-value">{gold_ch:+.1f}%</span></div>
            <div class="sidebar-metric"><span class="sidebar-label">Öl WTI (5T %)</span><span class="sidebar-value">{oil_ch:+.1f}%</span></div>
            <div class="sidebar-metric"><span class="sidebar-label">Zinskurve</span><span class="sidebar-value">{'⚠️ INV' if t10y < t2y else 'Normal'}</span></div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        if m_score >= 40: st.error(f"EINSTUFUNG: HOCH ({m_score})")
        elif m_score >= 15: st.warning(f"EINSTUFUNG: MITTEL ({m_score})")
        else: st.success(f"EINSTUFUNG: NIEDRIG ({m_score})")
        
        st.markdown("""<div class="risiko-legende"><b>Risiko-Bereiche:</b><br>🟢 0-14: Niedrig (Markt stabil)<br>🟡 15-39: Mittel (Erhöhte Volatilität)<br>🔴 40+: Hoch (Vorsicht/Absicherung)</div>""", unsafe_allow_html=True)
    except: st.write("Makro-Daten aktuell nicht verfügbar.")

# ==========================================
# 4. HAUPTSEITE & VOLLSTÄNDIGE LEGENDE
# ==========================================
st.title("Gemini Stock Sniper PRO")

with st.expander("📖 Strategie-Guide & Agenda (Kennzahlen-Erklärung)", expanded=True):
    t_mak, t_tra, t_inv = st.tabs(["🌍 Makro-Einstufung", "📈 Trading-Signale", "💎 Invest-Rating"])
    with t_mak:
        st.markdown("""
        **Makro-Score Berechnung:**
        - **Zinskurve (+40):** Inversion (10J < 3M) signalisiert Rezessionsgefahr.
        - **VIX (>30):** Panik-Indikator (+30 Punkte).
        - **Öl-Preis (>5%):** Preisschock (+20 Punkte).
        - **Gold (>3%):** Kapitalflucht (+10 Punkte).
        """)
    with t_tra:
        st.markdown("""
        **Handels-Signale (Timing):**
        - **PULLBACK:** Aktie ist im Aufwärtstrend (Kurs > SMA 200) + RSI (30-60) zeigt Abkühlung.
        - **Kauf-Limit (SMA 200):** Wichtigste technische Unterstützungslinie.
        - **Trade_Score:** 100 = Perfekter Einstieg (Direkt am SMA 200 bei niedrigem RSI).
        """)
    with t_inv:
        st.markdown("""
        **Qualitäts-Einstufung (Langfristig):**
        - **Invest_Score:** Produkt aus (Operative Marge * Eigenkapitalrendite) / 100.
        - **Marge % / ROE %:** Profitabilität und Kapitaleffizienz.
        - *Hinweis:* Filtert nach deinen Sidebar-Vorgaben.
        """)

# ==========================================
# 5. SCANNER
# ==========================================
if st.button("🚀 VOLLSTÄNDIGEN MARKT-SCAN STARTEN"):
    universe = get_full_universe()
    results = []
    prog = st.progress(0, text=f"Scan von {len(universe)} Titeln...")
    
    for i, t in enumerate(universe):
        try:
            s = yf.Ticker(t)
            h = s.history(period="1y")
            if len(h) < 200: continue
            
            cp = h['Close'].iloc[-1]
            sma200 = h['Close'].rolling(200).mean().iloc[-1]
            rsi = calculate_rsi(h).iloc[-1]
            dist = (cp / sma200) - 1
            
            inf = s.info
            marge = (inf.get('operatingMargins', 0) or 0) * 100
            roe = (inf.get('returnOnEquity', 0) or 0) * 100
            
            # Trading & Invest Logik
            status, trade_score, invest_score = "---", 0, 0
            if cp > sma200 and 30 <= rsi <= 60:
                trade_score = (1 - min(dist, 0.15)/0.15) * 70 + (1 - abs(rsi-45)/45) * 30
                status = "PULLBACK"
            
            if marge >= min_marge and roe >= min_roe:
                invest_score = (marge * roe) / 100

            results.append({
                "Ticker": t, "Name": inf.get('shortName', t)[:15], "Status": status,
                "Preis": round(cp, 2), "Kauf-Limit (200er)": round(sma200, 2), "Abst.%": round(dist*100, 1),
                "RSI": round(rsi, 1), "Trade_S.": int(trade_score), "Invest_S.": round(invest_score, 1),
                "Marge%": round(marge, 1), "ROE%": round(roe, 1)
            })
        except: continue
        prog.progress((i+1)/len(universe))

    if results:
        df = pd.DataFrame(results)
        t1, t2, t3 = st.tabs(["📈 Trading", "💎 Investing", "📊 Alle Daten"])
        with t1: st.dataframe(df[df['Status'] == "PULLBACK"].sort_values("Trade_S.", ascending=False), hide_index=True, use_container_width=True)
        with t2: st.dataframe(df[df['Invest_S.'] > 0].sort_values("Invest_S.", ascending=False), hide_index=True, use_container_width=True)
        with t3: st.dataframe(df, use_container_width=True)
        st.markdown('<div class="disclaimer">⚠️ Keine Anlageberatung. Alle Daten ohne Gewähr.</div>', unsafe_allow_html=True)
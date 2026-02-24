import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import io

# ==========================================
# VERSION 4.2 (LEGENDE CONSISTENT SPACING FIX)
# ==========================================

st.set_page_config(page_title="Gemini Stock Sniper PRO v4.2", layout="wide", page_icon="🎯")

# DESIGN (OPTIMIERT FÜR MAXIMALE KOMPAKTHEIT IN DER SIDEBAR & HEADER NACH OBEN)
st.markdown("""
    <style>
    /* Hauptcontainer nach oben schieben */
    .block-container { padding-top: 1.5rem !important; }
    
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background-color: #0e1117 !important; }
    [data-testid="stSidebar"] { background-color: #161a22 !important; width: 300px !important; }
    .stApp, p, label, h1, h2, h3, span { color: #cfd8dc !important; }
    div.stButton > button:first-child { 
        background-color: #89abe3 !important; color: #0e1117 !important; 
        font-weight: bold !important; width: 100% !important; border-radius: 6px !important;
    }
    
    /* Ultradünne Sidebar Metriken */
    .sidebar-metric { 
        display: flex; justify-content: space-between; 
        padding: 1px 0; border-bottom: 1px solid #2d3239; 
        font-size: 0.75rem; line-height: 1.1;
    }
    .sidebar-label { color: #90a4ae !important; }
    .sidebar-value { font-weight: bold; color: #89abe3 !important; } 
    
    /* Ultradünne Header in der Sidebar */
    .reg-header { 
        font-size: 0.75rem; font-weight: bold; color: #89abe3; 
        margin-top: 8px; margin-bottom: 2px;
        text-transform: uppercase; border-left: 2px solid #89abe3; padding-left: 6px; 
    }
    
    /* EIGENE, EXTREM KOMPAKTE STATUS-BOXEN (Ersetzt st.success etc.) */
    .status-box {
        padding: 3px 6px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: bold;
        text-align: left;
        margin-top: 2px;
        margin-bottom: 6px;
    }
    .success-box { background-color: #122b1c; color: #a8d5ba; border: 1px solid #1e452c; }
    .warning-box { background-color: #3b2b0f; color: #ffe082; border: 1px solid #5c4317; }
    .error-box { background-color: #3b1515; color: #ffbaba; border: 1px solid #5c2121; }
    .info-box { background-color: #12253b; color: #89abe3; border: 1px solid #1e3d61; }
    
    /* Expander und Tabs */
    .stExpander { background-color: #161a22 !important; border: 1px solid #2d3239 !important; border-radius: 8px !important; }
    [data-testid="stExpanderDetails"] { background-color: #161a22 !important; }
    .stExpander summary { background-color: #161a22 !important; color: #89abe3 !important; font-weight: bold !important; }
    .stTabs [aria-selected="true"] { color: #89abe3 !important; border-bottom-color: #89abe3 !important; }
    
    /* ---- NEU: Konsistentes und sanftes Spacing für Aufzählungen in der Legende ---- */
    [data-testid="stExpanderDetails"] ul { margin-top: 0.2rem; }
    [data-testid="stExpanderDetails"] li { margin-bottom: 0.4rem; }
    
    /* Slider noch kompakter machen */
    div[data-testid="stSlider"] { margin-bottom: -20px !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. TICKER ENGINE (FULL HARDCODED BACKUP LIST)
# ==========================================
@st.cache_data(ttl=86400)
def get_full_universe():
    em_list = ["TSM", "BABA", "TCEHY", "MELI", "ASML", "PDD", "BIDU", "JD", "INFY", "VALE", "PBR", "SE", "CPNG", "NVO"]
    dax_list = ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BEI.DE", "BMW.DE", "CON.DE", "1COV.DE", "DTG.DE", "DTE.DE", "DBK.DE", "DB1.DE", "DHL.DE", "EON.DE", "FRE.DE", "HNR1.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "MBG.DE", "MRK.DE", "MTX.DE", "MUV2.DE", "PUM.DE", "RWE.DE", "SAP.DE", "SRT3.DE", "SIE.DE", "SY1.DE", "VOW3.DE", "VNA.DE"]
    sp500_full = ["AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "BRK-B", "JPM", "UNH", "V", "XOM", "MA", "PG", "HD", "CVX", "ABBV", "LLY", "MRK", "PEP", "KO", "AVGO", "BAC", "TMO", "COST", "CSCO", "MCD", "WMT", "CRM", "ABT", "DHR", "LIN", "ACN", "TXN", "VZ", "UPS", "PM", "NEE", "RTX", "MS", "HON", "INTC", "BMY", "ORCL", "BA", "QCOM", "LMT", "UNP", "IBM", "AMD", "GS", "GE", "CAT", "INTU", "DE", "NOW", "PLD", "AMAT", "EL", "ISRG", "T", "BLK", "BKNG", "MDLZ", "GILD", "SYK", "TJX", "ADI", "C", "AXP", "ZTS", "MDT", "SBUX", "CB", "LRCX", "MMC", "AMT", "SCHW", "VRTX", "BDX", "CI", "MO", "CVS", "PNC", "TGT", "SO", "BSX", "ITW", "SLB", "EQIX", "DUK", "EOG", "AON", "CL", "APD", "PYPL", "KMB", "NOC", "WM", "FCX", "AEP", "CSX", "ICE", "MCK", "MCO", "FDX", "SHW", "PSA", "ORLY", "EMR", "VLO", "USB", "MPC", "MAR", "PH", "HCA", "GD", "ADSK", "ECL", "MNST", "MCHP", "AJG", "NSC", "MSI", "PSX", "ORCL", "TRV", "D", "SNPS", "ROP", "CARR", "DXCM", "STZ", "A", "MET", "FIS", "CMG", "CPRT", "TEL", "DLR", "CDNS", "O", "MPWR", "WELL", "IQV", "GPN", "EW", "KHC", "MOLN", "PRU", "IDXX", "VRSK", "DOW", "KEE", "DHI", "PAYX", "HPQ", "VICI", "ANET", "FAST", "EXC", "F", "DFS", "CTAS", "AZO", "AME", "KR", "ROK", "LEN", "VMC", "GEHC", "ALGN", "CE", "CMI", "BBY", "BKR", "K", "LHX", "KMI", "WBD", "KVUE", "SYY", "STT", "HWM", "FITB", "MTB", "EFX", "EBAY", "FTV", "DLTR", "HIG", "WY", "TSCO", "HBAN", "ON", "NUE", "EXR", "GLW", "WDC", "PPG", "MRO", "RCL", "WST", "STX", "KEY", "TRGP", "ED", "CAH", "EQT", "FANG", "HAL", "NDAQ", "AWK", "LYB", "PCG", "KEYS", "XYL", "AVB", "VTR", "ATO", "FE", "ES", "IRM", "TYL", "GRMN", "RF", "BRO", "INVH", "WAT", "TDY", "LDOS", "AKAM", "STE", "POOL", "TER", "BXP", "WRB", "MOH", "COO", "IPG", "DRI", "ZBRA", "SWK", "DG", "DPZ", "EPAM", "TRMB", "HAS", "CHRW", "GEN", "PARA", "CZR", "MKTX", "IVZ", "BEN", "BWA", "RL", "FOXA", "FOX", "FMC", "NCLH", "MHK", "FRT", "LNC", "BIO", "NWL"]

    try:
        sp5 = pd.read_html(io.StringIO(requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies').text))[0]
        tickers = sp5['Symbol'].tolist()
        dax_wiki = pd.read_html(io.StringIO(requests.get('https://en.wikipedia.org/wiki/DAX').text))[4]
        tickers.extend([f"{t.split('.')[0]}.DE" for t in dax_wiki['Ticker symbol'].tolist()])
        tickers.extend(em_list)
    except:
        tickers = sp500_full + dax_list + em_list
        
    return sorted(list(set([t.replace('.', '-') if (".DE" not in t and "." in t) else t for t in tickers])))

# ==========================================
# 3. AUTONOME MAKRO ABFRAGE
# ==========================================
@st.cache_data(ttl=43200)
def get_live_macro_data():
    data = {"PMI_USA": 51.2, "PMI_DAX": 50.7, "PMI_EM": 52.0, "ZEW_EU": 58.3}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
    
    try:
        url_pmi = "https://tradingeconomics.com/country-list/manufacturing-pmi"
        res_pmi = requests.get(url_pmi, headers=headers, timeout=5)
        if res_pmi.status_code == 200:
            df_pmi = pd.read_html(io.StringIO(res_pmi.text))[0].set_index('Country')
            if 'United States' in df_pmi.index: data['PMI_USA'] = float(df_pmi.loc['United States', 'Last'])
            if 'Germany' in df_pmi.index: data['PMI_DAX'] = float(df_pmi.loc['Germany', 'Last'])
            
            em_weights = {'China': 0.347, 'India': 0.208, 'Taiwan': 0.208, 'South Korea': 0.167, 'Brazil': 0.069}
            em_val, w_sum = 0, 0
            for c, w in em_weights.items():
                if c in df_pmi.index:
                    em_val += float(df_pmi.loc[c, 'Last']) * w
                    w_sum += w
            if w_sum > 0: data['PMI_EM'] = round(em_val / w_sum, 1)
    except: pass
    
    try:
        url_zew = "https://tradingeconomics.com/country-list/zew-economic-sentiment-index"
        res_zew = requests.get(url_zew, headers=headers, timeout=5)
        if res_zew.status_code == 200:
            df_zew = pd.read_html(io.StringIO(res_zew.text))[0].set_index('Country')
            if 'Germany' in df_zew.index:
                data['ZEW_EU'] = float(df_zew.loc['Germany', 'Last'])
    except: pass

    return data

# ==========================================
# 4. SIDEBAR (MARKTEINSTUFUNG)
# ==========================================
with st.sidebar:
    st.title("🎯 Sniper v4.2")
    min_marge = st.slider("Min. Marge %", 0, 50, 12)
    min_roe = st.slider("Min. ROE %", 0, 50, 15)
    
    # Ultradünner Divider statt st.divider()
    st.markdown('<hr style="margin: 10px 0; border: none; border-top: 1px solid #2d3239;">', unsafe_allow_html=True)
    st.markdown("### 🛡️ Markteinstufung")
    
    macro_data = get_live_macro_data()
    
    def get_val(ticker):
        try:
            d = yf.Ticker(ticker).history(period="5d")
            return d['Close'].iloc[-1] if not d.empty else None
        except: return None

    def get_vdax_robust():
        for t in ["V1X.DE", "^V1X", "^VDAX"]:
            try:
                d = yf.Ticker(t).history(period="5d")
                if not d.empty: return d['Close'].iloc[-1]
            except: continue
        try:
            url = "https://www.finanzen.net/index/vdax_new"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            res = requests.get(url, headers=headers, timeout=5)
            dfs = pd.read_html(io.StringIO(res.text), decimal=',', thousands='.')
            for df in dfs:
                if 'Schluss' in df.columns and not df.empty:
                    return float(df['Schluss'].iloc[0])
        except: pass
        return 18.14

    # USA
    st.markdown('<div class="reg-header">🇺🇸 USA</div>', unsafe_allow_html=True)
    vix = get_val("^VIX")
    vix_val = f"{vix:.2f}" if vix else "N/A"
    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">VIX (Angst)</span><span class="sidebar-value">{vix_val}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">PMI (Wirtschaft)</span><span class="sidebar-value">{macro_data["PMI_USA"]:.1f}</span></div>', unsafe_allow_html=True)
    
    if vix:
        if vix < 20: st.markdown('<div class="status-box success-box">US-Markt: Stabil</div>', unsafe_allow_html=True)
        elif 20 <= vix <= 30: st.markdown('<div class="status-box warning-box">US-Markt: Nervös</div>', unsafe_allow_html=True)
        else: st.markdown('<div class="status-box error-box">US-Markt: Panik</div>', unsafe_allow_html=True)
    
    # EUROPA (DAX)
    st.markdown('<div class="reg-header">🇪🇺 Europa (DAX)</div>', unsafe_allow_html=True)
    
    vdax = get_vdax_robust()
    vdax_val = f"{vdax:.2f}"
    
    pmi_dax = macro_data["PMI_DAX"]
    zew_eu = macro_data["ZEW_EU"]

    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">VDAX</span><span class="sidebar-value">{vdax_val}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">PMI (Wirtschaft)</span><span class="sidebar-value">{pmi_dax:.1f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">ZEW (Erwartung)</span><span class="sidebar-value">{zew_eu:.1f}</span></div>', unsafe_allow_html=True)

    if vdax:
        if vdax < 20: st.markdown('<div class="status-box success-box">EU-Markt: Stabil</div>', unsafe_allow_html=True)
        elif 20 <= vdax <= 30: st.markdown('<div class="status-box warning-box">EU-Markt: Nervös</div>', unsafe_allow_html=True)
        else: st.markdown('<div class="status-box error-box">EU-Markt: Panik</div>', unsafe_allow_html=True)


    # EMERGING MARKETS
    st.markdown('<div class="reg-header">🌏 Emerging Markets</div>', unsafe_allow_html=True)
    dxy = get_val("DX-Y.NYB")
    dxy_val = f"{dxy:.2f}" if dxy else "N/A"
    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">DXY (Dollar)</span><span class="sidebar-value">{dxy_val}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">PMI (EM Gewicht.)</span><span class="sidebar-value">{macro_data["PMI_EM"]:.1f}</span></div>', unsafe_allow_html=True)
    
    if dxy:
        if dxy < 102: st.markdown('<div class="status-box success-box">EM-Markt: Günstig</div>', unsafe_allow_html=True)
        elif 102 <= dxy <= 105: st.markdown('<div class="status-box warning-box">EM-Markt: Belastet</div>', unsafe_allow_html=True)
        else: st.markdown('<div class="status-box error-box">EM-Markt: Risiko</div>', unsafe_allow_html=True)

    # ROHSTOFFE & ZINSEN
    st.markdown('<div class="reg-header">📈 Zinsen & Rohstoffe</div>', unsafe_allow_html=True)
    tnx = get_val("^TNX")     
    t2y = get_val("^IRX")     
    gold = get_val("GC=F")
    oil = get_val("CL=F")
    
    tnx_val = f"{tnx:.2f}%" if tnx else "N/A"
    gold_val = f"{gold:,.2f}" if gold else "N/A"
    oil_val = f"{oil:.2f}" if oil else "N/A"
    
    zins_status = "N/A"
    if tnx and t2y:
        zins_status = "⚠️ Invers" if tnx < t2y else "✅ Normal"
        
    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">US 10J Zins</span><span class="sidebar-value">{tnx_val}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">Zinskurve (10J/3M)</span><span class="sidebar-value">{zins_status}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">Gold (USD)</span><span class="sidebar-value">{gold_val}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">Öl WTI (USD)</span><span class="sidebar-value">{oil_val}</span></div>', unsafe_allow_html=True)

# ==========================================
# 5. HAUPTSEITE & VOLLSTÄNDIGE AGENDA
# ==========================================
st.title("Gemini Stock Sniper PRO v4.2")

# Space zwischen Header und Legend
st.markdown("<br>", unsafe_allow_html=True)

with st.expander("📖 Strategie-Guide & Agenda", expanded=True):
    t1, t2, t3 = st.tabs(["🌍 Makro Phasen", "📈 Trading Kennzahlen", "💎 Invest Kennzahlen"])
    
    with t1:
        # Alles in EINEM Markdown-Block mit <br> für exakte Zeilenabstände
        st.markdown("""
        **Markteinstufungs-Logik:**
        - **USA (VIX):** < 20 = Stabil, 20-30 = Nervös, > 30 = Panik.
        - **Europa (VDAX):** Das deutsche Angstbarometer (WKN: A0DMX9). < 20 = Stabil, 20-30 = Nervös, > 30 = Panik.
        - **Einkaufsmanagerindizes (PMI):** Der wichtigste Konjunkturindikator für die Realwirtschaft (USA, DAX/HCOB, EM). **> 50:** Wirtschaft wächst. **< 50:** Wirtschaft schrumpft.
        - **ZEW (Konjunkturerwartung DAX):** Spiegelt die Stimmung der institutionellen Anleger wider. **Regel:<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**✅ ZEW > PMI** ➔ Optimisten in der Überzahl.<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**⚠️ ZEW < PMI** ➔ Pessimisten dominieren.
        - **DXY (US-Dollar Index):** Misst die Stärke des US-Dollars gegen andere Leitwährungen (Basiswert 100). Er ist der Taktgeber für die Emerging Markets.<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**✅ < 100:** Schwacher Dollar. Positiv für Schwellenländer, da deren Kredite günstiger werden und Kapital dorthin fließt.<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**⚖️ 100 - 105:** Normales bis belastendes Niveau.<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**⚠️ > 105:** Starker Dollar. Kritisch (Risiko), da es Kapital aus den Schwellenländern in die USA absaugt.
        - **Zinskurve (10J/3M):** Vergleicht langfristige (10 Jahre) mit kurzfristigen (3 Monate) US-Staatsanleihen.<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**✅ Normal:** 10J-Zinsen > 3M-Zinsen. Der gesunde Wirtschaftszustand (Lange Bindung = mehr Zinsen).<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**⚠️ Invers:** 3M-Zinsen > 10J-Zinsen. Ein klassisches Rezessions-Warnsignal. Der Markt preist schwere Zeiten ein.
        - **Rohstoffe:** Gold steigt bei Angst; Öl ist ein wichtiger Inflations-Treiber.
        """, unsafe_allow_html=True)
        
    with t2:
        st.markdown("""
        **Trading Pullback Logik:**
        - **SMA 200 (Kauf-Limit):** Langfristiger Aufwärtstrend. Wir kaufen nur, wenn der Preis über dem Durchschnitt der letzten 200 Tage liegt.
        - **RSI (Relative Stärke):** Wert zwischen 30 und 60 gesucht. Wir wollen keine überkauften Aktien, sondern gesunde Rücksetzer.
        - **Kauf-/Verkaufssignal:** Ein Pullback-Signal entsteht bei einer Korrektur im intakten Aufwärtstrend.
        - **Trade_Score:** Bewertung der Einstiegs-Qualität (Nähe zum SMA 200 + optimales RSI-Level).
        """)
        
    with t3:
        st.markdown("""
        **Invest-Rating (Qualität):**
        - **Operative Marge (>12%):** Zeigt die Preismacht. Wie viel Gewinn bleibt pro Euro Umsatz hängen?
        - **ROE (>15%):** Eigenkapitalrendite. Wie effizient arbeitet das Kapital der Aktionäre?
        - **Invest_Score:** Produkt aus Marge & ROE. Höhere Werte signalisieren exzellente Business-Qualität (Gedeckelt bei 100).
        """)
        
# ==========================================
# 6. SCANNER (UNBERÜHRT)
# ==========================================
if st.button("🚀 VOLLSTÄNDIGEN MARKT-SCAN STARTEN"):
    universe = get_full_universe()
    results = []
    prog = st.progress(0, text="Sniper scannt...")
    for i, t in enumerate(universe):
        try:
            s = yf.Ticker(t); h = s.history(period="1y")
            if len(h) < 200: continue
            cp = h['Close'].iloc[-1]; sma200 = h['Close'].rolling(200).mean().iloc[-1]
            delta = h['Close'].diff(); g = (delta.where(delta > 0, 0)).rolling(14).mean(); l = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (g / l))).iloc[-1]
            inf = s.info; marge = (inf.get('operatingMargins', 0) or 0) * 100; roe = (inf.get('returnOnEquity', 0) or 0) * 100
            status = "PULLBACK" if (cp > sma200 and 30 <= rsi <= 60) else "---"
            invest_score = min(100.0, (marge * roe) / 100) if (marge >= min_marge and roe >= min_roe) else 0
            results.append({"Ticker": t, "Name": inf.get('shortName', t)[:15], "Status": status, "Preis": round(cp, 2), "Limit (SMA)": round(sma200, 2), "RSI": round(rsi, 1), "Trade_S.": int((1 - min((cp/sma200-1), 0.15)/0.15) * 100) if status=="PULLBACK" else 0, "Invest_S.": round(invest_score, 1), "Marge%": round(marge, 1), "ROE%": round(roe, 1)})
        except: continue
        prog.progress((i+1)/len(universe))
    if results:
        df = pd.DataFrame(results)
        t_tr, t_inv = st.tabs(["📈 Trading", "💎 Investing"])
        with t_tr: st.dataframe(df[df['Status'] == "PULLBACK"].sort_values("Trade_S.", ascending=False), hide_index=True, use_container_width=True)
        with t_inv: st.dataframe(df[df['Invest_S.'] > 0].sort_values("Invest_S.", ascending=False), hide_index=True, use_container_width=True)
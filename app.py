import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import io
import re
import cloudscraper
import os
import shutil
import json

# ==========================================
# VERSION 5.17 (UPDATED COMMODITY LEGEND)
# ==========================================

AV_KEY = "WB048V1B735CQQUN" # Dein persönlicher API Key

st.set_page_config(page_title="Gemini Stock Sniper PRO v5.17", layout="wide", page_icon="🎯")

# ==========================================
# 1. DESIGN
# ==========================================
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; }
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background-color: #0e1117 !important; }
    [data-testid="stSidebar"] { background-color: #161a22 !important; width: 300px !important; }
    .stApp, p, label, h1, h2, h3, span, a { color: #cfd8dc !important; }
    div.stButton > button:first-child { 
        background-color: #89abe3 !important; color: #0e1117 !important; 
        font-weight: bold !important; width: 100% !important; border-radius: 6px !important;
    }
    .sidebar-metric { display: flex; justify-content: space-between; padding: 1px 0; border-bottom: 1px solid #2d3239; font-size: 0.75rem; line-height: 1.1; }
    .sidebar-label { color: #90a4ae !important; }
    .sidebar-value { font-weight: bold; color: #89abe3 !important; } 
    .reg-header { font-size: 0.75rem; font-weight: bold; color: #89abe3; margin-top: 8px; margin-bottom: 2px; text-transform: uppercase; border-left: 2px solid #89abe3; padding-left: 6px; }
    .status-box { padding: 3px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; text-align: left; margin-top: 2px; margin-bottom: 6px; }
    .success-box { background-color: #122b1c; color: #a8d5ba; border: 1px solid #1e452c; }
    .warning-box { background-color: #3b2b0f; color: #ffe082; border: 1px solid #5c4317; }
    .error-box { background-color: #3b1515; color: #ffbaba; border: 1px solid #5c2121; }
    .info-box { background-color: #12253b; color: #89abe3; border: 1px solid #1e3d61; }
    
    /* Expander Design */
    .stExpander { background-color: #161a22 !important; border: 1px solid #2d3239 !important; border-radius: 8px !important; }
    [data-testid="stExpanderDetails"] { background-color: #161a22 !important; }
    .stExpander summary { background-color: #161a22 !important; color: #89abe3 !important; font-weight: bold !important; }
    .stExpander summary p { font-size: 0.75rem !important; }
    
    /* Kompakte Inputs */
    div[data-testid="stNumberInput"] label p { font-size: 0.7rem !important; margin-bottom: -5px !important; }
    div[data-testid="stNumberInput"] div[data-baseweb="input"] { height: 28px !important; min-height: 28px !important; border-radius: 4px !important; }
    div[data-testid="stNumberInput"] input { padding: 2px 6px !important; font-size: 0.75rem !important; }
    
    .stTabs [aria-selected="true"] { color: #89abe3 !important; border-bottom-color: #89abe3 !important; }
    [data-testid="stExpanderDetails"] ul { margin-top: 0.2rem; }
    [data-testid="stExpanderDetails"] li { margin-bottom: 0.4rem; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. TICKER ENGINE
# ==========================================
@st.cache_data(ttl=86400)
def get_full_universe():
    em_list = ["TSM", "BABA", "TCEHY", "MELI", "ASML", "PDD", "BIDU", "JD", "INFY", "VALE", "PBR", "SE", "CPNG", "NVO"]
    dax_list = ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BEI.DE", "BMW.DE", "CON.DE", "1COV.DE", "DTG.DE", "DTE.DE", "DBK.DE", "DB1.DE", "DHL.DE", "EON.DE", "FRE.DE", "HNR1.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "MBG.DE", "MRK.DE", "MTX.DE", "MUV2.DE", "PUM.DE", "RWE.DE", "SAP.DE", "SRT3.DE", "SIE.DE", "SY1.DE", "VOW3.DE", "VNA.DE"]
    sp500_full = ["AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "BRK-B", "JPM", "UNH", "V", "XOM", "MA", "PG", "HD", "CVX", "ABBV", "LLY", "MRK", "PEP", "KO", "AVGO", "BAC", "TMO", "COST", "CSCO", "MCD", "WMT", "CRM", "ABT", "DHR", "LIN", "ACN", "TXN", "VZ", "UPS", "PM", "NEE", "RTX", "MS", "HON", "INTC", "BMY", "ORCL", "BA", "QCOM", "LMT", "UNP", "IBM", "AMD", "GS", "GE", "CAT", "INTU", "DE", "NOW", "PLD", "AMAT", "EL", "ISRG", "T", "BLK", "BKNG", "MDLZ", "GILD", "SYK", "TJX", "ADI", "C", "AXP", "ZTS", "MDT", "SBUX", "CB", "LRCX", "MMC", "AMT", "SCHW", "VRTX", "BDX", "CI", "MO", "CVS", "PNC", "TGT", "SO", "BSX", "ITW", "SLB", "EQIX", "DUK", "EOG", "AON", "CL", "APD", "PYPL", "KMB", "NOC", "WM", "FCX", "AEP", "CSX", "ICE", "MCK", "MCO", "FDX", "SHW", "PSA", "ORLY", "EMR", "VLO", "USB", "MPC", "MAR", "PH", "HCA", "GD", "ADSK", "ECL", "MNST", "MCHP", "AJG", "NSC", "MSI", "PSX", "ORCL", "TRV", "D", "SNPS", "ROP", "CARR", "DXCM", "STZ", "A", "MET", "FIS", "CMG", "CPRT", "TEL", "DLR", "CDNS", "O", "MPWR", "WELL", "IQV", "GPN", "EW", "KHC", "MOLN", "PRU", "IDXX", "VRSK", "DOW", "KEE", "DHI", "PAYX", "HPQ", "VICI", "ANET", "FAST", "EXC", "F", "DFS", "CTAS", "AZO", "AME", "KR", "ROK", "LEN", "VMC", "GEHC", "ALGN", "CE", "CMI", "BBY", "BKR", "K", "LHX", "KMI", "WBD", "KVUE", "SYY", "STT", "HWM", "FITB", "MTB", "EFX", "EBAY", "FTV", "DLTR", "HIG", "WY", "TSCO", "HBAN", "ON", "NUE", "EXR", "GLW", "WDC", "PPG", "MRO", "RCL", "WST", "STX", "KEY", "TRGP", "ED", "CAH", "EQT", "FANG", "HAL", "NDAQ", "AWK", "LYB", "PCG", "KEYS", "XYL", "AVB", "VTR", "ATO", "FE", "ES", "IRM", "TYL", "GRMN", "RF", "BRO", "INVH", "WAT", "TDY", "LDOS", "AKAM", "STE", "POOL", "TER", "BXP", "WRB", "MOH", "COO", "IPG", "DRI", "ZBRA", "SWK", "DG", "DPZ", "EPAM", "TRMB", "HAS", "CHRW", "GEN", "PARA", "CZR", "MKTX", "IVZ", "BEN", "BWA", "RL", "FOXA", "FOX", "FMC", "NCLH", "MHK", "FRT", "LNC", "BIO", "NWL"]

    try:
        sp5 = pd.read_html(io.StringIO(requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies', timeout=5).text))[0]
        tickers = sp5['Symbol'].tolist()
        dax_wiki = pd.read_html(io.StringIO(requests.get('https://en.wikipedia.org/wiki/DAX', timeout=5).text))[4]
        tickers.extend([f"{t.split('.')[0]}.DE" for t in dax_wiki['Ticker symbol'].tolist()])
        tickers.extend(em_list)
    except:
        tickers = sp500_full + dax_list + em_list
        
    return sorted(list(set([t.replace('.', '-') if (".DE" not in t and "." in t) else t for t in tickers])))

# ==========================================
# 3. HELPER FUNKTIONEN (VOLLAUTOMATISIERT)
# ==========================================
def get_av_quote(symbol):
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={AV_KEY}"
        res = requests.get(url, timeout=5)
        data = res.json()
        if "Global Quote" in data and "05. price" in data["Global Quote"]:
            return float(data["Global Quote"]["05. price"])
    except: pass
    return None

def get_av_yield(maturity="10year"):
    try:
        url = f"https://www.alphavantage.co/query?function=TREASURY_YIELD&interval=daily&maturity={maturity}&apikey={AV_KEY}"
        res = requests.get(url, timeout=5)
        data = res.json()
        if "data" in data and len(data["data"]) > 0:
            val = data["data"][0].get("value", ".")
            if val != ".": return float(val)
    except: pass
    return None

@st.cache_data(ttl=43200)
def _fetch_api_macro_data():
    data = {"PMI_USA": None, "PMI_DAX": None, "PMI_EM": None, "ZEW_EU": None}
    
    try:
        url_av_pmi = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=I:USPMI&apikey={AV_KEY}"
        res_av = requests.get(url_av_pmi, timeout=8)
        av_json = res_av.json()
        if "Monthly Time Series" in av_json:
            latest_month = list(av_json["Monthly Time Series"].keys())[0]
            val = av_json["Monthly Time Series"][latest_month]["4. close"]
            data["PMI_USA"] = float(val)
    except: pass

    headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
    
    urls_pmi = [
        "https://tradingeconomics.com/country-list/manufacturing-pmi",
        "https://api.codetabs.com/v1/proxy/?quest=https://tradingeconomics.com/country-list/manufacturing-pmi",
        "https://api.allorigins.win/raw?url=https://tradingeconomics.com/country-list/manufacturing-pmi"
    ]
    
    html_pmi = None
    for u in urls_pmi:
        try:
            res = requests.get(u, headers=headers, timeout=10)
            if res.status_code == 200 and "United States" in res.text:
                html_pmi = res.text
                break
        except: pass

    if html_pmi:
        match_us = re.search(r'United States\s*</a>\s*</td>\s*<td[^>]*>\s*([\d\.]+)\s*</td>', html_pmi, re.IGNORECASE)
        if match_us: data['PMI_USA'] = float(match_us.group(1))

        match_de = re.search(r'Germany\s*</a>\s*</td>\s*<td[^>]*>\s*([\d\.]+)\s*</td>', html_pmi, re.IGNORECASE)
        if match_de: data['PMI_DAX'] = float(match_de.group(1))

        em_weights = {'China': 0.347, 'India': 0.208, 'Taiwan': 0.208, 'South Korea': 0.167, 'Brazil': 0.069}
        em_val, w_sum = 0, 0
        for c, w in em_weights.items():
            match_em = re.search(rf'{c}\s*</a>\s*</td>\s*<td[^>]*>\s*([\d\.]+)\s*</td>', html_pmi, re.IGNORECASE)
            if match_em:
                em_val += float(match_em.group(1)) * w
                w_sum += w
        if w_sum > 0: data['PMI_EM'] = round(em_val / w_sum, 1)

    urls_zew = [
        "https://tradingeconomics.com/country-list/zew-economic-sentiment-index",
        "https://api.codetabs.com/v1/proxy/?quest=https://tradingeconomics.com/country-list/zew-economic-sentiment-index",
        "https://api.allorigins.win/raw?url=https://tradingeconomics.com/country-list/zew-economic-sentiment-index"
    ]
    for u in urls_zew:
        try:
            res = requests.get(u, headers=headers, timeout=10)
            if res.status_code == 200 and "Germany" in res.text:
                match_zew = re.search(r'Germany\s*</a>\s*</td>\s*<td[^>]*>\s*([\-\d\.]+)\s*</td>', res.text, re.IGNORECASE)
                if match_zew:
                    data['ZEW_EU'] = float(match_zew.group(1))
                    break
        except: pass

    if data["PMI_USA"] is None:
        try:
            scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
            res = scraper.get("https://tradingeconomics.com/country-list/manufacturing-pmi", timeout=10)
            match_us = re.search(r'United States\s*</a>\s*</td>\s*<td[^>]*>\s*([\d\.]+)\s*</td>', res.text, re.IGNORECASE)
            if match_us: data['PMI_USA'] = float(match_us.group(1))
        except: pass

    return data

def get_live_macro_data():
    data = _fetch_api_macro_data()
    backup_file = "pmi_backup.json"
    
    if os.path.exists(backup_file):
        try:
            with open(backup_file, "r") as f:
                cached_data = json.load(f)
            if data["PMI_USA"] is None and cached_data.get("PMI_USA"): data["PMI_USA"] = cached_data["PMI_USA"]
            if data["PMI_DAX"] is None and cached_data.get("PMI_DAX"): data["PMI_DAX"] = cached_data["PMI_DAX"]
            if data["PMI_EM"] is None and cached_data.get("PMI_EM"):  data["PMI_EM"] = cached_data["PMI_EM"]
            if data["ZEW_EU"] is None and cached_data.get("ZEW_EU"):  data["ZEW_EU"] = cached_data["ZEW_EU"]
        except: pass
        
    if data["PMI_USA"] is not None:
        try:
            with open(backup_file, "w") as f:
                json.dump(data, f)
        except: pass

    return data

def get_vdax_robust():
    for t in ["^VDAX", "V1X.DE"]:
        av_val = get_av_quote(t)
        if av_val is not None: return av_val
    for t in ["^V1X", "^VDAX", "V1X.DE"]:
        try:
            d = yf.download(t, period="5d", progress=False)
            if not d.empty and len(d) > 0: return float(d['Close'].iloc[-1].iloc[0])
        except: continue
    try:
        scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
        try:
            res = scraper.get("https://www.onvista.de/index/VDAX-NEW-Index-12105789", timeout=5)
            match_json = re.search(r'"price"\s*:\s*"?([1-9][0-9]\.[0-9]{2})"?', res.text)
            if match_json: return float(match_json.group(1))
            match_text = re.search(r'([1-9][0-9],[0-9]{2})\s*Pkt\.', res.text)
            if match_text: return float(match_text.group(1).replace(',', '.'))
        except: pass
        try:
            res = scraper.get("https://www.comdirect.de/inf/indizes/DE000A0DMX99", timeout=5)
            match = re.search(r'>([1-9][0-9],[0-9]{2})<', res.text)
            if match: return float(match.group(1).replace(',', '.'))
        except: pass
    except: pass
    return None

def get_val(ticker):
    av_val = get_av_quote(ticker)
    if av_val is not None: return av_val
    try:
        d = yf.download(ticker, period="5d", progress=False)
        if not d.empty and len(d) > 0: return float(d['Close'].iloc[-1].iloc[0])
    except: pass
    return None

def get_commodity_data(ticker):
    try:
        t = yf.Ticker(ticker)
        d = t.history(period="1mo")
        if not d.empty and len(d) >= 2:
            cp = float(d['Close'].iloc[-1])
            prev_p = float(d['Close'].iloc[-2])
            sma20 = float(d['Close'].rolling(20).mean().iloc[-1])
            pct_change = ((cp / prev_p) - 1) * 100
            return cp, pct_change, sma20
    except: pass
    return None, None, None

# ==========================================
# 4. SIDEBAR (MARKTEINSTUFUNG HOLISTIC)
# ==========================================
with st.sidebar:
    st.title("🎯 Sniper v5.17")
    
    st.markdown('<hr style="margin: 0px 0 10px 0; border: none; border-top: 1px solid #2d3239;">', unsafe_allow_html=True)
    st.markdown("### 🛡️ Markteinstufung")
    
    macro_data = get_live_macro_data()
    auto_vdax = get_vdax_robust()
    
    if macro_data["PMI_USA"] is None or macro_data["PMI_DAX"] is None or macro_data["ZEW_EU"] is None:
        with st.expander("⚠️ Manuelle Eingabe (PMI/ZEW):", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1: man_pmi_us = st.number_input("PMI US", value=0.0, step=0.1)
            with c2: man_pmi_eu = st.number_input("PMI EU", value=0.0, step=0.1)
            with c3: man_zew = st.number_input("ZEW", value=0.0, step=0.1)
                
            vdax_final = auto_vdax
            pmi_usa_final = man_pmi_us if man_pmi_us > 0 else macro_data["PMI_USA"]
            pmi_dax_final = man_pmi_eu if man_pmi_eu > 0 else macro_data["PMI_DAX"]
            zew_eu_final = man_zew if man_zew > 0 else macro_data["ZEW_EU"]
            pmi_em_final = macro_data["PMI_EM"] 
    else:
        vdax_final = auto_vdax
        pmi_usa_final = macro_data["PMI_USA"]
        pmi_dax_final = macro_data["PMI_DAX"]
        zew_eu_final = macro_data["ZEW_EU"]
        pmi_em_final = macro_data["PMI_EM"]

    # ---- USA ----
    st.markdown('<div class="reg-header">🇺🇸 USA</div>', unsafe_allow_html=True)
    vix = get_val("^VIX")
    vix_val = f"{vix:.2f}" if vix is not None else "N/A"
    pmi_usa_str = f"{pmi_usa_final:.1f}" if pmi_usa_final is not None else "N/A"
    
    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">VIX (Angst)</span><span class="sidebar-value">{vix_val}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">PMI (Wirtschaft)</span><span class="sidebar-value">{pmi_usa_str}</span></div>', unsafe_allow_html=True)
    
    if vix is not None:
        if vix < 20: v_stat, b_class = "Stabil", "success-box"
        elif 20 <= vix <= 30: v_stat, b_class = "Nervös", "warning-box"
        else: v_stat, b_class = "Panik", "error-box"
        
        if pmi_usa_final is not None:
            p_stat = "Wachstum" if pmi_usa_final >= 50 else "Abschwung"
            if pmi_usa_final < 50 and b_class == "success-box": b_class = "warning-box"
            st.markdown(f'<div class="status-box {b_class}">US: {v_stat} | {p_stat}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-box {b_class}">US-Markt: {v_stat}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-box error-box">US-Markt: VIX N/A</div>', unsafe_allow_html=True)
    
    # ---- EUROPA (DAX) ----
    st.markdown('<div class="reg-header">🇪🇺 Europa (DAX)</div>', unsafe_allow_html=True)
    
    vdax_str = f"{vdax_final:.2f}" if vdax_final is not None else "N/A"
    pmi_dax_str = f"{pmi_dax_final:.1f}" if pmi_dax_final is not None else "N/A"
    zew_eu_str = f"{zew_eu_final:.1f}" if zew_eu_final is not None else "N/A"

    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">VDAX</span><span class="sidebar-value">{vdax_str}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">PMI (Wirtschaft)</span><span class="sidebar-value">{pmi_dax_str}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">ZEW (Erwartung)</span><span class="sidebar-value">{zew_eu_str}</span></div>', unsafe_allow_html=True)

    if vdax_final is not None:
        if vdax_final < 20: v_stat, b_class = "Stabil", "success-box"
        elif 20 <= vdax_final <= 30: v_stat, b_class = "Nervös", "warning-box"
        else: v_stat, b_class = "Panik", "error-box"
        
        if pmi_dax_final is not None:
            p_stat = "Wachstum" if pmi_dax_final >= 50 else "Abschwung"
            if pmi_dax_final < 50 and b_class == "success-box": b_class = "warning-box"
            
            if zew_eu_final is not None:
                z_stat = "Opt." if zew_eu_final > pmi_dax_final else "Pess."
                st.markdown(f'<div class="status-box {b_class}">EU: {v_stat} | {p_stat} ({z_stat})</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="status-box {b_class}">EU: {v_stat} | {p_stat}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-box {b_class}">EU-Markt: {v_stat}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-box error-box">EU-Markt: VDAX N/A</div>', unsafe_allow_html=True)

    # ---- EMERGING MARKETS ----
    st.markdown('<div class="reg-header">🌏 Emerging Markets</div>', unsafe_allow_html=True)
    dxy = get_val("DX-Y.NYB")
    
    dxy_val = f"{dxy:.2f}" if dxy is not None else "N/A"
    pmi_em_str = f"{pmi_em_final:.1f}" if pmi_em_final is not None else "N/A"
    
    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">DXY (Dollar)</span><span class="sidebar-value">{dxy_val}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">PMI (EM Gewicht.)</span><span class="sidebar-value">{pmi_em_str}</span></div>', unsafe_allow_html=True)
    
    if dxy is not None:
        if dxy < 102: v_stat, b_class = "Günstig", "success-box"
        elif 102 <= dxy <= 105: v_stat, b_class = "Belastet", "warning-box"
        else: v_stat, b_class = "Risiko", "error-box"
        
        if pmi_em_final is not None:
            p_stat = "Wachstum" if pmi_em_final >= 50 else "Abschwung"
            if pmi_em_final < 50 and b_class == "success-box": b_class = "warning-box"
            st.markdown(f'<div class="status-box {b_class}">EM: {v_stat} | {p_stat}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-box {b_class}">EM-Markt: {v_stat}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-box error-box">EM-Markt: Daten N/A</div>', unsafe_allow_html=True)

    # ---- ROHSTOFFE & ZINSEN (Dynamisiert) ----
    st.markdown('<div class="reg-header">📈 Zinsen & Rohstoffe</div>', unsafe_allow_html=True)
    
    tnx = get_val("^TNX") or get_av_yield("10year")
    t2y = get_val("^IRX") or get_av_yield("3month")
    
    gold_cp, gold_pct, gold_sma = get_commodity_data("GC=F")
    oil_cp, oil_pct, oil_sma = get_commodity_data("CL=F")
    
    tnx_val = f"{tnx:.2f}%" if tnx is not None else "N/A"
    gold_val = f"{gold_cp:,.2f} ({gold_pct:+.1f}%)" if gold_cp is not None else "N/A"
    oil_val = f"{oil_cp:.2f} ({oil_pct:+.1f}%)" if oil_cp is not None else "N/A"
    
    zins_status = "N/A"
    if tnx is not None and t2y is not None:
        zins_status = "⚠️ Invers" if tnx < t2y else "✅ Normal"
        
    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">US 10J Zins</span><span class="sidebar-value">{tnx_val}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">Zinskurve (10J/3M)</span><span class="sidebar-value">{zins_status}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">Gold (USD)</span><span class="sidebar-value">{gold_val}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-metric"><span class="sidebar-label">Öl WTI (USD)</span><span class="sidebar-value">{oil_val}</span></div>', unsafe_allow_html=True)

    if gold_cp is not None and gold_pct is not None:
        if gold_pct > 0.5 or (gold_sma is not None and gold_cp > gold_sma):
            st.markdown('<div class="status-box warning-box">Rohstoffe: Gold stark (Sicherheit)</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-box success-box">Rohstoffe: Gold ruhig</div>', unsafe_allow_html=True)

    if oil_cp is not None and oil_pct is not None:
        if oil_cp >= 85 or oil_pct > 1.5:
            st.markdown('<div class="status-box error-box">Inflation: Ölpreis hoch (Risiko)</div>', unsafe_allow_html=True)
        elif oil_cp <= 75 or oil_pct < -1.0:
            st.markdown('<div class="status-box success-box">Inflation: Öl günstig (Entspannung)</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-box info-box">Inflation: Öl neutral</div>', unsafe_allow_html=True)

# ==========================================
# 5. HAUPTSEITE & VOLLSTÄNDIGE AGENDA
# ==========================================
st.title("Gemini Stock Sniper PRO v5.17")
st.markdown("<br>", unsafe_allow_html=True)

with st.expander("📖 Strategie-Guide & Agenda", expanded=True):
    t1, t2, t3 = st.tabs(["🌍 Makro Phasen", "📈 Trading Kennzahlen", "💎 Invest Kennzahlen"])
    
    with t1:
        st.markdown("""
        **Markteinstufungs-Logik:**
        - **USA (VIX):** < 20 = Stabil, 20-30 = Nervös, > 30 = Panik.
        - **Europa (VDAX):** Das deutsche Angstbarometer (WKN: A0DMX9). < 20 = Stabil, 20-30 = Nervös, > 30 = Panik.
        - **Einkaufsmanagerindizes (PMI):** Der wichtigste Konjunkturindikator für die Realwirtschaft (USA, DAX/HCOB, EM). **> 50:** Wirtschaft wächst. **< 50:** Wirtschaft schrumpft.
        - **ZEW (Konjunkturerwartung DAX):** Spiegelt die Stimmung der institutionellen Anleger wider. **Regel:**<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**✅ ZEW > PMI** ➔ Optimisten in der Überzahl.<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**⚠️ ZEW < PMI** ➔ Pessimisten dominieren.
        - **DXY (US-Dollar Index):** Misst die Stärke des US-Dollars gegen andere Leitwährungen (Basiswert 100). Er ist der Taktgeber für die Emerging Markets.<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**✅ < 100:** Schwacher Dollar. Positiv für Schwellenländer, da deren Kredite günstiger werden und Kapital dorthin fließt.<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**⚖️ 100 - 105:** Normales bis belastendes Niveau.<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**⚠️ > 105:** Starker Dollar. Kritisch (Risiko), da es Kapital aus den Schwellenländern in die USA absaugt.
        - **Zinskurve (10J/3M):** Vergleicht langfristige (10 Jahre) mit kurzfristigen (3 Monate) US-Staatsanleihen.<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**✅ Normal:** 10J-Zinsen > 3M-Zinsen. Der gesunde Wirtschaftszustand (Lange Bindung = mehr Zinsen).<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**⚠️ Invers:** 3M-Zinsen > 10J-Zinsen. Ein klassisches Rezessions-Warnsignal. Der Markt preist schwere Zeiten ein.
        - **Rohstoffe & Inflation:** Die Dynamik von Gold und Öl wird laufend bewertet.
          - **Gold (Angstbarometer):** Investoren fliehen bei Unsicherheit in Gold.<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**⚠️ Stark (Sicherheit):** Preis steigt heute > 0.5% oder notiert über seinem mittelfristigen 20-Tage-Trend.<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**✅ Ruhig:** Es ist kein akuter Fluchttrend erkennbar.
          - **Öl WTI (Inflations-Treiber):** Bestimmt massiv die globalen Inflations- und Zinserwartungen.<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**⚠️ Hoch (Risiko):** Preis >= 85 USD oder plötzlicher Tagesanstieg > 1.5%. Gift für die Wirtschaft.<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**✅ Günstig (Entspannung):** Preis <= 75 USD oder starker Tagesrückgang < -1.0%. Entlastet die Margen der Unternehmen.<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**⚖️ Neutral:** Preis bewegt sich unauffällig zwischen 75 und 85 USD.
        """, unsafe_allow_html=True)
        
    with t2:
        st.markdown("""
        **Trading Pullback Logik (Ergänzt):**
        - **SMA 200 %:** Die wichtigste Filter-Linie. Zeigt den Abstand zum 200-Tage-Durchschnitt. Wir traden kurzfristig nur, wenn der langfristige Trend (SMA 200 > 0) unser Sicherheitsnetz ist.
        - **RSI (Relative Stärke):** Wert zwischen 30 und 60 gesucht. Wir wollen keine überkauften Aktien, sondern gesunde Rücksetzer.
        - **EMA 20 %:** Zeigt den prozentualen Abstand zum 20-Tage-Trend. Ideal für Einstiege sind Werte nahe 0.
        - **EMA 50 %:** Zeigt den prozentualen Abstand zur mittelfristigen 50-Tage-Linie. 
        - **EMA 20/50 % (Crossover):** Gibt den Abstand zwischen EMA 20 und EMA 50 an. Werte nahe 0 kündigen ein bevorstehendes Kreuzen der Linien an (Kauf-/Verkaufssignal).
        - **MACD (12, 26, 9):** Misst das kurzfristige Momentum. Er vergleicht die 12- und 26-Tage-Linie. <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Bullish:** MACD-Linie liegt *über* der Signallinie (Aufwärtsmomentum).<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Bearish:** MACD-Linie hat die Signallinie nach *unten* gekreuzt (Abwärtsmomentum). Ein "Bearish" MACD bei gleichzeitig intaktem Trend (EMA > 0) ist das klassische Zeichen für unseren gesuchten Pullback (Verschnaufpause)!
        - **ATR % (Volatilität):** Misst die durchschnittliche tägliche Schwankung im Verhältnis zum Preis. **⚠️ > 4%** deutet auf sehr hohes Risiko hin.
        - **BB_Pos:** Die Position im Bollinger Band (0 = unteres Band, 1 = oberes Band). Werte **< 0.2** zeigen eine starke Überverkauf-Situation an.
        - **Kauf-/Verkaufssignal:** Ein Pullback-Signal entsteht bei einer Korrektur im intakten Aufwärtstrend.
        - **Trade_Score (0-100):** Ganzheitliche Bewertung des Setups. Belohnt überverkauften RSI (max 30 Pkt), Nähe zum unteren Bollinger Band (max 30 Pkt), Nähe zum SMA 200 Support (max 20 Pkt), eine enge EMA 20/50 Kompression (max 10 Pkt) und einen bullishen MACD-Dreh (max 10 Pkt).
        """, unsafe_allow_html=True)
        
    with t3:
        st.markdown("""
        **Invest-Rating (Qualität):**
        - **Operative Marge (>12%):** Zeigt die Preismacht. Wie viel Gewinn bleibt pro Euro Umsatz hängen?
        - **ROE (>15%):** Eigenkapitalrendite. Wie effizient arbeitet das Kapital der Aktionäre?
        - **Invest_Score:** Produkt aus Marge & ROE. Höhere Werte signalisieren exzellente Business-Qualität (Gedeckelt bei 100).
        """)

# ==========================================
# 6. SCANNER (UPGRADE MIT TRADING INDIKATOREN)
# ==========================================
if st.button("🚀 VOLLSTÄNDIGEN MARKT-SCAN STARTEN"):
    min_marge = 12
    min_roe = 15
    
    universe = get_full_universe()
    results = []
    prog = st.progress(0, text="Sniper scannt...")
    
    for i, t in enumerate(universe):
        try:
            s = yf.Ticker(t)
            h = s.history(period="1y")
            if len(h) < 200: continue
            
            cp = float(h['Close'].iloc[-1])
            
            # SMA 200 Berechnung
            sma200 = float(h['Close'].rolling(200).mean().iloc[-1])
            sma200_pct = round(((cp / sma200) - 1) * 100, 1)
            
            # EMA Berechnungen (20 & 50)
            ema20 = float(h['Close'].ewm(span=20, adjust=False).mean().iloc[-1])
            ema50 = float(h['Close'].ewm(span=50, adjust=False).mean().iloc[-1])
            
            ema20_pct = round(((cp / ema20) - 1) * 100, 1)
            ema50_pct = round(((cp / ema50) - 1) * 100, 1)
            ema20_50_pct = round(((ema20 / ema50) - 1) * 100, 1) 
            
            # RSI
            delta = h['Close'].diff()
            g = (delta.where(delta > 0, 0)).rolling(14).mean()
            l = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = float(100 - (100 / (1 + (g / l))).iloc[-1])
            
            # MACD
            exp1 = h['Close'].ewm(span=12, adjust=False).mean()
            exp2 = h['Close'].ewm(span=26, adjust=False).mean()
            macd_line = exp1 - exp2
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            is_bullish = bool(macd_line.iloc[-1] > signal_line.iloc[-1])
            
            # ATR & Bollinger
            tr = pd.concat([h['High']-h['Low'], abs(h['High']-h['Close'].shift()), abs(h['Low']-h['Close'].shift())], axis=1).max(axis=1)
            atr_pct = float((tr.rolling(14).mean().iloc[-1] / cp) * 100)
            
            sma20_val = float(h['Close'].rolling(20).mean().iloc[-1])
            std20_val = float(h['Close'].rolling(20).std().iloc[-1])
            
            if std20_val != 0:
                bb_pos = float((cp - (sma20_val - std20_val*2)) / (4 * std20_val))
            else:
                bb_pos = 0.5
            
            inf = s.info
            marge = float((inf.get('operatingMargins', 0) or 0) * 100)
            roe = float((inf.get('returnOnEquity', 0) or 0) * 100)
            
            vola_warn = "⚠️ " if atr_pct > 4.0 else ""
            status = "PULLBACK" if (cp > sma200 and 30 <= rsi <= 60) else "---"
            
            # Ganzheitliches 100-Punkte System für den Trade Score
            if status == "PULLBACK":
                score_rsi = max(0, 60 - rsi)
                score_bb = max(0, (0.5 - bb_pos) * 60)
                score_bb = min(30.0, score_bb) 
                score_sma = max(0, (1 - min((cp/sma200-1), 0.15)/0.15) * 20)
                score_ema = 0
                if 0 <= ema20_50_pct <= 5:
                    score_ema = (5 - ema20_50_pct) * 2
                score_macd = 10 if is_bullish else 0
                
                trade_score = int(score_rsi + score_bb + score_sma + score_ema + score_macd)
                trade_score = min(100, trade_score) 
            else:
                trade_score = 0
            
            invest_score = 0.0
            if marge > 0 and roe > 0:
                invest_score = min(100.0, (marge * roe) / 100)
            
            results.append({
                "Ticker": t, 
                "Name": str(inf.get('shortName', t)[:15]), 
                "Status": status, 
                "Preis": round(cp, 2),
                "RSI": round(rsi, 1), 
                "EMA20_%": ema20_pct,
                "EMA50_%": ema50_pct,
                "SMA200_%": sma200_pct,
                "EMA20/50_%": ema20_50_pct,
                "MACD": "Bullish" if is_bullish else "Bearish",
                "ATR_%": f"{vola_warn}{round(atr_pct, 2)}%", 
                "BB_Pos": round(bb_pos, 2),
                "Trade_S.": trade_score,
                "Invest_S.": round(invest_score, 1), 
                "Marge%": round(marge, 1), 
                "ROE%": round(roe, 1)
            })
        except: continue
        prog.progress((i+1)/len(universe))
        
    if results:
        df = pd.DataFrame(results)
        t_tr, t_inv = st.tabs(["📈 Trading", "💎 Investing"])
        with t_tr: 
            st.dataframe(df[df['Status'] == "PULLBACK"].sort_values("Trade_S.", ascending=False)[
                ["Ticker", "Name", "Preis", "RSI", "EMA20_%", "EMA50_%", "SMA200_%", "EMA20/50_%", "MACD", "ATR_%", "BB_Pos", "Trade_S."]
            ], hide_index=True, width='stretch')
        with t_inv: 
            st.dataframe(df.sort_values("Invest_S.", ascending=False)[
                ["Ticker", "Name", "Preis", "Invest_S.", "Marge%", "ROE%"]
            ], hide_index=True, width='stretch')
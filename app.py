import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# ==========================================
# 1. SETUP & DESIGN
# ==========================================
st.set_page_config(page_title="Gemini Stock Sniper PRO", layout="wide", page_icon="🎯")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4255; }
    div.stButton > button:first-child { background-color: #00ff00; color: black; font-weight: bold; width: 100%; }
    .info-box { background-color: #262730; padding: 10px; border-left: 5px solid #00ff00; font-size: 0.9em; }
    .disclaimer { font-size: 0.8em; color: #666; margin-top: 50px; border-top: 1px solid #333; padding-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LOGIK-FUNKTIONEN
# ==========================================
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=3600)
def get_all_tickers_pro():
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        table = pd.read_html(url, storage_options={'User-Agent': 'Mozilla/5.0'})
        sp500 = table[0]['Symbol'].tolist()
        sp500 = [t.replace('.', '-') for t in sp500]
    except:
        sp500 = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA"] # Kleiner Fallback
    
    dax = ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BEI.DE", "BMW.DE", "BNR.DE", 
           "CBK.DE", "CON.DE", "1COV.DE", "DTG.DE", "DBK.DE", "DB1.DE", "DHL.DE", "DTE.DE", 
           "EOAN.DE", "FRE.DE", "FME.DE", "HNR1.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "MBG.DE", 
           "MRK.DE", "MTX.DE", "MUV2.DE", "P911.DE", "PAH3.DE", "QIA.DE", "RHM.DE", "RWE.DE", 
           "SAP.DE", "SRT3.DE", "ENR.DE", "SIE.DE", "SHL.DE", "SY1.DE", "VOW3.DE", "VNA.DE"]
    return list(set(sp500 + dax))

# ==========================================
# 3. SIDEBAR (Krisen-Radar & Filter)
# ==========================================
with st.sidebar:
    st.title("🌍 Globales Radar")
    try:
        vix_h = yf.Ticker("^VIX").history(period="2d")
        oil_h = yf.Ticker("CL=F").history(period="5d")
        gold_h = yf.Ticker("GC=F").history(period="5d")
        
        vix = vix_h['Close'].iloc[-1]
        oil_ch = ((oil_h['Close'].iloc[-1] / oil_h['Close'].iloc[0]) - 1) * 100
        gold_ch = ((gold_h['Close'].iloc[-1] / gold_h['Close'].iloc[0]) - 1) * 100
        
        m1, m2 = st.columns(2)
        m1.metric("VIX", f"{vix:.2f}", delta="Angst" if vix > 22 else "Ruhig", delta_color="inverse")
        m2.metric("Gold (5T)", f"{gold_ch:+.1f}%")
        st.metric("Öl WTI (5T)", f"{oil_ch:+.1f}%", delta="Preisdruck" if oil_ch > 5 else "Stabil", delta_color="inverse")
        
        if oil_ch > 5 and gold_ch > 2:
            st.error("⚠️ GEOPOLITISCHER ALARM")
        elif vix > 22:
            st.warning("📉 HOHE VOLATILITÄT")
        else:
            st.success("🟢 MARKT STABIL")
    except: st.write("Marktdaten laden...")
    
    st.divider()
    st.markdown('<div class="info-box"><b>💡 Zielwerte:</b><br>Marge > 12% | ROE > 15%</div>', unsafe_allow_html=True)
    min_marge = st.slider("Min. Marge %", 0, 40, 12)
    min_roe = st.slider("Min. ROE %", 0, 40, 15)

# ==========================================
# 4. HAUPTSEITE & SCANNER
# ==========================================
st.title("🎯 Gemini Stock Sniper PRO")

if st.button("🚀 VOLLSTÄNDIGEN MARKT-SCAN STARTEN"):
    start_time = datetime.now().strftime("%H:%M:%S")
    tickers = get_all_tickers_pro()
    results = []
    
    progress_bar = st.progress(0, text="Analysiere Markt...")
    
    for i, t in enumerate(tickers):
        try:
            stock = yf.Ticker(t)
            inf = stock.info
            h = stock.history(period="1y")
            if h.empty or len(h) < 200: continue
            
            cp = h['Close'].iloc[-1]
            s200 = h['Close'].rolling(200).mean().iloc[-1]
            rsi = calculate_rsi(h).iloc[-1]
            marge = inf.get('operatingMargins', 0) or 0
            roe = inf.get('returnOnEquity', 0) or 0
            growth = inf.get('earningsQuarterlyGrowth', 0) or 0
            de = (inf.get('debtToEquity', 0) or 0) / 100

            t_score, i_score, status = 0, 0, "Kein Signal"
            
            if cp > s200:
                dist = (cp/s200 - 1) * 100
                if dist < 10 and 30 <= rsi <= 55:
                    status = "🟢 PULLBACK"
                    t_score = int((max(0, 100 - dist * 10) * 0.6) + ((60 - rsi) * 5 * 0.4))
            
            if roe >= (min_roe/100) and marge >= (min_marge/100) and de <= 1.0 and cp > s200:
                i_score = int((min(100, marge*300)*0.4) + (min(100, roe*250)*0.4) + (min(100, growth*200)*0.2))
            
            results.append({
                "Ticker": t, "Name": inf.get('longName', t)[:20], "Preis": round(cp, 2),
                "RSI": round(rsi, 1), "Marge%": round(marge*100, 1), "ROE%": round(roe*100, 1),
                "Trade_Score": t_score, "Invest_Score": i_score, "Status": status,
                "Wachstum%": round(growth*100, 1)
            })
        except: continue
        if (i+1) % 10 == 0:
            progress_bar.progress((i + 1) / len(tickers), text=f"Scan: {i+1}/{len(tickers)}")
            
    if results:
        df = pd.DataFrame(results)
        st.success(f"Analyse abgeschlossen! (Abruf: {start_time})")

        # --- NEU: LEGENDE EXPANDER ---
        with st.expander("📖 Hilfe: Kennzahlen, Grenzen & Status"):
            l1, l2 = st.columns(2)
            with l1:
                st.markdown("""
                **Kennzahlen & Grenzwerte:**
                - **Marge (>12%):** Profitabilität. Je höher, desto krisenfester.
                - **ROE (>15%):** Effizienz der Kapitalverwendung.
                - **RSI (35-50):** Wir suchen Aktien, die kurz "Luft holen" (Pullback).
                - **Invest_Score:** 100 = Perfekte fundamentale Qualität.
                """)
            with l2:
                st.markdown("""
                **Bezeichnungen & Status:**
                - **🟢 PULLBACK:** Aktie ist im Aufwärtstrend, aber aktuell kurzfristig günstig.
                - **Trade_Score:** 100 = Idealer technischer Zeitpunkt für Einstieg.
                - **Kein Signal:** Aktie ist aktuell zu teuer (überhitzt) oder im Abwärtstrend.
                """)

        tab1, tab2, tab3 = st.tabs(["📈 Trading", "💎 Investing", "📊 Alle Daten"])
        
        with tab1:
            trades = df[df['Status'] == "🟢 PULLBACK"]
            if not trades.empty:
                st.dataframe(trades.sort_values("Trade_Score", ascending=False), hide_index=True)
            else: st.info("Keine Pullbacks aktuell.")
                
        with tab2:
            invests = df[df['Invest_Score'] > 0]
            if not invests.empty:
                st.dataframe(invests.sort_values("Invest_Score", ascending=False), hide_index=True)
            else: st.info("Keine Qualitäts-Aktien nach Filtern.")

        with tab3:
            st.dataframe(df, use_container_width=True)
            
        # Haftungsausschluss ganz unten
        st.markdown('<div class="disclaimer">⚠️ <b>Haftungsausschluss:</b> Diese App dient nur Informationszwecken. Keine Anlageberatung. Aktieninvestments sind mit Risiken verbunden.</div>', unsafe_allow_html=True)
    else:
        st.error("Keine Daten empfangen.")
else:
    st.info("Klicke auf den Button, um den Scan zu starten.")
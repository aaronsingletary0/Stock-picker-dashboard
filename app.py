import streamlit as st
import pandas as pd
from pathlib import Path
import json
st.set_page_config(page_title="Stock Picker Research",layout="wide")
st.title("Stock Picker | Equity Research")
st.warning("Exploratory research only. No validated investment recommendations.")
st.caption("Operating income / assets 40% • Momentum 25% • Earnings yield 15% • Conservative asset growth 15% • Book-to-market 5%")
root=Path(__file__).parent/"data"
def load(name,cols):
    p=root/name
    if not p.exists():
        st.info("Research data not yet available.")
        return None
    x=pd.read_csv(p)
    if x.empty or not set(cols)<=set(x.columns):
        st.info("No eligible observations.")
        return None
    return x[cols]
a,b,c,d=st.tabs(["Factor portfolios","Rebalance","Historical performance","Quality gates"])
with a:
    x=load("portfolios.csv",["index","as_of","n","rank","security_id","score","target_weight"])
    if x is not None:
        idx=st.selectbox("Universe",sorted(x["index"].unique()))
        x=x[x["index"]==idx]
        n=st.selectbox("Holdings",sorted(x.n.unique()))
        x=x[x.n==n].sort_values("rank")
        st.bar_chart(x.set_index("security_id").target_weight)
        st.dataframe(x,hide_index=True)
with b:
    x=load("rebalance.csv",["index","n","security_id","previous_target","new_target","delta","action"])
    if x is not None: st.dataframe(x,hide_index=True)
    st.caption("Target comparisons only, not brokerage holdings.")
with c:
    x=load("returns.csv",["index","n","frequency","start","end","factor","size","paired"])
    if x is not None:
        idx=st.selectbox("Historical universe",sorted(x["index"].unique()))
        x=x[x["index"]==idx]
        n=st.selectbox("Historical holdings",sorted(x.n.unique()))
        x=x[x.n==n]
        freq=st.selectbox("Frequency",sorted(x.frequency.unique()))
        x=x[x.frequency==freq].sort_values("start")
        st.dataframe(x,hide_index=True)
        if len(x) and x.paired.astype(str).str.lower().eq("true").all() and x[["factor","size"]].notna().all().all() and list(x.start.iloc[1:])==list(x.end.iloc[:-1]):
            st.line_chart((1+x.set_index("end")[["factor","size"]]).cumprod())
    st.caption("Historical issuer identity and corporate actions remain unverified.")
with d:
    st.error("Validated portfolio publication remains restricted.")
    st.caption("Minimum exploratory coverage: 70%.")
    p=root/"status.json"
    if p.exists():
        s=json.loads(p.read_text())
        st.json({k:s[k] for k in ("as_of","coverage","status") if k in s})
    else: st.info("No approved public evidence snapshot available.")

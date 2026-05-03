"""
Antigravity — Personal Finance Manager
Run with: streamlit run finance_app.py
"""

import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import date, datetime

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Antigravity · Finance",
    page_icon="🪐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS  — dark glassmorphism theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Background ── */
.stApp {
    background: linear-gradient(135deg, #0f0c1a 0%, #1a1030 50%, #0d1b2a 100%);
    color: #e8e0f5;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.04);
    border-right: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(20px);
}
[data-testid="stSidebar"] .stMarkdown h2 {
    color: #c084fc;
    font-weight: 700;
    letter-spacing: 0.04em;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 20px 24px !important;
    backdrop-filter: blur(12px);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(192,132,252,0.15);
}
[data-testid="stMetricLabel"] { color: #a78bfa !important; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; }
[data-testid="stMetricValue"] { color: #f3eeff !important; font-size: 1.9rem !important; font-weight: 700 !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    padding: 0.5rem 1.2rem;
    transition: all 0.2s ease;
    box-shadow: 0 4px 15px rgba(124,58,237,0.35);
}
.stButton > button:hover {
    background: linear-gradient(135deg, #6d28d9, #4338ca);
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(124,58,237,0.5);
}

/* ── Input widgets ── */
.stSelectbox > div > div, .stTextInput > div > div > input,
.stNumberInput > div > div > input, .stDateInput > div > div > input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #e8e0f5 !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.08);
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 12px !important;
    color: #c084fc !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
}
.streamlit-expanderContent {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 0 0 12px 12px !important;
}

/* ── Section dividers ── */
hr { border-color: rgba(255,255,255,0.08) !important; }

/* ── Chart backgrounds ── */
.js-plotly-plot .plotly .main-svg {
    border-radius: 16px;
}

/* ── Radio buttons ── */
.stRadio > div { gap: 0.6rem; }
.stRadio label { color: #c4b5fd; }

/* ── Alert / info boxes ── */
.stAlert { border-radius: 12px !important; }

/* ── Header title gradient ── */
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(90deg, #a78bfa, #818cf8, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin-bottom: 0.2rem;
}
.hero-sub {
    color: #94a3b8;
    font-size: 1rem;
    font-weight: 400;
    margin-bottom: 1.5rem;
}
.section-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #7c3aed;
    margin-bottom: 0.4rem;
}
.tag-pill {
    display: inline-block;
    background: rgba(124,58,237,0.18);
    color: #c084fc;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.75rem;
    font-weight: 600;
    border: 1px solid rgba(192,132,252,0.25);
    margin-right: 4px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 1 — DATA PERSISTENCE
# ─────────────────────────────────────────────────────────────────────────────
DB_PATH = "wealth_manager.db"

CATEGORIES = ["Housing", "Food", "Transport", "Utilities", "Entertainment", "Healthcare", "Other"]

NEEDS_CATS  = {"Housing", "Food", "Transport", "Utilities", "Healthcare"}
WANTS_CATS  = {"Entertainment", "Other"}


def get_connection():
    """Return a sqlite3 connection to the local database."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create the transactions table if it does not already exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT,
                description TEXT,
                category    TEXT,
                type        TEXT,
                amount      REAL
            )
        """)
        conn.commit()


def load_data() -> pd.DataFrame:
    """Return all transactions as a DataFrame; empty DF if none exist."""
    with get_connection() as conn:
        try:
            df = pd.read_sql_query("SELECT * FROM transactions ORDER BY date DESC", conn)
        except Exception:
            df = pd.DataFrame(columns=["id", "date", "description", "category", "type", "amount"])
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df


def insert_transaction(txn_date: str, description: str, category: str,
                        txn_type: str, amount: float):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO transactions (date, description, category, type, amount) VALUES (?,?,?,?,?)",
            (txn_date, description, category, txn_type, amount)
        )
        conn.commit()


def delete_transaction(txn_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM transactions WHERE id = ?", (txn_id,))
        conn.commit()


# Initialise DB on every run (idempotent)
init_db()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN AREA & TABS (Mobile Oriented)
# ─────────────────────────────────────────────────────────────────────────────
df_all = load_data()

if "form_reset" not in st.session_state:
    st.session_state.form_reset = 0

# ── Hero header ────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">Antigravity Finance</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Mobile-first personal wealth dashboard</div>', unsafe_allow_html=True)

# Mobile-friendly Tabs
tab_dash, tab_add, tab_logs = st.tabs(["📊 Dashboard", "➕ Add Entry", "📝 Manage Logs"])

with tab_add:
    st.markdown("### ➕ Record Transaction")
    st.markdown("Quickly add a new income or expense log.")
    reset_key = st.session_state.form_reset

    amount = st.number_input("Amount (₹)", min_value=0.01, step=0.01, format="%.2f", key=f"amount_{reset_key}")
    description = st.text_input("Description", placeholder="e.g. Zomato order", key=f"desc_{reset_key}")
    category = st.selectbox("Category", CATEGORIES, key=f"cat_{reset_key}")
    txn_type = st.radio("Type", ["Income", "Expense"], horizontal=True, key=f"type_{reset_key}")
    txn_date = st.date_input("Date", value=date.today(), key=f"date_{reset_key}")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✅ Submit Transaction", use_container_width=True):
        if amount > 0 and description.strip():
            insert_transaction(str(txn_date), description.strip(), category, txn_type, amount)
            st.session_state.form_reset += 1
            st.success("Transaction saved successfully!")
            st.rerun()
        else:
            st.error("Enter a valid amount and description.")

with tab_logs:
    st.markdown("### 🗑 Remove Wrongly Entered Logs")
    st.markdown("Tap the Delete button to remove an incorrect entry.")
    if df_all.empty:
        st.info("No logs available to manage.")
    else:
        # Show a mobile-friendly list view for deletions
        for _, row in df_all.head(50).iterrows():
            c1, c2 = st.columns([3, 1])
            with c1:
                sign = "+" if row["type"] == "Income" else "-"
                color = "#34d399" if row["type"] == "Income" else "#f87171"
                st.markdown(
                    f"<div style='font-size:0.95rem; line-height:1.4;'>"
                    f"<b>{row['date'].strftime('%d %b %Y')}</b> · {row['description']}<br>"
                    f"<span style='color:{color};font-weight:600;'>{sign}₹{row['amount']:,.0f}</span> · "
                    f"<span style='color:#a78bfa;font-size:0.8rem;'>{row['category']}</span>"
                    f"</div>", 
                    unsafe_allow_html=True
                )
            with c2:
                # Vertical alignment fix for button
                st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
                if st.button("Delete", key=f"del_{row['id']}", use_container_width=True):
                    delete_transaction(int(row["id"]))
                    st.rerun()
            st.markdown("<hr style='margin: 0.8em 0; border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)

with tab_dash:
    if df_all.empty:
        st.info("🌱 No transactions yet. Go to the '➕ Add Entry' tab to record your first log!")
    else:
        # ── Month selector ──────────────────────────────────────────────────────────
        df_all["month_label"] = df_all["date"].dt.strftime("%B %Y")
        available_months = df_all["month_label"].drop_duplicates().tolist()

        st.markdown('<div class="section-label" style="margin-top:10px;">Filter by Month</div>', unsafe_allow_html=True)
        selected_month = st.selectbox("", available_months, label_visibility="collapsed")

        df = df_all[df_all["month_label"] == selected_month].copy()

        # ── Compute KPIs ────────────────────────────────────────────────────────────
        income_df   = df[df["type"] == "Income"]
        expense_df  = df[df["type"] == "Expense"]

        total_income   = income_df["amount"].sum()
        total_expenses = expense_df["amount"].sum()
        net_balance    = total_income - total_expenses
        savings_rate   = ((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0.0

        # ── KPI Row ─────────────────────────────────────────────────────────────────
        st.markdown('<div class="section-label">Monthly Overview</div>', unsafe_allow_html=True)
        # Mobile optimization: 2x2 grid
        k1, k2 = st.columns(2)
        k3, k4 = st.columns(2)

        with k1:
            st.metric("💰 Income", f"₹{total_income:,.0f}")
        with k2:
            st.metric("💸 Expenses", f"₹{total_expenses:,.0f}")
        with k3:
            st.metric("🏦 Net Balance", f"₹{net_balance:,.0f}",
                      delta=f"₹{abs(net_balance):,.0f} {'surplus' if net_balance >= 0 else 'deficit'}",
                      delta_color="normal" if net_balance >= 0 else "inverse")
        with k4:
            st.metric("📈 Savings Rate", f"{savings_rate:.1f}%",
                      delta=f"{'On track ✓' if savings_rate >= 20 else 'Below 20% ⚠'}")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Charts row ──────────────────────────────────────────────────────────────
        CHART_THEME = dict(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", color="#c4b5fd"),
            margin=dict(l=10, r=10, t=40, b=10),
        )
        PALETTE = ["#7c3aed", "#818cf8", "#38bdf8", "#34d399", "#fbbf24", "#f472b6", "#fb923c", "#a3e635"]

        # Mobile optimization: Vertical stacking
        st.markdown('<div class="section-label">Expense Breakdown</div>', unsafe_allow_html=True)
        if expense_df.empty:
            st.info("No expense transactions for this month.")
        else:
            cat_totals = expense_df.groupby("category")["amount"].sum().reset_index()
            fig_pie = px.pie(
                cat_totals, values="amount", names="category",
                color_discrete_sequence=PALETTE,
                hole=0.45,
            )
            fig_pie.update_traces(
                textfont=dict(family="Inter", size=13, color="white"),
                hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>"
            )
            fig_pie.update_layout(height=320, **CHART_THEME, legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown('<div class="section-label" style="margin-top:20px;">Daily Spending</div>', unsafe_allow_html=True)
        if expense_df.empty:
            st.info("No expense transactions for this month.")
        else:
            daily = expense_df.groupby(expense_df["date"].dt.date)["amount"].sum().reset_index()
            daily.columns = ["date", "amount"]
            fig_bar = px.bar(
                daily, x="date", y="amount",
                color_discrete_sequence=["#7c3aed"],
            )
            fig_bar.update_traces(
                marker_line_color="rgba(255,255,255,0.1)",
                marker_line_width=1,
                hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>"
            )
            fig_bar.update_layout(
                height=280,
                xaxis_title="", yaxis_title="Amount (₹)",
                xaxis=dict(showgrid=False, tickformat="%d %b"),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
                **CHART_THEME
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")

        # ─────────────────────────────────────────────────────────────────────────────
        # MODULE 4 — INTELLIGENT SAVINGS ADVISOR
        # ─────────────────────────────────────────────────────────────────────────────
        category_totals = expense_df.groupby("category")["amount"].sum()

        food_pct      = (category_totals.get("Food",          0) / total_expenses * 100) if total_expenses > 0 else 0
        entertain_pct = (category_totals.get("Entertainment", 0) / total_expenses * 100) if total_expenses > 0 else 0

        with st.expander("💡 Savings Advisor", expanded=True):
            st.markdown("### 🔍 Smart Alerts")

            if total_expenses > total_income:
                st.error("🚨 **Deficit warning:** your expenses exceed income this month.")

            if total_income > 0 and savings_rate < 20:
                st.warning(f"⚠️ Your savings rate is **{savings_rate:.1f}%**, below the 20% target.")
            elif total_income > 0:
                st.success(f"✅ Great work! Your savings rate is **{savings_rate:.1f}%** — above the 20% benchmark.")

            if total_expenses > 0 and food_pct > 25:
                st.info(f"🍔 Food is **{food_pct:.1f}%** of expenses (target: <25%). Try meal-prepping weekly.")

            if total_expenses > 0 and entertain_pct > 15:
                st.info(f"🎬 Entertainment is **{entertain_pct:.1f}%** of expenses. Look for free local events.")

            if total_expenses == 0:
                st.info("No expense data for this month.")

            st.markdown("### 📐 50 / 30 / 20 Rule")

            if total_income > 0 and total_expenses > 0:
                needs_amt  = sum(category_totals.get(c, 0) for c in NEEDS_CATS)
                wants_amt  = sum(category_totals.get(c, 0) for c in WANTS_CATS)
                savings_amt = max(total_income - total_expenses, 0)

                needs_pct   = needs_amt  / total_income * 100
                wants_pct   = wants_amt  / total_income * 100
                savings_pct = savings_amt / total_income * 100

                bands = [
                    ("🏠 Needs",   needs_pct,   50, "#7c3aed"),
                    ("🎉 Wants",   wants_pct,   30, "#818cf8"),
                    ("💰 Savings", savings_pct, 20, "#38bdf8"),
                ]

                for label, actual, target, colour in bands:
                    over = actual > target
                    status = "⚠️ Over" if over else "✅ OK"
                    st.markdown(f"**{label}** — `{actual:.1f}%` / target `{target}%` {status}")
                    st.progress(min(actual / 100, 1.0))

                # Gauge chart for savings rate
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=savings_pct,
                    delta={"reference": 20, "increasing": {"color": "#34d399"}, "decreasing": {"color": "#f87171"}},
                    gauge={
                        "axis": {"range": [0, 60], "tickcolor": "#c4b5fd", "tickfont": {"color": "#c4b5fd"}},
                        "bar": {"color": "#7c3aed"},
                        "bgcolor": "rgba(0,0,0,0)",
                        "bordercolor": "rgba(255,255,255,0.08)",
                        "steps": [
                            {"range": [0, 20],  "color": "rgba(248,113,113,0.15)"},
                            {"range": [20, 40], "color": "rgba(52,211,153,0.12)"},
                            {"range": [40, 60], "color": "rgba(56,189,248,0.12)"},
                        ],
                        "threshold": {"line": {"color": "#a3e635", "width": 3}, "thickness": 0.8, "value": 20},
                    },
                    title={"text": "Savings Rate %", "font": {"color": "#c4b5fd", "family": "Inter", "size": 16}},
                    number={"suffix": "%", "font": {"color": "#f3eeff", "size": 32, "family": "Inter"}},
                ))
                fig_gauge.update_layout(
                    height=240,
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#c4b5fd"),
                    margin=dict(l=10, r=10, t=30, b=10),
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
            else:
                st.info("Add income and expense transactions to see the 50/30/20 breakdown.")

st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#4b5563;font-size:0.75rem;'>"
    "🪐 Antigravity Finance · Mobile-Oriented Offline Dashboard"
    "</p>",
    unsafe_allow_html=True
)


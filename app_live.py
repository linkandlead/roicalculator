import json
import math
from pathlib import Path
import base64

import streamlit as st
import plotly.graph_objects as go

CONFIG_DIR = Path("config")
ASSETS_DIR = Path("assets")

def load_json(path: Path, defaults: dict) -> dict:
    data = defaults.copy()
    if path.exists():
        try:
            data.update(json.loads(path.read_text()))
        except Exception:
            pass
    return data

def load_text(path: Path, fallback: str = "") -> str:
    if path.exists():
        try:
            return path.read_text()
        except Exception:
            return fallback
    return fallback

def save_json(path: Path, data: dict):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

def save_text(path: Path, text: str):
    path.write_text(text)

def img_base64(path: Path, width: int = 180) -> str:
    if not path.exists():
        return ""
    b64 = base64.b64encode(path.read_bytes()).decode()
    return f"<img src='data:image/png;base64,{b64}' width='{width}'>"

def read_file_bytes(path: Path) -> bytes | None:
    try:
        return path.read_bytes()
    except Exception:
        return None

st.set_page_config(page_title="Link & Lead ROI", layout="wide")

# Load config defaults + files
theme = load_json(CONFIG_DIR / "theme.json", {
    "header_bg": "#8BD3C0",
    "header_text": "#111827",
    "stat_card_min_height": 140,

    "funnel_outreach_color": "#78716C",
    "funnel_expected_color": "#A8A29E",
    "funnel_potential_color": "#D97706",

    "result_image": "assets/slide8.png"
})
strings = load_json(CONFIG_DIR / "strings.json", {
    "app_title": "Link & Lead ROI calculator"
})

benefits_base_md = load_text(CONFIG_DIR / "benefits_base.md", "")
benefits_engage_md = load_text(CONFIG_DIR / "benefits_engage.md", "")
benefits_lead_md = load_text(CONFIG_DIR / "benefits_lead.md", "")

# Tabs
tab_preview, tab_editor = st.tabs(["Preview", "Editor"])

with tab_preview:
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
html, body, [class*="st-"] {{ font-family: 'Inter', sans-serif; }}
.main {{ background-color: #F8F7F5; }}

.header-box {{ background-color: {theme["header_bg"]}; padding: 1.5rem 0; margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between; border-radius: 1rem; }}
.header-text h1 {{ color: {theme["header_text"]}; margin: 0; font-weight: 900; font-size: 2.2rem; }}

.stat-card {{
    background: #FFFFFF; padding: 1.25rem; border-radius: 0.75rem; border: 1px solid #E7E5E4;
    text-align: center; height: 100%;
    min-height: {int(theme["stat_card_min_height"])}px; display:flex; flex-direction:column; justify-content:center;
}}
.stat-label {{ color: #6B7280; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05rem; }}
.stat-value {{ color: #111827; font-size: 1.65rem; font-weight: 900; margin-top: 0.25rem; }}
.stat-sub {{ color: #78716C; font-size: 12px; font-weight: 700; margin-top: 4px; }}

.cfo-caption {{ color: #78716C; font-size: 0.85rem; font-style: italic; margin-top: -10px; margin-bottom: 15px; }}

.section-header {{ font-weight: 900; font-size: 14px; color: #1F2937; margin: 18px 0 8px 0; }}
</style>
        """,
        unsafe_allow_html=True,
    )

    logo_path = Path("assets/logo_wit.png")
    st.markdown(
        f"""
<div class="header-box">
  <div class="header-text">
    <h1>{strings["app_title"]}</h1>
  </div>
  {img_base64(logo_path)}
</div>
        """,
        unsafe_allow_html=True,
    )

    col_in, col_out = st.columns([1, 2], gap="large")

    with col_in:
        st.subheader("Diagnose")

        cur_rev = st.number_input("Huidige jaaromzet (€)", value=500_000, step=25_000)
        order_val = st.number_input("Huidige omzet per order (€)", value=5_000, step=500, min_value=1)
        margin_euro = st.number_input("Huidige marge per order (€)", value=1_500, step=100, min_value=0)

        margin_pct = (margin_euro / order_val * 100) if order_val > 0 else 0
        st.markdown(f'<p class="cfo-caption">Bruto marge percentage: {margin_pct:.1f}%</p>', unsafe_allow_html=True)

        growth_pct = st.slider("Gewenste groei ambitie (%)", 0, 200, 25)

        st.divider()
        st.subheader("De Machine")

        pkg_options = {
            "Start & Connect — €595 p/m": 595,
            "Engage & Grow — €1750 p/m": 1750,
            "Lead & Scale — €2250 p/m": 2250,
        }
        pkg_label = st.selectbox("Pakket selectie", list(pkg_options.keys()), index=1)
        monthly_cost = pkg_options[pkg_label]

        setup_fee = 750
        st.caption(f"Inschrijffee (niet aanpasbaar): €{setup_fee:,.0f}".replace(",", "."))

        duration = st.number_input("Contractduur (maanden)", min_value=6, value=6, step=1)

        st.markdown("### Conversie validatie (6 maanden)")

        appts_in_6m = st.number_input(
            "Aantal gekwalificeerde afspraken (minimaal 12 in 6 maanden)",
            min_value=12,
            value=12,
            step=1,
        )

        closings_per_10 = st.number_input(
            "Hoeveel klanten haalt u gemiddeld uit 10 gekwalificeerde afspraken?",
            min_value=0,
            max_value=10,
            value=2,
            step=1,
        )

        success_rate = (closings_per_10 / 10) if closings_per_10 is not None else 0
        st.markdown(
            f'<p class="cfo-caption">Gevalideerde closing ratio: {success_rate * 100:.1f}% (gebaseerd op uw antwoord).</p>',
            unsafe_allow_html=True,
        )

        returns_per_year = st.number_input(
            "Hoe vaak komt een klant gemiddeld per jaar terug?",
            min_value=0,
            value=0,
            step=1,
            help="Deze frequentie wordt meegenomen in de omzet- en marge-berekening.",
        )

        retention = 100 if returns_per_year >= 1 else 0
        st.markdown(f'<p class="cfo-caption">Returning customer rate: {retention}%</p>', unsafe_allow_html=True)

    order_count_per_customer = 1 + returns_per_year
    revenue_per_customer_year = order_val * order_count_per_customer
    margin_per_customer_year = margin_euro * order_count_per_customer

    target_extra_revenue = cur_rev * (growth_pct / 100)

    deals_needed_growth = math.ceil(target_extra_revenue / revenue_per_customer_year) if revenue_per_customer_year > 0 else 0
    appts_needed_for_target = math.ceil(deals_needed_growth / success_rate) if success_rate > 0 else 0

    expected_customers = math.floor(appts_in_6m * success_rate)
    expected_revenue_scenario = expected_customers * revenue_per_customer_year
    expected_profit_scenario = expected_customers * margin_per_customer_year

    potential_customers = appts_in_6m
    potential_profit_scenario = potential_customers * margin_per_customer_year

    potential_revenue_scenario = potential_customers * revenue_per_customer_year

    total_investment = setup_fee + (duration * monthly_cost)

    roi_pct = ((expected_profit_scenario - total_investment) / total_investment) * 100 if total_investment > 0 else 0

    break_even_deals = math.ceil(total_investment / margin_per_customer_year) if margin_per_customer_year > 0 else 0
    deals_needed_campaign = break_even_deals + 1
    be_months = math.ceil(total_investment / (expected_profit_scenario / 12)) if expected_profit_scenario > 0 else 0

    period_factor = duration / 12
    n_leads_year = 5200
    n_connecties_year = 2160
    n_newsletter_year = 100

    pkg_name_for_title = pkg_label.split(" — ")[0]
    extra_md = ""
    if pkg_label.startswith("Engage"):
        extra_md = benefits_engage_md
    elif pkg_label.startswith("Lead"):
        extra_md = benefits_engage_md + ("\n" if benefits_engage_md.strip() else "") + benefits_lead_md

    with col_out:
        st.subheader("Conclusie")

        stats = [
            (
                "Potentiële omzet",
                f"€{potential_revenue_scenario:,.0f}".replace(",", "."),
                f"(verwacht €{expected_revenue_scenario:,.0f}".replace(",", ".") + " op basis van closing rate)",
            ),
            ("Investering (m)", f"€{total_investment:,.0f}".replace(",", ".") + f" ({duration}m)", ""),
            ("Marge", f"{margin_pct:.1f}%", ""),
            ("ROI", f"{roi_pct:.0f}%", ""),
            ("Deals nodig voor de % groei ambitie", f"{deals_needed_growth}", ""),
            ("Deals nodig voor de campagne (winst)", f"{deals_needed_campaign}", ""),
        ]

        rows = [stats[:3], stats[3:]]
        for row in rows:
            c1, c2, c3 = st.columns(3)
            for (label, value, sub), col in zip(row, [c1, c2, c3]):
                col.markdown(
                    f'''<div class="stat-card">
<div class="stat-label">{label}</div>
<div class="stat-value">{value}</div>
{"<div class='stat-sub'>" + sub + "</div>" if sub else ""}
</div>''',
                    unsafe_allow_html=True,
                )

        st.markdown(
            f"""
**Expected (op basis van uw closing):** {expected_customers} klanten in 6 maanden → marge {margin_pct:.1f}% over {order_count_per_customer} orders per klant per jaar → winst ≈ €{expected_profit_scenario:,.0f}  
**Potential (als alle {appts_in_6m} vallen):** {potential_customers} klanten → winst ≈ €{potential_profit_scenario:,.0f}
            """
        )

        fig_funnel = go.Figure(
            go.Funnel(
                y=["Gekwalificeerde afspraken", "Klanten (expected)", "Klanten (potential)"],
                x=[appts_in_6m, expected_customers, potential_customers],
                textinfo="value",
                marker={"color": [
                    theme.get("funnel_outreach_color", "#78716C"),
                    theme.get("funnel_expected_color", "#A8A29E"),
                    theme.get("funnel_potential_color", "#D97706"),
                ]},
            )
        )
        fig_funnel.update_layout(
            title="Business funnel (6 maanden → omzet/jaar)",
            height=320,
            margin=dict(t=50, b=20, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_funnel, use_container_width=True)

        # Afbeelding (config)
        result_img_path = Path(theme.get("result_image", "assets/slide8.png"))
        if result_img_path.exists():
            st.image(str(result_img_path), use_container_width=True)

        st.subheader(f"Extra voordelen bij {pkg_name_for_title}")
        if benefits_base_md.strip():
            st.markdown(benefits_base_md)
        if extra_md.strip():
            st.markdown(extra_md)

        st.markdown(
            f"""
**Basis cijfers (op contractduur: {duration} maanden):**
- Kwalitatieve leads: **{int(n_leads_year * period_factor)}**
- Kwalitatieve connecties: **{int(n_connecties_year * period_factor)}**
- Warme connecties in nieuwsbrief: **{int(n_newsletter_year * period_factor)}**
            """
        )

        st.markdown(
            f"""
---
**Break-even (verwacht):** {be_months} maanden  
*(Returning frequency is meegenomen: {returns_per_year} extra orders per klant per jaar. Returning customer rate automatisch: {retention}%.)*
            """
        )

with tab_editor:
    st.subheader("Editor")

    with st.form("editor_form"):
        st.write("Kleuren & layout")
        header_bg = st.color_picker("Header achtergrond", theme.get("header_bg", "#8BD3C0"))
        header_text = st.color_picker("Header tekstkleur", theme.get("header_text", "#111827"))
        stat_card_min_height = st.number_input(
            "Min. hoogte stat cards (px)", min_value=80, max_value=300, value=int(theme.get("stat_card_min_height", 140))
        )

        st.write("Funnel kleuren")
        funnel_outreach_color = st.color_picker(
            "Funnel kleur: gekwalificeerde afspraken", theme.get("funnel_outreach_color", "#78716C")
        )
        funnel_expected_color = st.color_picker(
            "Funnel kleur: klanten (expected)", theme.get("funnel_expected_color", "#A8A29E")
        )
        funnel_potential_color = st.color_picker(
            "Funnel kleur: klanten (potential)", theme.get("funnel_potential_color", "#D97706")
        )

        st.write("Tekst")
        app_title = st.text_input("App titel", strings.get("app_title", "Link & Lead ROI calculator"))

        st.write("Afbeelding (timeline)")
        result_image_path_edit = st.text_input("Afbeelding pad", theme.get("result_image", "assets/slide8.png"))

        uploaded_file = st.file_uploader("Upload nieuwe afbeelding (png/jpg)", type=["png", "jpg", "jpeg"])
        uploaded_save_path = None
        if uploaded_file:
            uploaded_bytes = uploaded_file.getvalue()
            out_path = ASSETS_DIR / uploaded_file.name
            out_path.write_bytes(uploaded_bytes)
            uploaded_save_path = str(out_path)

        st.write("Benefits markdown")
        base_md_edit = st.text_area("Benefits base (markdown)", benefits_base_md, height=160)
        engage_md_edit = st.text_area("Benefits Engage & Grow extra (markdown)", benefits_engage_md, height=120)
        lead_md_edit = st.text_area("Benefits Lead & Scale extra (markdown)", benefits_lead_md, height=120)

        saved = st.form_submit_button("Save (config/)")
        if saved:
            theme_save = {
                "header_bg": header_bg,
                "header_text": header_text,
                "stat_card_min_height": stat_card_min_height,

                "funnel_outreach_color": funnel_outreach_color,
                "funnel_expected_color": funnel_expected_color,
                "funnel_potential_color": funnel_potential_color,

                "result_image": uploaded_save_path if uploaded_save_path else result_image_path_edit,
            }
            strings_save = {"app_title": app_title}

            try:
                save_json(CONFIG_DIR / "theme.json", theme_save)
                save_json(CONFIG_DIR / "strings.json", strings_save)
                save_text(CONFIG_DIR / "benefits_base.md", base_md_edit)
                save_text(CONFIG_DIR / "benefits_engage.md", engage_md_edit)
                save_text(CONFIG_DIR / "benefits_lead.md", lead_md_edit)
                st.success("Config saved ✅")
            except Exception as e:
                st.error(f"Opslaan mislukt: {e}")



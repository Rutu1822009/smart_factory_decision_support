import streamlit as st
import pandas as pd
import textwrap

from agents.agent_controller import run_agent

from rag_assistant import (
    load_pdf_text,
    create_chunks,
    search_document
)

from forecast import (
    forecast_production,
    evaluate_model
)
from alerts import generate_alerts
from what_if import calculate_impact




# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Smart Factory DSS",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ==============================
       MAIN PAGE
    ============================== */

    .main {
        background-color: #f5f7fa;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }


    /* ==============================
       DASHBOARD HEADER
    ============================== */

    .dashboard-header {
        background: linear-gradient(135deg, #eff6ff, #dbeafe);
        padding: 24px 28px;
        border-radius: 18px;
        border: 1px solid #bfdbfe;
        box-shadow: 0 5px 18px rgba(37, 99, 235, 0.08);
        margin-bottom: 22px;
    }

    .main-title {
        font-size: 40px;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }

    .subtitle {
        font-size: 17px;
        color: #475569;
        margin-bottom: 5px;
    }


    /* ==============================
       KPI CARDS
    ============================== */

    .kpi-card {
        background: white;
        padding: 20px 22px;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        border-top: 4px solid #2563eb;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        min-height: 120px;
        transition: all 0.2s ease;
    }

    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(37,99,235,0.12);
    }

    .kpi-title {
        font-size: 14px;
        font-weight: 600;
        color: #64748b;
        margin-bottom: 10px;
    }

    .kpi-value {
        font-size: 30px;
        font-weight: 750;
        color: #0f172a;
    }


    /* ==============================
       SECTION HEADERS
    ============================== */

    .section-header {
        font-size: 23px;
        font-weight: 700;
        color: #111827;
        margin-top: 25px;
        margin-bottom: 15px;
    }


    /* ==============================
       FACTORY STATUS CARD
    ============================== */

    .status-card {
        background: white;
        padding: 18px 22px;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 3px 12px rgba(0,0,0,0.06);
        margin-bottom: 20px;
    }

    .status-title {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 5px;
    }

    .status-value {
        font-size: 22px;
        font-weight: 700;
        color: #111827;
    }


    /* ==============================
       MANAGEMENT RISK BOXES
    ============================== */

    .risk-box {
        padding: 16px 20px;
        border-radius: 14px;
        margin-bottom: 12px;
        border: 1px solid;
        font-size: 15px;
    }

    .risk-box strong {
        font-size: 17px;
    }

    .risk-high {
        background: #fef2f2;
        border-color: #fecaca;
        color: #991b1b;
    }

    .risk-medium {
        background: #fff7ed;
        border-color: #fed7aa;
        color: #9a3412;
    }

    .risk-low {
        background: #f0fdf4;
        border-color: #bbf7d0;
        color: #166534;
    }


    /* ==============================
       SIDEBAR
    ============================== */

    section[data-testid="stSidebar"] {
        background-color: #111827;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {
        color: white !important;
    }


    /* ==============================
       BUTTONS
    ============================== */

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 8px 18px;
    }


    /* ==============================
       DATAFRAME
    ============================== */

    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }


    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# LOAD DATA
# ============================================================

try:

    production = pd.read_csv("data/production.csv")
    machines = pd.read_csv("data/machines.csv")
    inventory = pd.read_csv("data/inventory.csv")
    quality = pd.read_csv("data/quality.csv")
    cost = pd.read_csv("data/cost.csv")
    energy = pd.read_csv("data/energy.csv")

except Exception as e:

    st.error(f"❌ Unable to load factory data: {e}")
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    """
    <div style="text-align:center;">
        <div style="font-size:45px;">🏭</div>
        <h2>Smart Factory</h2>
        <p>Decision Support Assistant</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "📈 Production",
        "⚙️ Machines",
        "📦 Inventory",
        "✅ Quality",
        "💰 Cost Analysis",
        "🌱 Energy Monitoring",
        "🤖 AI Assistant",
        "📄 SOP Assistant",
        "🔮 What-If Analysis",
        "📷 Computer Vision"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    "🏭 Smart Manufacturing\n\n"
    "AI-powered decision support for "
    "production, machines, inventory, "
    "quality, cost and energy."
)


# ============================================================
# COMMON CALCULATIONS
# ============================================================

total_target = production["target"].sum()
total_produced = production["produced"].sum()

if total_target > 0:
    production_percentage = (
        total_produced / total_target
    ) * 100
else:
    production_percentage = 0

running_machines = (
    machines["status"] == "Running"
).sum()

stopped_machines = (
    machines["status"] == "Stopped"
).sum()

total_machines = len(machines)

low_stock = inventory[
    inventory["current_stock"] < inventory["min_stock"]
]

low_stock_count = len(low_stock)

total_products = quality["total"].sum()
total_passed = quality["passed"].sum()
total_rejected = quality["rejected"].sum()

if total_products > 0:

    quality_percentage = (
        total_passed / total_products
    ) * 100

    defect_percentage = (
        total_rejected / total_products
    ) * 100

else:

    quality_percentage = 0
    defect_percentage = 0


if page == "🏠 Dashboard":

    st.markdown(
        '''
        <div class="dashboard-header">
            <div class="main-title">🏭 Smart Factory Dashboard</div>
            <div class="subtitle">
                AI-powered Factory Decision Support System
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-header">📊 Factory Overview</div>',
        unsafe_allow_html=True
    )

    # ========================================================
    # KPI CARDS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
     st.markdown(
        textwrap.dedent(f"""
        <div class="kpi-card">
            <div class="kpi-title">📈 Production Achievement</div>
            <div class="kpi-value">{production_percentage:.1f}%</div>
        </div>
        """),
        unsafe_allow_html=True
    )

    with col2:
     st.markdown(
        textwrap.dedent(f"""
        <div class="kpi-card">
            <div class="kpi-title">⚙️ Running Machines</div>
            <div class="kpi-value">{running_machines}/{total_machines}</div>
        </div>
        """),
        unsafe_allow_html=True
    )

    with col3:
     st.markdown(
        textwrap.dedent(f"""
        <div class="kpi-card">
            <div class="kpi-title">📦 Low Stock Materials</div>
            <div class="kpi-value">{low_stock_count}</div>
        </div>
        """),
        unsafe_allow_html=True
    )

    with col4:
     st.markdown(
        textwrap.dedent(f"""
        <div class="kpi-card">
            <div class="kpi-title">✅ Quality Pass Rate</div>
            <div class="kpi-value">{quality_percentage:.1f}%</div>
        </div>
        """),
        unsafe_allow_html=True
    )

    # ========================================================
    # MANAGEMENT DECISION SUPPORT
    # ========================================================

    st.markdown(
    '<div class="section-header">'
    '🎯 Management Decision Support'
    '</div>',
    unsafe_allow_html=True
)

    st.info(
    "💡 The system automatically identifies major factory "
    "risks and provides recommended actions."
)


    # ========================================================
    # FIND HIGHEST DOWNTIME MACHINE
    # ========================================================

    if not machines.empty:

        highest_downtime_row = machines.loc[
            machines["downtime_hours"].idxmax()
        ]

        highest_downtime_machine = str(
            highest_downtime_row["machine"]
        )

        highest_downtime_hours = float(
            highest_downtime_row["downtime_hours"]
        )

    else:

        highest_downtime_machine = "N/A"
        highest_downtime_hours = 0


    # ========================================================
    # PRODUCTION RISK
    # ========================================================

    if production_percentage < 90:

        st.error(
            f"""
            📈 **Production Risk: 🔴 HIGH**

            **Current Achievement:** {production_percentage:.2f}%

            **Recommended Action:**  
            Increase production efficiency and identify the
            reason for the production shortfall.
            """
        )

    else:

        st.success(
            f"""
            📈 **Production Risk: 🟢 LOW**

            **Current Achievement:** {production_percentage:.2f}%

            **Recommended Action:**  
            Maintain the current production performance.
            """
        )


    # ========================================================
    # MACHINE RISK
    # ========================================================

    if highest_downtime_hours >= 10:

        st.error(
            f"""
            ⚙️ **Machine Risk: 🔴 HIGH**

            **Highest Downtime Machine:** {highest_downtime_machine}

            **Downtime:** {highest_downtime_hours:.1f} hours

            **Recommended Action:**  
            Inspect {highest_downtime_machine} and schedule
            preventive maintenance.
            """
        )

    elif highest_downtime_hours >= 5:

        st.warning(
            f"""
            ⚙️ **Machine Risk: 🟠 MEDIUM**

            **Highest Downtime Machine:** {highest_downtime_machine}

            **Downtime:** {highest_downtime_hours:.1f} hours

            **Recommended Action:**  
            Inspect the machine and monitor downtime closely.
            """
        )

    else:

        st.success(
            f"""
            ⚙️ **Machine Risk: 🟢 LOW**

            **Highest Downtime Machine:** {highest_downtime_machine}

            **Downtime:** {highest_downtime_hours:.1f} hours

            **Recommended Action:**  
            Continue regular machine monitoring.
            """
        )


    # ========================================================
    # INVENTORY RISK
    # ========================================================

    if low_stock_count > 0:

        st.error(
            f"""
            📦 **Inventory Risk: 🔴 HIGH**

            **Low Stock Materials:** {low_stock_count}

            **Recommended Action:**  
            Reorder the {low_stock_count} low-stock material(s)
            before production is affected.
            """
        )

    else:

        st.success(
            """
            📦 **Inventory Risk: 🟢 LOW**

            **Low Stock Materials:** 0

            **Recommended Action:**  
            Continue regular inventory monitoring.
            """
        )


    # ========================================================
    # QUALITY RISK
    # ========================================================

    if defect_percentage >= 5:

        st.error(
            f"""
            ✅ **Quality Risk: 🔴 HIGH**

            **Defect Rate:** {defect_percentage:.2f}%

            **Recommended Action:**  
            Improve quality inspection and perform
            root-cause analysis.
            """
        )

    else:

        st.success(
            f"""
            ✅ **Quality Risk: 🟢 LOW**

            **Defect Rate:** {defect_percentage:.2f}%

            **Recommended Action:**  
            Maintain the current quality-control process.
            """
        )


    # ========================================================
    # COST RISK
    # ========================================================

    total_material_cost = cost["material_cost"].sum()
    total_defect_cost = cost["defect_cost"].sum()
    total_energy_cost = cost["energy_cost"].sum()

    cost_risk = False

    if total_material_cost > 0:

        if total_defect_cost > total_material_cost * 0.05:
            cost_risk = True

        if total_energy_cost > total_material_cost * 0.25:
            cost_risk = True

    if cost_risk:

        st.warning(
            f"""
            💰 **Cost Risk: 🟠 MEDIUM**

            **Defect Cost:** ₹{total_defect_cost:,.2f}

            **Energy Cost:** ₹{total_energy_cost:,.2f}

            **Recommended Action:**  
            Reduce defect-related costs by improving quality
            inspection and root-cause analysis.
            """
        )

    else:

        st.success(
            f"""
            💰 **Cost Risk: 🟢 LOW**

            **Defect Cost:** ₹{total_defect_cost:,.2f}

            **Energy Cost:** ₹{total_energy_cost:,.2f}

            **Recommended Action:**  
            Continue monitoring production and operating costs.
            """
        )


    # ========================================================
    # OVERALL MANAGEMENT RECOMMENDATION
    # ========================================================

    st.markdown("---")

    st.markdown(
        '<div class="section-header">'
        '🧠 Overall Management Recommendation'
        '</div>',
        unsafe_allow_html=True
    )

    critical_risks = []

    if highest_downtime_hours >= 10:
        critical_risks.append("machine downtime")

    if low_stock_count > 0:
        critical_risks.append("inventory")

    if defect_percentage >= 5:
        critical_risks.append("quality")

    if cost_risk:
        critical_risks.append("cost")

    if critical_risks:

        risk_text = ", ".join(critical_risks)

        st.error(
            f"""
            🚨 **Immediate Management Attention Required**

            Critical risk areas detected: **{risk_text}**

            Management should prioritize these areas to avoid
            production interruption, quality problems and
            financial losses.
            """
        )

    else:

        st.success(
            """
            ✅ **Factory Operations Stable**

            No critical operational risks were detected.
            Continue regular monitoring and preventive maintenance.
            """
        )


    # ========================================================
    # FACTORY DECISION SUMMARY
    # ========================================================

    st.markdown("---")

    st.markdown(
        '<div class="section-header">'
        '🧠 Factory Decision Summary'
        '</div>',
        unsafe_allow_html=True
    )

    if production_percentage < 90:

        st.warning(
            "⚠️ Production is below the expected target."
        )

    else:

        st.success(
            "✅ Production performance is satisfactory."
        )

    if low_stock_count > 0:

        st.warning(
            f"📦 {low_stock_count} material(s) require attention."
        )

    else:

        st.success(
            "✅ Inventory levels are healthy."
        )

    if stopped_machines > 0:

        st.warning(
            f"⚙️ {stopped_machines} machine(s) are currently stopped."
        )

    else:

        st.success(
            "✅ All machines are currently running."
        )

    if defect_percentage >= 5:

        st.error(
            "❌ Defect rate requires quality-team attention."
        )

    else:

        st.success(
            "✅ Quality performance is within acceptable range."
        )


    # ========================================================
    # SMART ALERTS
    # ========================================================

    st.markdown("---")

    st.markdown(
        '<div class="section-header">⚠️ Smart Alerts</div>',
        unsafe_allow_html=True
    )
    st.caption(
    "Real-time alerts highlighting important factory risks and operational issues."
)

    try:

        alerts = generate_alerts()

        if alerts:

            for alert in alerts:

                if str(alert).startswith("🔴"):
                    st.error(alert)

                elif str(alert).startswith("🟠"):
                    st.warning(alert)

                elif str(alert).startswith("🟡"):
                    st.warning(alert)

                else:
                    st.info(alert)

        else:

            st.success(
                "✅ No critical alerts. Factory is operating normally."
            )

    except Exception as e:

        st.warning(
            f"⚠️ Smart alerts unavailable: {e}"
        )


    # ========================================================
    # AI RECOMMENDATIONS
    # ========================================================

    st.markdown("---")

    st.markdown(
        '<div class="section-header">'
        '🤖 AI Recommendations'
        '</div>',
        unsafe_allow_html=True
    )
    st.caption(
    "AI-generated recommendations to support faster management decisions."
)

    try:

        highest_defect_line = quality.groupby(
            "line"
        )["defect_rate"].mean().idxmax()

    except Exception:

        highest_defect_line = "Quality Line"

    st.info(
        f"🔧 Inspect **{highest_downtime_machine}** because "
        f"it has the highest downtime "
        f"({highest_downtime_hours:.1f} hours)."
    )

    if low_stock_count > 0:

        st.warning(
            f"📦 Reorder the {low_stock_count} low-stock "
            "material(s) to avoid production interruption."
        )

    st.info(
        f"✅ Increase quality inspection on "
        f"**{highest_defect_line}**."
    )


    # ==================================================
    # ML PRODUCTION FORECAST
    # ==================================================

    st.markdown("---")

    st.markdown(
    '<div class="section-header">'
    '🔮 ML-Based Production Forecast'
    '</div>',
    unsafe_allow_html=True
)

    st.info(
        "Machine Learning Model: Random Forest Regression"
    )

    try:

        prediction = forecast_production()

        latest_date = production["date"].max()

        next_day_target = production[
            production["date"] == latest_date
        ]["target"].sum()

        predicted_achievement = (
            prediction / next_day_target
        ) * 100

        difference = (
            prediction - next_day_target
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "🔮 ML Predicted Production",
                f"{prediction:,} units"
            )

        with col2:
            st.metric(
                "🎯 Next Day Target",
                f"{next_day_target:,} units"
            )

        with col3:
            st.metric(
                "📊 Expected Achievement",
                f"{predicted_achievement:.2f}%"
            )

        # ==================================================
        # ML MODEL PERFORMANCE
        # ==================================================

        mae, r2 = evaluate_model()

        st.markdown("---")

        st.subheader("📊 ML Model Performance")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "MAE",
                f"{mae:.2f} units"
            )

        with col2:
            st.metric(
                "R² Score",
                f"{r2:.2f}"
            )

        st.caption(
            "MAE shows the average prediction error in units. "
            "R² indicates how well the model fits the available "
            "historical data."
        )

        # ==================================================
        # DECISION SUPPORT
        # ==================================================

        if difference < 0:

            shortfall = abs(difference)

            st.warning(
                f"⚠️ ML Forecast Alert: "
                f"Production may be approximately "
                f"{shortfall:,} units below target."
            )

        else:

            surplus = difference

            st.success(
                f"✅ ML Forecast Status: "
                f"Production may be approximately "
                f"{surplus:,} units above target."
            )

    except Exception as e:

        st.error(
            f"ML Forecast unavailable: {e}"
        )

    
# ============================================================
# PRODUCTION
# ============================================================

elif page == "📈 Production":

    st.markdown(
    '<div class="section-header">📈 Production Analysis</div>',
    unsafe_allow_html=True
)

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "🎯 Total Target",
            f"{total_target:,}"
        )

    with col2:

        st.metric(
            "🏭 Total Produced",
            f"{total_produced:,}"
        )

    with col3:

        st.metric(
            "📊 Achievement",
            f"{production_percentage:.2f}%"
        )

    st.markdown("---")

    st.subheader("📈 Production Trend")

    try:

        production_chart = production.groupby(
            "date"
        )[["target", "produced"]].sum()

        st.line_chart(production_chart)

    except Exception as e:

        st.error(
            f"Unable to create production chart: {e}"
        )

    st.markdown("---")

    st.subheader("📋 Production Data")

    st.dataframe(
        production,
        use_container_width=True
    )


# ============================================================
# MACHINES
# ============================================================

elif page == "⚙️ Machines":

    st.markdown(
    '<div class="section-header">⚙️ Machine Monitoring</div>',
    unsafe_allow_html=True
)

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "🏭 Total Machines",
            total_machines
        )

    with col2:

        st.metric(
            "🟢 Running",
            running_machines
        )

    with col3:

        st.metric(
            "🔴 Stopped",
            stopped_machines
        )

    st.markdown("---")

    st.subheader("⚙️ Machine Status")

    st.dataframe(
        machines,
        use_container_width=True
    )

    st.markdown("---")

    if not machines.empty:

        highest_downtime = machines.loc[
            machines["downtime_hours"].idxmax()
        ]

        st.warning(
            f"⚠️ Highest downtime: "
            f"{highest_downtime['machine']} "
            f"({float(highest_downtime['downtime_hours']):.1f} hours)"
        )


# ============================================================
# INVENTORY
# ============================================================

elif page == "📦 Inventory":

    st.markdown(
    '<div class="section-header">📦 Inventory Analysis</div>',
    unsafe_allow_html=True
)

    st.metric(
        "⚠️ Low Stock Materials",
        low_stock_count
    )

    st.markdown("---")

    st.dataframe(
        inventory,
        use_container_width=True
    )

    st.markdown("---")

    st.subheader("🧠 Inventory Recommendations")

    if low_stock_count > 0:

        for _, row in low_stock.iterrows():

            st.warning(
                f"📦 **{row['material']}** is below minimum stock. "
                f"Current: {row['current_stock']} | "
                f"Minimum: {row['min_stock']}"
            )

    else:

        st.success(
            "✅ All materials have sufficient stock."
        )


# ============================================================
# QUALITY
# ============================================================

elif page == "✅ Quality":

    st.markdown(
    '<div class="section-header">✅ Quality Analysis</div>',
    unsafe_allow_html=True
)

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "📦 Total Products",
            f"{total_products:,}"
        )

    with col2:

        st.metric(
            "✅ Passed",
            f"{total_passed:,}"
        )

    with col3:

        st.metric(
            "❌ Rejected",
            f"{total_rejected:,}"
        )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "✅ Quality Pass Rate",
            f"{quality_percentage:.2f}%"
        )

    with col2:

        st.metric(
            "❌ Defect Rate",
            f"{defect_percentage:.2f}%"
        )

    st.markdown("---")

    st.dataframe(
        quality,
        use_container_width=True
    )


# ============================================================
# COST ANALYSIS
# ============================================================

elif page == "💰 Cost Analysis":

    st.markdown(
    '<div class="section-header">💰 Cost Analysis</div>',
    unsafe_allow_html=True
)

    total_material = cost["material_cost"].sum()
    total_labor = cost["labor_cost"].sum()
    total_energy_cost_page = cost["energy_cost"].sum()
    total_defect = cost["defect_cost"].sum()

    total_cost = (
        total_material
        + total_labor
        + total_energy_cost_page
        + total_defect
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "📦 Material Cost",
            f"₹{total_material:,.2f}"
        )

    with col2:

        st.metric(
            "👷 Labor Cost",
            f"₹{total_labor:,.2f}"
        )

    with col3:

        st.metric(
            "⚡ Energy Cost",
            f"₹{total_energy_cost_page:,.2f}"
        )

    with col4:

        st.metric(
            "❌ Defect Cost",
            f"₹{total_defect:,.2f}"
        )

    st.markdown("---")

    st.metric(
        "💰 Total Production Cost",
        f"₹{total_cost:,.2f}"
    )

    st.markdown("---")

    st.subheader("📊 Daily Cost Trend")

    try:

        daily_cost = cost.set_index("date")[
            [
                "material_cost",
                "labor_cost",
                "energy_cost",
                "defect_cost"
            ]
        ]

        st.line_chart(daily_cost)

    except Exception as e:

        st.error(
            f"Unable to create cost chart: {e}"
        )

    st.markdown("---")

    st.subheader("💡 Cost Recommendations")

    if (
        total_material > 0
        and total_defect > total_material * 0.05
    ):

        st.warning(
            "⚠️ Defect cost is relatively high. "
            "Improve quality inspection and identify "
            "the root cause of defects."
        )

    if (
        total_material > 0
        and total_energy_cost_page > total_material * 0.25
    ):

        st.info(
            "⚡ Energy cost is significant. "
            "Consider energy-efficient machine operation."
        )

    st.success(
        "✅ Monitor material, energy and defect costs "
        "regularly to improve factory efficiency."
    )


# ============================================================
# ENERGY MONITORING
# ============================================================

elif page == "🌱 Energy Monitoring":

    st.markdown(
    '<div class="section-header">🌱 Energy Consumption Monitoring</div>',
    unsafe_allow_html=True
)

    total_energy = energy["energy_kwh"].sum()

    average_energy = energy["energy_kwh"].mean()

    machine_energy_grouped = (
        energy.groupby("machine")["energy_kwh"]
        .sum()
    )

    if not machine_energy_grouped.empty:

        highest_machine = machine_energy_grouped.idxmax()

        highest_machine_energy = (
            machine_energy_grouped.max()
        )

    else:

        highest_machine = "N/A"
        highest_machine_energy = 0

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "⚡ Total Energy",
            f"{total_energy:,.2f} kWh"
        )

    with col2:

        st.metric(
            "📊 Average Consumption",
            f"{average_energy:.1f} kWh"
        )

    with col3:

        st.metric(
            "⚠️ Highest Consumer",
            highest_machine
        )

    st.markdown("---")

    st.subheader(
        "⚡ Machine-wise Energy Consumption"
    )

    machine_energy = (
        energy.groupby("machine")["energy_kwh"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(machine_energy)

    st.markdown("---")

    st.subheader(
        "📈 Energy Consumption Trend"
    )

    daily_energy = (
        energy.groupby("date")["energy_kwh"]
        .sum()
    )

    st.line_chart(daily_energy)

    st.markdown("---")

    st.subheader(
        "💡 Energy Saving Recommendation"
    )

    st.warning(
        f"{highest_machine} is consuming the highest "
        f"amount of energy "
        f"({highest_machine_energy:,.2f} kWh). "
        "Consider checking operating hours, machine efficiency "
        "and unnecessary idle operation."
    )

    st.markdown("---")

    st.dataframe(
        energy,
        use_container_width=True
    )


# ============================================================
# AI ASSISTANT
# ============================================================

elif page == "🤖 AI Assistant":
    if "agent_chat_history" not in st.session_state:
       st.session_state.agent_chat_history = []

    st.title("🤖 Factory AI Assistant")

    st.write(
        "Ask questions about production, machines, "
        "inventory and quality."
    )

    question = st.text_input(
        "💬 Ask your question",
        placeholder=(
            "Example: Which machine has the highest downtime?"
        )
    )

    if st.button("🔍 Ask AI"):

        if question.strip():

            try:

                answer = run_agent(question)

                st.session_state.agent_chat_history.append(
    {
        "question": question,
        "answer": answer
    }
)


                st.markdown("### 🤖 AI Answer")

                st.markdown(answer)

            except Exception as e:

                st.error(
                    f"AI Assistant unavailable: {e}"
                )

        else:

            st.warning(
                "Please enter a question."
            )


# ============================================================
# SOP ASSISTANT
# ============================================================

elif page == "📄 SOP Assistant":

    st.title("📄 SOP & Manual Assistant")

    st.write(
        "Ask questions about the Machine Maintenance SOP."
    )

    if st.button("📄 Load SOP Document"):

        try:

            text = load_pdf_text(
                "documents/Machine_Maintenance_SOP.pdf"
            )

            chunks = create_chunks(text)

            st.session_state["sop_chunks"] = chunks

            st.success(
                f"✅ SOP loaded successfully! "
                f"{len(chunks)} sections found."
            )

        except Exception as e:

            st.error(
                f"Unable to load SOP: {e}"
            )

    question = st.text_input(
        "💬 Ask about the SOP",
        placeholder=(
            "Example: What are the safety precautions?"
        )
    )

    if question:

        if "sop_chunks" not in st.session_state:

            st.warning(
                "⚠️ Please load the SOP document first."
            )

        else:

            try:

                answer = search_document(
                    question,
                    st.session_state["sop_chunks"]
                )

                st.info(answer)

            except Exception as e:

                st.error(
                    f"SOP search failed: {e}"
                )


# ============================================================
# WHAT-IF ANALYSIS
# ============================================================

elif page == "🔮 What-If Analysis":

    st.title("🔮 What-If Analysis")

    st.write(
        "Simulate the possible impact of a machine shutdown "
        "on factory operations."
    )

    # ========================================================
    # MACHINE SELECTION
    # ========================================================

    machine_names = (
        machines["machine"]
        .dropna()
        .tolist()
    )

    if not machine_names:

        st.error(
            "❌ No machines found in machines.csv"
        )
        st.stop()

    selected_machine = st.selectbox(
        "⚙️ Select Machine",
        machine_names
    )

    shutdown_days = st.number_input(
        "📅 Shutdown Duration (Days)",
        min_value=1.0,
        max_value=30.0,
        value=2.0,
        step=1.0
    )

    # ========================================================
    # ANALYZE BUTTON
    # ========================================================

    if st.button(
        "🔮 Analyze Impact",
        type="primary"
    ):

        try:

            result = calculate_impact(
                selected_machine,
                shutdown_days
            )

            if result is None:

                st.error(
                    "❌ Machine information not found."
                )

            else:

                # =================================================
                # BASIC VALUES
                # =================================================

                machine_name = result.get(
                    "machine",
                    selected_machine
                )

                days = float(
                    result.get(
                        "days",
                        shutdown_days
                    )
                )

                existing_downtime = float(
                    result.get(
                        "existing_downtime",
                        0
                    )
                )

                shutdown_hours = float(
                    result.get(
                        "shutdown_hours",
                        days * 8
                    )
                )

                total_downtime = float(
                    result.get(
                        "total_downtime",
                        existing_downtime + shutdown_hours
                    )
                )

                estimated_loss = result.get(
                    "estimated_loss",
                    None
                )

                impact_percentage = result.get(
                    "impact_percentage",
                    None
                )

                cost_per_unit = result.get(
                    "cost_per_unit",
                    None
                )

                estimated_cost_impact = result.get(
                    "estimated_cost_impact",
                    None
                )


                # =================================================
                # IMPACT ANALYSIS
                # =================================================

                st.markdown("---")

                st.subheader(
                    "📊 Impact Analysis"
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "⚙️ Machine",
                        machine_name
                    )

                with col2:

                    st.metric(
                        "📅 Shutdown",
                        f"{days:g} days"
                    )

                with col3:

                    st.metric(
                        "⏱️ Total Downtime",
                        f"{total_downtime:.1f} hours"
                    )


                # =================================================
                # DOWNTIME DETAILS
                # =================================================

                st.markdown("---")

                st.subheader(
                    "⏱️ Downtime Details"
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "⏱️ Existing Downtime",
                        f"{existing_downtime:.1f} hours"
                    )

                with col2:

                    st.metric(
                        "🛑 Additional Shutdown",
                        f"{shutdown_hours:.1f} hours"
                    )


                # =================================================
                # PRODUCTION IMPACT
                # =================================================

                if estimated_loss is not None:

                    st.markdown("---")

                    st.subheader(
                        "📉 Production Impact"
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        try:

                            loss_value = float(
                                estimated_loss
                            )

                            loss_text = (
                                f"{loss_value:,.0f} units"
                            )

                        except Exception:

                            loss_text = str(
                                estimated_loss
                            )

                        st.metric(
                            "📦 Estimated Production Loss",
                            loss_text
                        )

                    with col2:

                        if impact_percentage is not None:

                            try:

                                impact_value = float(
                                    impact_percentage
                                )

                                impact_text = (
                                    f"{impact_value:.2f}%"
                                )

                            except Exception:

                                impact_text = str(
                                    impact_percentage
                                )

                        else:

                            impact_text = "N/A"

                        st.metric(
                            "📊 Factory Impact",
                            impact_text
                        )


                # =================================================
                # FINANCIAL IMPACT
                # =================================================

                if (
                    cost_per_unit is not None
                    or estimated_cost_impact is not None
                ):

                    st.markdown("---")

                    st.subheader(
                        "💰 Financial Impact"
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        if cost_per_unit is not None:

                            try:

                                cpu_value = float(
                                    cost_per_unit
                                )

                                cpu_text = (
                                    f"₹{cpu_value:,.2f}"
                                )

                            except Exception:

                                cpu_text = str(
                                    cost_per_unit
                                )

                        else:

                            cpu_text = "N/A"

                        st.metric(
                            "💰 Cost Per Unit",
                            cpu_text
                        )

                    with col2:

                        if estimated_cost_impact is not None:

                            try:

                                cost_value = float(
                                    estimated_cost_impact
                                )

                                cost_text = (
                                    f"₹{cost_value:,.2f}"
                                )

                            except Exception:

                                cost_text = str(
                                    estimated_cost_impact
                                )

                        else:

                            cost_text = "N/A"

                        st.metric(
                            "💸 Estimated Cost Impact",
                            cost_text
                        )


                # =================================================
                # SHUTDOWN IMPACT SUMMARY
                # =================================================

                st.markdown("---")

                st.subheader(
                    "⚠️ Shutdown Impact"
                )

                summary_text = (
                    f"""
                    If **{machine_name}** remains stopped for
                    **{days:g} days**:

                    **Existing Downtime:**  
                    {existing_downtime:.1f} hours

                    **Additional Shutdown:**  
                    {shutdown_hours:.1f} hours

                    **Estimated Total Downtime:**  
                    {total_downtime:.1f} hours
                    """
                )

                if estimated_loss is not None:

                    try:

                        summary_text += (
                            f"""

                            **Estimated Production Loss:**  
                            {float(estimated_loss):,.0f} units
                            """
                        )

                    except Exception:

                        summary_text += (
                            f"""

                            **Estimated Production Loss:**  
                            {estimated_loss}
                            """
                        )

                if impact_percentage is not None:

                    try:

                        summary_text += (
                            f"""

                            **Factory Production Impact:**  
                            {float(impact_percentage):.2f}%
                            """
                        )

                    except Exception:

                        summary_text += (
                            f"""

                            **Factory Production Impact:**  
                            {impact_percentage}
                            """
                        )

                if estimated_cost_impact is not None:

                    try:

                        summary_text += (
                            f"""

                            **Estimated Financial Impact:**  
                            ₹{float(estimated_cost_impact):,.2f}
                            """
                        )

                    except Exception:

                        summary_text += (
                            f"""

                            **Estimated Financial Impact:**  
                            {estimated_cost_impact}
                            """
                        )

                st.warning(summary_text)


                # =================================================
                # RECOMMENDATION
                # =================================================

                st.info(
                    """
                    💡 **Recommendation**

                    Shift production load to an available machine
                    if possible.

                    Schedule preventive maintenance for the selected
                    machine to reduce future downtime.

                    Monitor production and cost impact during the
                    shutdown period.
                    """
                )

        except Exception as e:

            st.error(
                f"❌ Unable to calculate shutdown impact: {e}"
            )

            st.info(
                "Please check the calculate_impact() function "
                "in what_if.py and make sure it returns the "
                "required impact values."
            )
          


# ============================================================
# END OF APPLICATION
# ============================================================
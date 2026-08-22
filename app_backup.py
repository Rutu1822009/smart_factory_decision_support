import streamlit as st
import pandas as pd

from ai_assistant import get_answer
from rag_assistant import (
    load_pdf_text,
    create_chunks,
    search_document
)
from forecast import forecast_production
from alerts import generate_alerts
from what_if import calculate_impact


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Smart Factory DSS",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

.main {
    background-color: #f5f7fa;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.main-title {
    font-size: 38px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 17px;
    color: #6b7280;
    margin-bottom: 25px;
}

.kpi-card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 3px 12px rgba(0,0,0,0.06);
    min-height: 125px;
}

.kpi-title {
    font-size: 14px;
    color: #6b7280;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 28px;
    font-weight: 700;
}

.section-header {
    font-size: 23px;
    font-weight: 650;
    margin-top: 15px;
    margin-bottom: 15px;
}

.recommendation {
    background: white;
    padding: 16px;
    border-radius: 12px;
    border-left: 5px solid #2563eb;
    margin-bottom: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

section[data-testid="stSidebar"] {
    background-color: #111827;
}

section[data-testid="stSidebar"] * {
    color: white;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# LOAD DATA
# ==================================================

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


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.markdown(
    """
    <div style="text-align:center;">
        <div style="font-size:45px;">🏭</div>
        <h2>Smart Factory</h2>
        <p>Decision Support System</p>
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
        "🔮 What-If Analysis"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    "🏭 Smart Manufacturing\n\n"
    "AI-powered decision support for "
    "production, machines, inventory, "
    "quality, cost and energy."
)


# ==================================================
# BASIC CALCULATIONS
# ==================================================

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


# ==================================================
# DASHBOARD
# ==================================================

if page == "🏠 Dashboard":

    st.markdown(
        '<div class="main-title">'
        '🏭 Smart Factory Dashboard'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'AI-powered Factory Decision Support System'
        '</div>',
        unsafe_allow_html=True
    )


    # ==================================================
    # KPI CARDS
    # ==================================================

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">
                    📈 Production Achievement
                </div>
                <div class="kpi-value">
                    {production_percentage:.1f}%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">
                    ⚙️ Running Machines
                </div>
                <div class="kpi-value">
                    {running_machines}/{total_machines}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col3:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">
                    📦 Low Stock Materials
                </div>
                <div class="kpi-value">
                    {low_stock_count}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col4:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">
                    ✅ Quality Pass Rate
                </div>
                <div class="kpi-value">
                    {quality_percentage:.1f}%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    # ==================================================
    # DECISION SUMMARY
    # ==================================================

    st.markdown("---")

    st.markdown(
        '<div class="section-header">'
        '🧠 Factory Decision Summary'
        '</div>',
        unsafe_allow_html=True
    )


    summary_points = []


    if production_percentage < 90:

        summary_points.append(
            "⚠️ Production is below the expected target."
        )

    else:

        summary_points.append(
            "✅ Production performance is satisfactory."
        )


    if low_stock_count > 0:

        summary_points.append(
            f"📦 {low_stock_count} material(s) "
            "require attention."
        )

    else:

        summary_points.append(
            "✅ Inventory levels are healthy."
        )


    if stopped_machines > 0:

        summary_points.append(
            f"⚙️ {stopped_machines} machine(s) "
            "are currently stopped."
        )

    else:

        summary_points.append(
            "✅ All machines are currently running."
        )


    if defect_percentage >= 5:

        summary_points.append(
            "❌ Defect rate requires "
            "quality-team attention."
        )

    else:

        summary_points.append(
            "✅ Quality performance is "
            "within acceptable range."
        )


    for point in summary_points:

        st.markdown(
            f"""
            <div class="recommendation">
                {point}
            </div>
            """,
            unsafe_allow_html=True
        )


    # ==================================================
    # SMART ALERTS
    # ==================================================

    st.markdown("---")

    st.markdown(
        '<div class="section-header">'
        '⚠️ Smart Alerts'
        '</div>',
        unsafe_allow_html=True
    )


    try:

        alerts = generate_alerts()

        if alerts:

            for alert in alerts:

                if alert.startswith("🔴"):

                    st.error(alert)

                elif alert.startswith("🟠"):

                    st.warning(alert)

                elif alert.startswith("🟡"):

                    st.warning(alert)

                else:

                    st.info(alert)

        else:

            st.success(
                "✅ No critical alerts. "
                "Factory is operating normally."
            )

    except Exception as e:

        st.warning(
            f"⚠️ Alerts unavailable: {e}"
        )


    # ==================================================
    # AI RECOMMENDATIONS
    # ==================================================

    st.markdown("---")

    st.markdown(
        '<div class="section-header">'
        '🤖 AI Recommendations'
        '</div>',
        unsafe_allow_html=True
    )


    if not machines.empty:

        highest_downtime_machine = machines.loc[
            machines["downtime_hours"].idxmax(),
            "machine"
        ]

        highest_downtime_hours = machines[
            "downtime_hours"
        ].max()

        st.markdown(
            f"""
            <div class="recommendation">
                🔧 <b>Machine Recommendation:</b><br>
                Inspect <b>{highest_downtime_machine}</b>.
                It has the highest downtime
                ({highest_downtime_hours} hours).
            </div>
            """,
            unsafe_allow_html=True
        )


    if low_stock_count > 0:

        st.markdown(
            """
            <div class="recommendation">
                📦 <b>Inventory Recommendation:</b><br>
                Reorder low-stock materials to avoid
                production interruption.
            </div>
            """,
            unsafe_allow_html=True
        )


    if not quality.empty:

        highest_defect_line = quality.groupby(
            "line"
        )["defect_rate"].mean().idxmax()

        st.markdown(
            f"""
            <div class="recommendation">
                ✅ <b>Quality Recommendation:</b><br>
                Increase quality inspection on
                <b>{highest_defect_line}</b>.
            </div>
            """,
            unsafe_allow_html=True
        )


    # ==================================================
    # PRODUCTION FORECAST
    # ==================================================

    st.markdown("---")

    st.markdown(
        '<div class="section-header">'
        '🔮 Production Forecast'
        '</div>',
        unsafe_allow_html=True
    )


    try:

        prediction = forecast_production()

        st.metric(
            "📈 Next Day Estimated Production",
            f"{prediction:,} units"
        )

    except Exception as e:

        st.error(
            f"Forecast unavailable: {e}"
        )


# ==================================================
# PRODUCTION
# ==================================================

elif page == "📈 Production":

    st.title("📈 Production Analysis")


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

        st.warning(
            f"Production chart unavailable: {e}"
        )


    st.markdown("---")

    st.subheader("📋 Production Data")

    st.dataframe(
        production,
        use_container_width=True
    )


# ==================================================
# MACHINES
# ==================================================

elif page == "⚙️ Machines":

    st.title("⚙️ Machine Monitoring")


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
            f"({highest_downtime['downtime_hours']} hours)"
        )


# ==================================================
# INVENTORY
# ==================================================

elif page == "📦 Inventory":

    st.title("📦 Inventory Analysis")


    st.metric(
        "⚠️ Low Stock Materials",
        low_stock_count
    )


    st.markdown("---")

    st.subheader("📋 Inventory Data")


    st.dataframe(
        inventory,
        use_container_width=True
    )


    st.markdown("---")

    st.subheader("🧠 Inventory Recommendations")


    if low_stock_count > 0:

        for _, row in low_stock.iterrows():

            st.warning(
                f"📦 **{row['material']}** is below "
                f"minimum stock. "
                f"Current: **{row['current_stock']}** | "
                f"Minimum: **{row['min_stock']}**"
            )

    else:

        st.success(
            "✅ All materials have sufficient stock."
        )


# ==================================================
# QUALITY
# ==================================================

elif page == "✅ Quality":

    st.title("✅ Quality Analysis")


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


    st.subheader("📋 Quality Data")


    st.dataframe(
        quality,
        use_container_width=True
    )


# ==================================================
# COST ANALYSIS
# ==================================================

elif page == "💰 Cost Analysis":

    st.title("💰 Cost Analysis")


    total_material = cost["material_cost"].sum()

    total_labor = cost["labor_cost"].sum()

    total_energy_cost = cost["energy_cost"].sum()

    total_defect = cost["defect_cost"].sum()


    total_cost = (
        total_material
        + total_labor
        + total_energy_cost
        + total_defect
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "📦 Material Cost",
            f"₹{total_material:,.0f}"
        )


    with col2:

        st.metric(
            "👷 Labor Cost",
            f"₹{total_labor:,.0f}"
        )


    with col3:

        st.metric(
            "⚡ Energy Cost",
            f"₹{total_energy_cost:,.0f}"
        )


    with col4:

        st.metric(
            "❌ Defect Cost",
            f"₹{total_defect:,.0f}"
        )


    st.markdown("---")


    st.metric(
        "💰 Total Production Cost",
        f"₹{total_cost:,.0f}"
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

        st.warning(
            f"Cost chart unavailable: {e}"
        )


    st.markdown("---")

    st.subheader("💡 Cost Recommendations")


    if total_material > 0:

        if total_defect > total_material * 0.05:

            st.warning(
                "⚠️ Defect cost is relatively high. "
                "Improve quality inspection and "
                "identify root causes."
            )


        if total_energy_cost > total_material * 0.25:

            st.info(
                "⚡ Energy cost is significant. "
                "Consider energy-efficient machine operation."
            )


    st.success(
        "✅ Monitor material, energy and defect costs "
        "regularly to improve factory efficiency."
    )


# ==================================================
# ENERGY MONITORING
# ==================================================

elif page == "🌱 Energy Monitoring":

    st.title("🌱 Energy Consumption Monitoring")


    total_energy = energy["energy_kwh"].sum()

    average_energy = energy["energy_kwh"].mean()


    if not energy.empty:

        highest_machine = (
            energy.groupby("machine")["energy_kwh"]
            .sum()
            .idxmax()
        )

        highest_machine_energy = (
            energy.groupby("machine")["energy_kwh"]
            .sum()
            .max()
        )

    else:

        highest_machine = "N/A"
        highest_machine_energy = 0


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "⚡ Total Energy",
            f"{total_energy:,.1f} kWh"
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

    st.subheader("⚡ Machine-wise Energy Consumption")


    try:

        machine_energy = (
            energy.groupby("machine")["energy_kwh"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(machine_energy)

    except Exception as e:

        st.warning(
            f"Energy chart unavailable: {e}"
        )


    st.markdown("---")

    st.subheader("📈 Energy Consumption Trend")


    try:

        daily_energy = (
            energy.groupby("date")["energy_kwh"]
            .sum()
        )

        st.line_chart(daily_energy)

    except Exception as e:

        st.warning(
            f"Energy trend unavailable: {e}"
        )


    st.markdown("---")

    st.subheader("💡 Energy Saving Recommendation")


    if highest_machine != "N/A":

        st.warning(
            f"{highest_machine} is consuming the highest "
            f"amount of energy "
            f"({highest_machine_energy:,.1f} kWh). "
            "Consider checking operating hours, "
            "machine efficiency and unnecessary idle operation."
        )


    st.markdown("---")

    st.subheader("📋 Energy Data")

    st.dataframe(
        energy,
        use_container_width=True
    )


# ==================================================
# AI ASSISTANT
# ==================================================

elif page == "🤖 AI Assistant":

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

                answer = get_answer(question)

                st.markdown("### 🤖 AI Answer")

                st.success(answer)

            except Exception as e:

                st.error(
                    f"❌ AI Assistant unavailable: {e}"
                )

        else:

            st.warning(
                "⚠️ Please enter a question."
            )


# ==================================================
# SOP ASSISTANT
# ==================================================

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
                f"❌ Unable to load SOP: {e}"
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
                    f"❌ SOP search failed: {e}"
                )


# ==================================================
# WHAT-IF ANALYSIS
# ==================================================

elif page == "🔮 What-If Analysis":

    st.title("🔮 What-If Analysis")


    st.write(
        "Simulate the effect of a machine shutdown "
        "on factory operations."
    )


    # --------------------------------------------------
    # MACHINE SELECTION
    # --------------------------------------------------

    machine_names = machines["machine"].tolist()


    if not machine_names:

        st.error(
            "❌ No machines found in machines.csv"
        )

        st.stop()


    selected_machine = st.selectbox(
        "⚙️ Select Machine",
        machine_names
    )


    # --------------------------------------------------
    # SHUTDOWN DAYS
    # --------------------------------------------------

    shutdown_days = st.number_input(
        "📅 Shutdown Duration (Days)",
        min_value=1,
        max_value=30,
        value=2,
        step=1
    )


    st.markdown("---")


    # --------------------------------------------------
    # ANALYZE BUTTON
    # --------------------------------------------------

    if st.button(
        "🔮 Analyze Impact",
        type="primary"
    ):

        try:

            result = calculate_impact(
                selected_machine,
                shutdown_days
            )


            # --------------------------------------------------
            # MACHINE NOT FOUND
            # --------------------------------------------------

            if result is None:

                st.error(
                    "❌ Machine information not found."
                )


            # --------------------------------------------------
            # SUCCESS
            # --------------------------------------------------

            else:

                st.subheader(
                    "📊 Impact Analysis"
                )


                col1, col2, col3 = st.columns(3)


                with col1:

                    st.metric(
                        "⚙️ Machine",
                        result["machine"]
                    )


                with col2:

                    st.metric(
                        "📅 Shutdown",
                        f"{result['days']} days"
                    )


                with col3:

                    st.metric(
                        "⏱️ Total Downtime",
                        f"{result['total_downtime']:.1f} hours"
                    )


                st.markdown("---")


                # --------------------------------------------------
                # DETAILED IMPACT
                # --------------------------------------------------

                detail_col1, detail_col2 = st.columns(2)


                with detail_col1:

                    st.metric(
                        "Existing Downtime",
                        f"{result['existing_downtime']:.1f} hours"
                    )


                with detail_col2:

                    st.metric(
                        "Additional Shutdown",
                        f"{result['shutdown_hours']:.1f} hours"
                    )


                st.markdown("---")


                # --------------------------------------------------
                # WARNING
                # --------------------------------------------------

                st.warning(
                    f"⚠️ If **{result['machine']}** remains "
                    f"stopped for **{result['days']} days**, "
                    f"the estimated total downtime will be "
                    f"**{result['total_downtime']:.1f} hours**."
                )


                # --------------------------------------------------
                # RECOMMENDATION
                # --------------------------------------------------

                st.info(
                    "💡 Recommendation: Shift production load "
                    "to an available machine if possible."
                )


                # --------------------------------------------------
                # SIMPLE DECISION
                # --------------------------------------------------

                if result["total_downtime"] >= 40:

                    st.error(
                        "🔴 High Impact: The shutdown may "
                        "significantly affect production. "
                        "Immediate mitigation is recommended."
                    )

                elif result["total_downtime"] >= 24:

                    st.warning(
                        "🟠 Medium Impact: Production may be "
                        "affected. Consider alternate capacity."
                    )

                else:

                    st.success(
                        "🟢 Low Impact: The estimated downtime "
                        "impact is relatively limited."
                    )


        except Exception as e:

            st.error(
                f"❌ What-If Analysis failed: {e}"
            )


# ==================================================
# END
# ==================================================

st.sidebar.markdown("---")

st.sidebar.caption(
    "Smart Factory DSS | Decision Support System"
)
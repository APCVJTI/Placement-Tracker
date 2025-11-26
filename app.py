import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta

DATA_FILE = "applications.csv"

# ------------ Helpers to load & save data ------------ #

def load_data():
    try:
        df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(
            columns=[
                "ID",
                "Company",
                "Role",
                "Location",
                "Application_Date",
                "Status",
                "Next_Step_Date",
                "Priority",
                "Notes",
                "Last_Updated",
            ]
        )
    # Convert date columns to date objects (if they exist)
    for col in ["Application_Date", "Next_Step_Date", "Last_Updated"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
    return df


def save_data(df: pd.DataFrame):
    df.to_csv(DATA_FILE, index=False)


def get_new_id(df: pd.DataFrame) -> int:
    if df.empty:
        return 1
    return int(df["ID"].max()) + 1


# ------------ Streamlit page config ------------ #

st.set_page_config(
    page_title="Placement & Interview Tracker",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 Placement & Interview Preparation Tracker")
st.write(
    "Keep all your applications, interviews, and deadlines **organized** in one place."
)

# Use session_state to hold data
if "df" not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

# ------------ Sidebar Navigation ------------ #

st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["➕ Add / Update Applications", "📋 Dashboard", "📊 Analytics & Export"],
)

st.sidebar.info(
    "💡 Tip: This file is self-contained. Just keep `app.py` and it will create "
    "`applications.csv` automatically for storage."
)

# ------------ Page 1: Add / Update Applications ------------ #

if page == "➕ Add / Update Applications":
    st.subheader("➕ Add or Edit Application")

    mode = st.radio("Choose mode", ["Add New", "Edit Existing"])

    if mode == "Edit Existing":
        if df.empty:
            st.warning("No applications found. Add a new one first.")
        else:
            # Create a label like: "3 | Google - SDE Intern"
            df_sorted = df.sort_values("Last_Updated", ascending=False)
            options = {
                f'{row.ID} | {row.Company} - {row.Role}': row.ID
                for _, row in df_sorted.iterrows()
            }
            selected_label = st.selectbox("Select application to edit", list(options.keys()))
            selected_id = options[selected_label]
            record = df[df["ID"] == selected_id].iloc[0]

            with st.form("edit_form"):
                company = st.text_input("Company", value=str(record["Company"]))
                role = st.text_input("Role / Position", value=str(record["Role"]))
                location = st.text_input(
                    "Location (optional)", value=str(record.get("Location", "") or "")
                )

                app_date = st.date_input(
                    "Application Date",
                    value=record["Application_Date"] or date.today(),
                )

                status = st.selectbox(
                    "Current Status",
                    [
                        "Applied",
                        "Online Assessment",
                        "Interview Scheduled",
                        "Offer",
                        "Rejected",
                        "On Hold",
                        "Not Interested",
                    ],
                    index=[
                        "Applied",
                        "Online Assessment",
                        "Interview Scheduled",
                        "Offer",
                        "Rejected",
                        "On Hold",
                        "Not Interested",
                    ].index(record["Status"])
                    if record["Status"] in [
                        "Applied",
                        "Online Assessment",
                        "Interview Scheduled",
                        "Offer",
                        "Rejected",
                        "On Hold",
                        "Not Interested",
                    ]
                    else 0,
                )

                next_step_date = st.date_input(
                    "Next Step / Interview Date (optional)",
                    value=record["Next_Step_Date"]
                    if pd.notna(record["Next_Step_Date"])
                    else date.today(),
                )

                priority = st.selectbox(
                    "Priority",
                    ["Low", "Medium", "High"],
                    index=["Low", "Medium", "High"].index(
                        record["Priority"] if record["Priority"] in ["Low", "Medium", "High"] else "Medium"
                    ),
                )

                notes = st.text_area(
                    "Notes (links, interviewer name, topics to revise, etc.)",
                    value=str(record["Notes"] or ""),
                )

                submitted = st.form_submit_button("💾 Save Changes")

            if submitted:
                idx = df.index[df["ID"] == selected_id][0]
                df.at[idx, "Company"] = company.strip()
                df.at[idx, "Role"] = role.strip()
                df.at[idx, "Location"] = location.strip()
                df.at[idx, "Application_Date"] = app_date
                df.at[idx, "Status"] = status
                df.at[idx, "Next_Step_Date"] = next_step_date
                df.at[idx, "Priority"] = priority
                df.at[idx, "Notes"] = notes.strip()
                df.at[idx, "Last_Updated"] = date.today()

                st.session_state.df = df
                save_data(df)
                st.success("✅ Application updated successfully!")

    else:  # Add New
        with st.form("add_form"):
            company = st.text_input("Company")
            role = st.text_input("Role / Position")
            location = st.text_input("Location (optional)")

            app_date = st.date_input(
                "Application Date", value=date.today()
            )

            status = st.selectbox(
                "Current Status",
                [
                    "Applied",
                    "Online Assessment",
                    "Interview Scheduled",
                    "Offer",
                    "Rejected",
                    "On Hold",
                    "Not Interested",
                ],
                index=0,
            )

            next_step_date = st.date_input(
                "Next Step / Interview Date (optional)",
                value=date.today(),
            )

            priority = st.selectbox(
                "Priority",
                ["Low", "Medium", "High"],
                index=1,
            )

            notes = st.text_area(
                "Notes (links, interviewer name, topics to revise, etc.)"
            )

            submitted = st.form_submit_button("➕ Add Application")

        if submitted:
            if not company.strip() or not role.strip():
                st.error("❗ Company and Role are required.")
            else:
                new_id = get_new_id(df)
                new_row = {
                    "ID": new_id,
                    "Company": company.strip(),
                    "Role": role.strip(),
                    "Location": location.strip(),
                    "Application_Date": app_date,
                    "Status": status,
                    "Next_Step_Date": next_step_date,
                    "Priority": priority,
                    "Notes": notes.strip(),
                    "Last_Updated": date.today(),
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.df = df
                save_data(df)
                st.success(f"✅ Application added for **{company} - {role}** (ID: {new_id})")

# ------------ Page 2: Dashboard ------------ #

elif page == "📋 Dashboard":
    st.subheader("📋 Applications Dashboard")

    if df.empty:
        st.info("No data yet. Go to **Add / Update Applications** to create your first entry.")
    else:
        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            status_filter = st.multiselect(
                "Filter by Status",
                options=sorted(df["Status"].dropna().unique()),
                default=list(sorted(df["Status"].dropna().unique())),
            )

        with col2:
            priority_filter = st.multiselect(
                "Filter by Priority",
                options=["Low", "Medium", "High"],
                default=["Low", "Medium", "High"],
            )

        with col3:
            company_search = st.text_input("Search Company / Role")

        filtered = df.copy()

        if status_filter:
            filtered = filtered[filtered["Status"].isin(status_filter)]

        if priority_filter:
            filtered = filtered[filtered["Priority"].isin(priority_filter)]

        if company_search.strip():
            text = company_search.strip().lower()
            filtered = filtered[
                filtered["Company"].str.lower().str.contains(text)
                | filtered["Role"].str.lower().str.contains(text)
            ]

        # Upcoming deadlines
        today = date.today()
        filtered["Days_to_Next_Step"] = (
            pd.to_datetime(filtered["Next_Step_Date"], errors="coerce") - pd.to_datetime(today)
        ).dt.days

        st.markdown("### 🔔 Upcoming interviews / deadlines (next 7 days)")
        upcoming = filtered[
            (filtered["Next_Step_Date"].notna())
            & (filtered["Days_to_Next_Step"].notna())
            & (filtered["Days_to_Next_Step"] >= 0)
            & (filtered["Days_to_Next_Step"] <= 7)
        ].sort_values("Next_Step_Date")

        if upcoming.empty:
            st.write("No upcoming events in the next 7 days.")
        else:
            st.dataframe(
                upcoming[
                    [
                        "ID",
                        "Company",
                        "Role",
                        "Status",
                        "Next_Step_Date",
                        "Priority",
                        "Notes",
                    ]
                ].reset_index(drop=True)
            )

        st.markdown("### 📄 All filtered applications")
        st.dataframe(
            filtered[
                [
                    "ID",
                    "Company",
                    "Role",
                    "Location",
                    "Application_Date",
                    "Status",
                    "Next_Step_Date",
                    "Priority",
                    "Last_Updated",
                    "Notes",
                ]
            ].sort_values("Application_Date", ascending=False).reset_index(drop=True)
        )

# ------------ Page 3: Analytics & Export ------------ #

elif page == "📊 Analytics & Export":
    st.subheader("📊 Analytics & Export")

    if df.empty:
        st.info("No data yet to analyze.")
    else:
        total_apps = len(df)
        offers = (df["Status"] == "Offer").sum()
        rejections = (df["Status"] == "Rejected").sum()
        in_process = df[df["Status"].isin(["Applied", "Online Assessment", "Interview Scheduled"])].shape[0]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Applications", total_apps)
        col2.metric("Offers", offers)
        col3.metric("Rejected", rejections)
        col4.metric("Still in Process", in_process)

        st.markdown("#### Status Distribution")
        status_counts = df["Status"].value_counts()
        st.bar_chart(status_counts)

        st.markdown("#### Priority Distribution")
        pr_counts = df["Priority"].value_counts()
        st.bar_chart(pr_counts)

        st.markdown("#### Top Companies (by number of applications)")
        top_companies = df["Company"].value_counts().head(10)
        st.bar_chart(top_companies)

        st.markdown("### 📥 Export Data")
        csv_data = df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            data=csv_data,
            file_name="applications_export.csv",
            mime="text/csv",
        )

        st.markdown("### 🧠 Quick Tips")
        st.write(
            "- Use the **Notes** field to store: HR contact, coding round topics, links to JD, etc.\n"
            "- Use **Priority = High** for dream companies or near deadlines.\n"
            "- Regularly check the **Dashboard** page for upcoming interviews in the next 7 days."
        )

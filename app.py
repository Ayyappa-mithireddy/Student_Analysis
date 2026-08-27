import streamlit as st
import pandas as pd
import plotly.express as px


# Configure the Streamlit page
st.set_page_config(
    page_title="Student Academic Risk Intelligence System",
    layout="wide",
    page_icon="🎓"
)


# Load the Maths.csv dataset
df = pd.read_csv("./data/maths.csv")


# -----------------------------
# Feature Engineering
# -----------------------------

# Create Result based on G3
# G3 = 0 means Dropout, 1-9 means Fail, and 10-20 means Pass
df["Result"] = df["G3"].apply(
    lambda x: "Dropout" if x == 0 else ("Fail" if 1 <= x <= 9 else "Pass")
)

# Convert G3 into percentage
df["Percentage"] = (df["G3"] / 20) * 100

# Calculate average alcohol consumption
df["avg_alcohol"] = (df["Dalc"] + df["Walc"]) / 2

# Calculate average education level of both parents
df["parent_edu_avg"] = (df["Medu"] + df["Fedu"]) / 2

# Calculate grade trend from G1 to G3
df["grade_trend"] = df["G3"] - df["G1"]

# Count "yes" values across schoolsup, famsup, and paid
df["total_support"] = (
    (df["schoolsup"] == "yes").astype(int)
    + (df["famsup"] == "yes").astype(int)
    + (df["paid"] == "yes").astype(int)
)

# Calculate the academic risk score
df["risk_score"] = (
    (df["failures"] * 2)
    + (df["absences"] / 10)
    + df["avg_alcohol"]
    - df["studytime"]
)

# Calculate average of G1 and G2
df["g1_g2_avg"] = (df["G1"] + df["G2"]) / 2


# -----------------------------
# Main Dashboard Title
# -----------------------------

st.title("🎓 Student Academic Risk Intelligence System")


# -----------------------------
# Calculate KPI Values
# -----------------------------

# Total number of students
total_students = len(df)

# Exclude dropouts for academic performance calculations
non_dropout = df[df["G3"] != 0]

# Calculate class average G3 excluding dropouts
class_average_g3 = round(non_dropout["G3"].mean(), 2)

# Count students who passed (G3 >= 10)
pass_count = (non_dropout["G3"] >= 10).sum()

# Calculate pass rate among non-dropout students
pass_rate = round((pass_count / len(non_dropout)) * 100, 1)

# Count students at risk (G3 between 1 and 9)
at_risk_count = ((df["G3"] >= 1) & (df["G3"] <= 9)).sum()


# -----------------------------
# Display 4 KPI Cards in One Row
# -----------------------------

# Create four columns for the KPI cards
col1, col2, col3, col4 = st.columns(4)

# Card 1: Total Students
with col1:
    st.metric("Total Students", total_students)

# Card 2: Class Average G3
with col2:
    st.metric("Class Average G3", class_average_g3)

# Card 3: Pass Rate
with col3:
    st.metric("Pass Rate %", f"{pass_rate:.1f}%")

# Card 4: At-Risk Count
with col4:
    st.metric("At-Risk Count", at_risk_count)


# -----------------------------
# Performance Charts Section
# -----------------------------

st.subheader("📊 Performance Charts")

# Create two columns to display the charts side by side
col1, col2 = st.columns(2)

# -----------------------------
# Left Chart: Study Time vs Final Grade
# -----------------------------
with col1:
    # Create an interactive scatter plot
    fig_scatter = px.scatter(
        df,
        x="studytime",
        y="G3",
        color="Result",
        color_discrete_map={
            "Pass": "green",
            "Fail": "red",
            "Dropout": "grey"
        },
        hover_data=["absences", "G1", "G2"],
        title="Study Time vs Final Grade"
    )

    # Display the scatter plot inside the left column
    st.plotly_chart(fig_scatter, use_container_width=True)


# -----------------------------
# Right Chart: Average G3 by Internet Access
# -----------------------------
with col2:
    # Calculate average G3 for each internet access group
    avg_g3_internet = (
        df.groupby("internet", as_index=False)["G3"]
        .mean()
    )

    # Create an interactive bar chart
    fig_bar = px.bar(
        avg_g3_internet,
        x="internet",
        y="G3",
        title="Average G3 by Internet Access",
        color="internet"
    )

    # Display the bar chart inside the right column
    st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------
# Student Analysis Table
# -----------------------------

st.subheader("🚨 Student Analysis Table")

# Create a dropdown to filter students by their result
result_filter = st.selectbox(
    "Filter by Result",
    ["All", "Pass", "Fail", "Dropout"]
)

# Apply the selected filter to the DataFrame
if result_filter == "All":
    filtered_df = df
else:
    filtered_df = df[df["Result"] == result_filter]

# Select only the required columns for the main table
display_columns = [
    "G1",
    "G2",
    "G3",
    "Result",
    "Percentage",
    "absences",
    "studytime",
    "failures",
    "risk_score"
]

# Display the filtered student DataFrame
st.dataframe(
    filtered_df[display_columns],
    use_container_width=True
)


# -----------------------------
# At-Risk Students Section
# -----------------------------

st.subheader("⚠️ At-Risk Students")

# Filter students with G3 between 1 and 9
at_risk_df = df[
    (df["G3"] >= 1) & (df["G3"] <= 9)
].copy()

# Sort at-risk students by G3 ascending
# Lower G3 means worse performance
at_risk_df = at_risk_df.sort_values("G3", ascending=True)

# Select only the required columns
at_risk_columns = [
    "G1",
    "G2",
    "G3",
    "absences",
    "studytime",
    "failures"
]

# Display the total number of at-risk students
st.write(f"Total at-risk students: {len(at_risk_df)}")

# Display the at-risk students table
st.dataframe(
    at_risk_df[at_risk_columns],
    use_container_width=True
)

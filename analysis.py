import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import os
def load_and_prepare_data(filepath):
    # Load the CSV file into a Pandas DataFrame
    df = pd.read_csv(filepath)

    # Create Result based on the final grade (G3)
    # G3 = 0 is treated as Dropout, not as a zero score
    df["Result"] = df["G3"].apply(
        lambda x: "Dropout" if x == 0 else ("Fail" if 1 <= x <= 9 else "Pass")
    )

    # Convert the final grade into a percentage
    df["Percentage"] = (df["G3"] / 20) * 100

    # Calculate average alcohol consumption
    df["avg_alcohol"] = (df["Dalc"] + df["Walc"]) / 2

    # Calculate average education level of both parents
    df["parent_edu_avg"] = (df["Medu"] + df["Fedu"]) / 2

    # Calculate the grade trend from G1 to G3
    df["grade_trend"] = df["G3"] - df["G1"]

    # Count the number of "yes" values across the three support columns
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

    # Calculate the average of the first and second period grades
    df["g1_g2_avg"] = (df["G1"] + df["G2"]) / 2

    # Return the complete prepared DataFrame
    return df

def calculate_statistics(df):
    # Exclude dropouts (G3 = 0) for academic performance statistics
    non_dropout = df[df["G3"] != 0]

    # Calculate the average final grade (G3) among non-dropout students
    class_avg_g3 = np.mean(non_dropout["G3"])

    # Calculate the pass rate among non-dropout students
    # Passing means G3 >= 10
    pass_rate = np.mean(non_dropout["G3"] >= 10) * 100

    # Count the total number of dropout students (G3 = 0)
    dropout_count = np.sum(df["G3"] == 0)

    # Count students who are at risk of failing (G3 from 1 to 9)
    at_risk_count = np.sum((df["G3"] >= 1) & (df["G3"] <= 9))

    # Calculate the correlation matrix for G1, G2, and G3
    # using only non-dropout students
    correlation_matrix = np.corrcoef(
        non_dropout[["G1", "G2", "G3"]].values,
        rowvar=False
    )

    # Return all calculated statistics as a dictionary
    return {
        "class_avg_g3": class_avg_g3,
        "pass_rate": pass_rate,
        "dropout_count": dropout_count,
        "at_risk_count": at_risk_count,
        "correlation_matrix": correlation_matrix
    }


def generate_static_charts(df):
    # Create the output folder if it does not already exist
    os.makedirs("output", exist_ok=True)

    # -----------------------------
    # Chart 1: Average G3 by Study Time
    # -----------------------------

    # Calculate the average G3 for each studytime level
    avg_g3_by_studytime = df.groupby("studytime")["G3"].mean()

    # Create the bar chart
    plt.figure(figsize=(8, 5))
    plt.bar(avg_g3_by_studytime.index, avg_g3_by_studytime.values)

    # Add chart title and axis labels
    plt.title("Average G3 by Study Time")
    plt.xlabel("Study Time (1=<2hrs, 2=2-5hrs, 3=5-10hrs, 4=>10hrs)")
    plt.ylabel("Average G3")

    # Ensure all studytime levels 1, 2, 3, and 4 appear on the X axis
    plt.xticks([1, 2, 3, 4])

    # Save the chart
    plt.savefig("output/avg_g3_by_studytime.png", bbox_inches="tight")

    # Close the chart to release memory
    plt.close()

    # -----------------------------
    # Chart 2: Student Result Distribution
    # -----------------------------

    # Count students in each result category
    result_counts = df["Result"].value_counts()

    # Ensure the categories appear in the required order
    result_counts = result_counts.reindex(
        ["Pass", "Fail", "Dropout"],
        fill_value=0
    )

    # Create the pie chart
    plt.figure(figsize=(7, 7))
    plt.pie(
        result_counts.values,
        labels=result_counts.index,
        autopct="%1.1f%%"
    )

    # Add chart title
    plt.title("Student Result Distribution")

    # Save the pie chart
    plt.savefig("output/pass_fail_dropout_pie.png", bbox_inches="tight")

    # Close the chart to release memory
    plt.close()


def generate_interactive_charts(df):
    # -----------------------------
    # Chart 1: Study Time vs Final Grade
    # -----------------------------

    # Create a scatter plot using Plotly
    fig1 = px.scatter(
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
        title="Study Time vs Final Grade (G3)"
    )

    # Display the interactive scatter plot
    fig1.show()

    # -----------------------------
    # Chart 2: Average G3 by Internet Access
    # -----------------------------

    # Calculate the average G3 for each internet access group
    avg_g3_by_internet = (
        df.groupby("internet", as_index=False)["G3"]
        .mean()
    )

    # Create an interactive bar chart
    fig2 = px.bar(
        avg_g3_by_internet,
        x="internet",
        y="G3",
        color="internet",
        title="Average G3 by Internet Access"
    )

    # Display the interactive bar chart
    fig2.show()


def print_summary(stats):
    # Print a clean formatted analysis summary
    print("=" * 48)
    print("STUDENT ACADEMIC RISK INTELLIGENCE SYSTEM")
    print()
    print("ANALYSIS SUMMARY")
    print("=" * 48)

    # Print each statistic in a readable format
    print(f"Total Students   : {stats['total_students']}")
    print(f"Class Average G3 : {stats['class_avg_g3']:.2f}")
    print(f"Pass Rate        : {stats['pass_rate']:.2f}%")
    print(f"At-Risk Count    : {stats['at_risk_count']}")
    print(f"Dropout Count    : {stats['dropout_count']}")

    print("=" * 48)


# Main block: execute the complete analysis pipeline
if __name__ == "__main__":
    # Load and prepare the student dataset
    df = load_and_prepare_data("data/Maths.csv")

    # Calculate academic statistics
    stats = calculate_statistics(df)

    # Add total number of students for the summary
    stats["total_students"] = len(df)

    # Generate and save static charts
    generate_static_charts(df)

    # Generate and display interactive charts
    generate_interactive_charts(df)

    # Print the formatted analysis summary
    print_summary(stats)

    # Confirm that the analysis has completed
    print("Analysis complete. Charts saved to output/ folder")
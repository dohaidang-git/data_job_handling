"""Vẽ biểu đồ từ CSV đã xử lý."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

INPUT_PATH = Path(__file__).resolve().parent.parent / "dataset" / "data_cleaned.csv"


def main():
    df = pd.read_csv(INPUT_PATH)

    plt.figure(figsize=(12, 6))
    df["job_title_category"].value_counts().plot(kind="bar")
    plt.tight_layout()
    plt.show()

    salary_vnd = df[df["salary_unit"] == "VND"]
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=salary_vnd, x="salary_avg", y="job_title_category")
    plt.tight_layout()
    plt.show()

    city_columns = [col for col in df.columns if col.startswith("city")]
    location = df.melt(
        id_vars=["job_title_category"],
        value_vars=city_columns,
        value_name="city",
    ).dropna(subset=["city"])
    bang_dem = pd.crosstab(location["city"], location["job_title_category"])
    plt.figure(figsize=(12, 10))
    sns.heatmap(bang_dem, annot=True, fmt="d", cmap="YlOrRd")
    plt.xlabel("Nhóm công việc")
    plt.ylabel("Tỉnh / thành phố")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()

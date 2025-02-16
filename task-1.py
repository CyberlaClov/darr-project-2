import matplotlib.pyplot as plt
import pandas as pd
from reliability.Probability_plotting import (
    Exponential_probability_plot,
    Lognormal_probability_plot,
    Normal_probability_plot,
    Weibull_probability_plot,
)


def load_and_prepare_data():
    """Load and set up the data for analysis."""

    # Load the dataset
    df = pd.read_csv("masked_data_V1.csv")
    return df


def plot_boxplot_by_model(df):
    """Create boxplot of time since previous repair by model."""
    plt.figure(figsize=(10, 6))
    df.boxplot(column="time since previous repair", by="model")
    plt.title("Time Since Previous Repair by Model")
    plt.xticks(rotation=45)
    plt.ylabel("Time Since Previous Repair")
    plt.show()
    plt.close()


def plot_weibull_by_product_type(df):
    """Create Weibull probability plots for each product type."""
    unique_products = df["product type"].unique()
    for product in unique_products:
        mask = df["product type"] == product
        Weibull_probability_plot(
            failures=df[mask]["time since previous repair"].to_list(),
            right_censored=df[mask]["censored"].to_list(),
        )
        plt.title(f"Weibull Probability for {product}")
        plt.grid(True)
        plt.show()
        plt.close()


def plot_distribution_comparisons(df):
    """Create probability plots for different distributions."""
    # Weibull probability plot
    Weibull_probability_plot(
        failures=df.loc[df.censored == 0, "time since previous repair"].to_list(),
        right_censored=df.loc[df.censored == 1, "time since previous repair"].to_list(),
    )
    plt.title("Weibull Probability for considered product")
    plt.grid(True)
    plt.show()
    plt.close()

    # Exponential probability plot
    Exponential_probability_plot(
        failures=df.loc[df.censored == 0, "time since previous repair"].to_list(),
    )
    plt.title("Exponential Probability for considered product")
    plt.grid(True)
    plt.show()
    plt.close()

    # Normal probability plot
    Normal_probability_plot(
        failures=df.loc[df.censored == 0, "time since previous repair"].to_list(),
    )
    plt.title("Normal Probability for considered product")
    plt.grid(True)
    plt.show()
    plt.close()

    # Lognormal probability plot
    Lognormal_probability_plot(
        failures=df.loc[df.censored == 0, "time since previous repair"].to_list(),
    )
    plt.title("Lognormal Probability for considered product")
    plt.grid(True)
    plt.show()
    plt.close()


def main():
    """Main function to execute the analysis pipeline."""
    # Load data
    print("Loading data...")
    df = load_and_prepare_data()

    # Create visualizations
    print("Creating visualizations...")
    plot_boxplot_by_model(df)
    plot_weibull_by_product_type(df)
    plot_distribution_comparisons(df)


if __name__ == "__main__":
    main()

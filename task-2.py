import pandas as pd
from dowhy import CausalModel
from sklearn.preprocessing import LabelEncoder

print("start")

df = pd.read_csv("masked_data_V1.csv")

# Prepare the data
# Convert categorical variables to numeric
le = LabelEncoder()
df["E_type"] = le.fit_transform(df["model"].str[3])  # Extract E component type (1,2,3)
# df["V_type"] = le.fit_transform(df["Model"].str[1])  # Extract V component type
df["product_type"] = le.fit_transform(df["product type"])
df["age"] = df["age after repair"]
df["time_to_failure"] = df["time since previous repair"]


def compare_components(df, comp1, comp2):
    """Compare two E-type components using binary treatment"""
    # Filter data for only the two components being compared
    mask = df["E_type"].isin([comp1, comp2])
    df_binary = df[mask].copy()

    # Create binary treatment (0 for comp1, 1 for comp2)
    df_binary["treatment"] = (df_binary["E_type"] == comp2).astype(int)

    # Create causal graph for binary comparison
    causal_graph = """
    digraph {
        age -> treatment;
        age -> time_to_failure;
        product_type -> treatment;
        product_type -> time_to_failure;
        treatment -> time_to_failure;
    }
    """

    # Create and fit causal model
    model = CausalModel(
        data=df_binary,
        treatment="treatment",
        outcome="time_to_failure",
        graph=causal_graph,
    )

    # Identify causal effect
    identified_estimand = model.identify_effect(proceed_when_unidentifiable=True)

    # Estimate causal effect
    estimate = model.estimate_effect(
        identified_estimand,
        method_name="backdoor.propensity_score_stratification",
        control_value=0,
        treatment_value=1,
        target_units="ate",
    )

    # Perform robustness check
    refutation = model.refute_estimate(
        identified_estimand, estimate, method_name="random_common_cause"
    )

    return estimate, refutation


# Perform all pairwise comparisons
component_pairs = [(0, 1), (1, 2), (0, 2)]  # Comparing E1-E2, E2-E3, E1-E3

for comp1, comp2 in component_pairs:
    print(f"\nComparing E{comp1+1} vs E{comp2+1}:")
    estimate, refutation = compare_components(df, comp1, comp2)
    print(f"Causal Estimate Results:")
    print(estimate)
    print(f"Robustness Check Results:")
    print(refutation)

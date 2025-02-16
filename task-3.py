import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from dowhy import CausalModel
from sklearn.preprocessing import LabelEncoder

# Load and prepare the data
df = pd.read_csv("masked_data_V1.csv")

# Convert categorical variables to numeric
le = LabelEncoder()
df["product_type"] = le.fit_transform(df["product type"])
df["model"] = le.fit_transform(df["model"])
df["age"] = df["age after repair"]
df["time_to_failure"] = df["time since previous repair"]

# Group by series number and create repair count
repair_counts = df.groupby("series number").size().reset_index(name="repair_count")
df = df.merge(repair_counts, on="series number", how="left")

# Create binary treatment (high vs low repair count)
median_repairs = df["repair_count"].median()
df["high_repairs"] = (df["repair_count"] > median_repairs).astype(int)

# Define causal graph
causal_graph = """
digraph {
    age -> high_repairs;
    age -> time_to_failure;
    product_type -> high_repairs;
    product_type -> time_to_failure;
    model -> high_repairs;
    model -> time_to_failure;
    high_repairs -> time_to_failure;
}
"""

# Create and visualize the graph
G = nx.DiGraph(
    [
        ("age", "high_repairs"),
        ("age", "time_to_failure"),
        ("product_type", "high_repairs"),
        ("product_type", "time_to_failure"),
        ("model", "high_repairs"),
        ("model", "time_to_failure"),
        ("high_repairs", "time_to_failure"),
    ]
)

plt.figure(figsize=(10, 8))
pos = nx.spring_layout(G)
nx.draw(
    G,
    pos,
    with_labels=True,
    node_color="lightblue",
    node_size=2000,
    arrowsize=20,
    font_size=10,
)
plt.title("Causal Graph: Impact of Repair Count on Reliability")
# plt.savefig("causal_graph_repairs.png")
plt.show()
# plt.close()

# Create and fit causal model
model = CausalModel(
    data=df,
    treatment="high_repairs",
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

# Perform robustness checks
refutation = model.refute_estimate(
    identified_estimand, estimate, method_name="random_common_cause"
)
print("\nRobustness Check Results:")
print(refutation)

print("\nCausal Estimate Results:")
print(estimate)

# Additional analysis: Look at average time to failure for both groups
print("\nAverage time to failure by repair group:")
print(df.groupby("high_repairs")["time_to_failure"].mean())

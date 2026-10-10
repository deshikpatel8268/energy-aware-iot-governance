# energy-aware-iot-governance

## Repository scope and experimental provenance

This repository contains two distinct computational components. The original dataset archive and documentation describe the initial network instances. The notebook `Energy_Aware_Governance_of_Large_Scale_Cyber_Physical_IoT_Networks_Final.ipynb` contains the original Pyomo/HiGHS analyses: it applies capacity preparation to these instances and produces the illustrative figures (multiplier trajectories, normalized flow comparison, and calibrated selected-node energy illustration).

The `reproducibility/` directory contains the separate replicated study used for the revised manuscript. It includes 60 feasible synthetic networks, generation and optimization scripts, Lagrangian pricing diagnostics, capacity-investment comparisons, service-priority experiments, capacity-degradation tests, saved results, and statistical aggregation code.

The original analyses used Pyomo and HiGHS. The replicated study uses SciPy and HiGHS. These two implementations differ in instance construction, endpoint restrictions, and pricing configuration and should not be treated as interchangeable implementations.

The original input capacities do not support the prescribed demands in the audited formulations. Results from the notebook's repaired instances therefore do not establish feasibility of the unchanged original datasets.

Execution instructions and interpretation limits are provided in `reproducibility/README.md`. Saved outputs are included; rerunning the scripts regenerates instances and overwrites computational outputs.

### Where each manuscript result comes from

| Manuscript result | Supporting file |
|---|---|
| Table II: exact-solver performance | `reproducibility/results/benchmark.csv` |
| Table III: capacity investment | `reproducibility/results/investment.csv` and `investment_seed_means.csv` |
| Table IV: service-priority tradeoffs | `reproducibility/results/priority.csv` |
| Capacity-degradation results (Section IV) | `reproducibility/results/stress.csv` |
| Intermediate pricing gaps, violations, and rankings | `reproducibility/results/prices.csv` |
| Minimum-hop comparison and sensitivity checks | `reproducibility/results/validation.csv` |
| Original-data feasibility audit | `reproducibility/results/original_feasibility_audit.csv` |
| Aggregated statistics | `reproducibility/results/summary.json` |
| Software and hardware configuration | `reproducibility/results/environment.json` |
| Structured solver-return records (status, objective, iterations, runtime; not full solver console logs) | `reproducibility/results/solver_records.jsonl` |
| Original notebook illustrations (Figs. A3–A5) | `Energy_Aware_Governance_of_Large_Scale_Cyber_Physical_IoT_Networks_Final.ipynb` |



### Running the original notebook

The notebook was written for Google Colab and is retained as a record of the original analyses.

- **Packages:** `pyomo`, `highspy`, `pandas`, `numpy`, `matplotlib`, `networkx`, `scipy`, `tabulate`, `openpyxl` (the first code cell installs these with `pip`).
- **Inputs:** extract `iot_scenario_pack.zip` and `iot_synthetic_datasets_bundle.zip` from `Dataset-20260516T171032Z-3-001.zip` and place them at `/content/iot_scenario_pack.zip` and `/content/iot_synthetic_datasets_bundle.zip`. When running outside Colab, change these paths in the notebook.
- **Outputs:** written to `/content/iot_ms_experiments/` (result tables and figure files).

The notebook repairs capacities with an instance-specific multiplier before solving and omits the source/destination endpoint restrictions used in the replicated study. Its embedded summary text predates the revised manuscript; in particular, its description of warm-start speedups is not supported by the revised analysis and is not used as evidence in the paper.

---

Synthetic large-scale smart city IoT network datasets for evaluating energy-aware multi-commodity routing, Lagrangian decomposition, congestion pricing, and scalable optimization under constrained capacity and node energy conditions. Includes network topologies, service demands, energy profiles, and stress-testing scenarios.

Recommended folder structure
datasets/
models/
results/
figures/
README.md
requirements.txt


# Energy-Aware Governance of Large-Scale Cyber-Physical IoT Networks  
## Synthetic Dataset and Scenario Repository

This repository contains the synthetic datasets, scenario packs, and supporting files used in the study:

> **“Energy-Aware Governance of Large-Scale Cyber-Physical IoT Networks: A Decomposition-Based Optimization Framework”**

The datasets were developed to support scalable experimentation for energy-aware multi-commodity routing, Lagrangian decomposition, congestion pricing, and governance-oriented optimization in smart city IoT environments.

---

# Repository Structure

```text
Dataset/
│
├── iot_synthetic_datasets_bundle.zip
│
└── iot_scenario_pack.zip

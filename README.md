# energy-aware-iot-governance

## Repository scope and experimental provenance

This repository contains two distinct computational components. The original dataset archive and documentation describe the initial network instances. 

The `reproducibility/` directory contains the separate replicated study used for the revised manuscript. It includes 60 feasible synthetic networks, generation and optimization scripts, Lagrangian pricing diagnostics, capacity-investment comparisons, service-priority experiments, capacity-degradation tests, saved results, and statistical aggregation code.

The original notebook uses Pyomo and HiGHS. The replicated study uses SciPy and HiGHS. These components differ in instance construction, endpoint restrictions, and pricing configuration and should not be treated as interchangeable implementations.

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
| Original notebook-generated illustrations | `original_notebook/Testing_Claude.ipynb` |

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

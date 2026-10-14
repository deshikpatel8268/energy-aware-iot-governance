# Extended analysis

Additional experiments for the journal version of the paper. These scripts do not modify anything in `reproducibility/results/`; they regenerate the same synthetic instances (the generator in `ext_common.py` is copied verbatim from `reproducibility/run_study.py`) and write to `results_extended/`.

## Contents

| File | Purpose |
|---|---|
| `ext_common.py` | Instance generation, witness routing, LP matrices and the LP solve (SciPy/HiGHS) |
| `ext_milp.py` | Optimal budgeted capacity-upgrade portfolio as a MILP (SciPy `milp`/HiGHS) |
| `run_extended.py` | Runs the experiments: optimal portfolio benchmark, sequential dual re-pricing (T = 2, 4, B tranches), sequential-utilization control, static rankings, and Polyak-type Lagrangian pricing with a witness-cost target |
| `summarize_extended.py` | Aggregates the CSVs and prints means with paired t-intervals |
| `results_extended/` | Saved outputs for the 70- and 150-node families (20 instances each) |

## Where each result comes from

| Manuscript result | Supporting file |
|---|---|
| Optimal portfolio benchmark and share of optimum | `results_extended/investment_n70.csv`, `investment_n150.csv` |
| Sequential dual re-pricing (Algorithm 2) | `results_extended/investment_n*.csv` (`seq_dual_*` columns) |
| Polyak-type pricing gaps | `results_extended/pricing_polyak_n*.csv`, `bounds_n*.csv` |
| MILP solve times | `results_extended/benchmark_n*.csv` |

## Running

Requires Python 3 with `numpy`, `scipy` (1.9 or later, for `milp`), and `pandas`.

```bash
cd extended_analysis
python run_extended.py 70 20      # 70-node family, seeds 0-19
python run_extended.py 150 20     # 150-node family, seeds 0-19
python summarize_extended.py
```

The second argument is either a seed count (`20`) or a range (`0-10`). An optional third argument `0` skips the MILP benchmark.

## Scope

The extended analysis covers the 70- and 150-node families. Full 300-node runs were not completed; the paper reports this limitation.

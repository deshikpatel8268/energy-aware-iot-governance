# Replicated computational study (October 2026)

This package contains NEW synthetic experiments and an independent audit of the publicly released data. It does not reproduce the original manuscript's Table II, 22% lifetime result, or warm-start implementation. The original model/run scripts were not present in the public repository at the audited commit.

## Run

Python 3.12; NumPy 2.3.5; SciPy 1.17.0 (bundled HiGHS 1.8.0). Plot/report processing additionally uses pandas and matplotlib. No proprietary solver is needed.

```
python run_study.py
python summarize.py
```

Run from a fresh copy if you want to retain the delivered outputs: these commands overwrite results and regenerate the 60 instances. Runtime depends on the machine. The script also documents utilization rounding to 12 decimal places before sorting, and all seven retained-capacity factors. The saved outputs in `results/` come from the run reported in the manuscript, so the tables can be checked without rerunning anything.

## Contents and provenance

- `original_data/`: unchanged CSV instances copied from the public repository, retained for the infeasibility audit only; not used as successful experiments.
- `data/`: sixty compressed NumPy instance files. Load with `np.load(path)`; arrays are arcs (zero-based), energy, b, c, u, and a feasible witness flow.
- `run_study.py`: original-data audit, generator, sparse LP model, pricing diagnostic, capacity interventions, weight sensitivity, and degradation tests.
- `results/original_feasibility_audit.csv`: all twelve original instances, tested with and without source/destination arc restrictions.
- `results/benchmark.csv`: two exact algorithms on each replacement instance.
- `results/investment.csv`: individual policy outcomes including ten random selections per seed and budget.
- `results/investment_seed_means.csv`: random replicates averaged within network before cross-network inference.
- `results/investment_by_size.csv`: size-stratified summaries.
- `results/prices.csv`: iteration-level bounds, rankings, feasibility violation, and elapsed pricing time.
- `results/priority.csv`: positive priority-weight comparisons.
- `results/stress.csv`: full-demand feasibility under capacity degradation.
- `results/validation.csv`: minimum-hop comparison and finite-difference sensitivity checks.
- `results/solver_records.jsonl`: structured solver-return records, not full native solver console transcripts. Contains status, message, objective, iterations, runtime, and residuals where available.
- `results/environment.json`: measured software and hardware configuration.
- `results/summary.json`: processed statistics used in the revised manuscript.
- `figures/`: generated figures; PDF versions are vector graphics.

Original repository: https://github.com/deshikpatel8268/energy-aware-iot-governance
Audited commit: 624a41b43e8dd26d473cab62a36660fb5e47ade8
Accessed 2026-10-06.

## Interpretation limits

The replacement family has 70, 150, or 300 nodes; four services; one destination; twenty seeds per size. Capacity is built from a feasible witness plus positive slack. This conditions the experiment on feasibility and is not an empirically calibrated municipal network. Each capacity investment adds five packet-capacity units on each chosen directed arc; the budget is an equal-cost arc-count budget, not dollars. Bidirectional physical upgrades would need a different intervention model. Rankings and outcomes use the same operating scenario; no held-out robustness claim is supported. All demand must be delivered, so stress infeasibility cannot be reinterpreted as observed service loss.

No battery depletion, node removal, packet delay, hard reservation, minimum-service guarantee, warm-start transfer, parallel implementation, 1,000-/5,000-node benchmark, or monetary return is modeled. The study intentionally narrows the claims instead of supplying unsupported results for those topics.

The pricing step uses a scale derived from median arc cost and mean capacity and a diminishing exponent of 0.75. It does not use the exact objective as a tuning target. Its last/early iterates can be infeasible. The exact LP is the source of feasible routing and optimal dual prices; no solver warm start is supplied. The program checks shortest-path versus relaxed LP objective agreement for one instance at each size, both exact algorithms' objective agreement for all instances, witness feasibility, lower-bound validity, and finite-difference sensitivity.

## Statistics

Network seed is the observational unit. Ten random intervention replicates are averaged within each network and budget. Confidence intervals are two-sided Student-t intervals over seed-level outcomes, with pooled descriptive summaries weighted equally across the three sizes. Policy-difference intervals are paired on the same instance. There is no multiple-comparison correction and no claim of population-level real-city inference. Runtime includes SciPy call overhead and matrix conversion internal to the solver wrapper; sparse matrix construction is reported separately. Machine load is not isolated.

## AI assistance

ChatGPT assisted in creating and executing the replacement code, interpreting outputs, and drafting the revised manuscript. The original authors have not yet independently validated this newly generated package. Coauthor review is required before research submission. No numerical outputs were manually substituted to obtain a favorable comparison.

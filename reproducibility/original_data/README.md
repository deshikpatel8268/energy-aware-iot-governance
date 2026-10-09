# IoT Scenario Pack (Synthetic)

This pack creates three scenarios aligned with the published IoT LP routing model:

- Scenario 1 (High capacity): u_ij = 20 on all existing links. Objective considers all services.
- Scenario 2 (Low capacity):  u_ij = 5  on all existing links. Objective considers all services.
- Scenario 3 (Priority objective): same dataset as Scenario 2 (u_ij = 5), but in the optimization model
  you should switch to the priority-only objective (Expression 6 in the paper).

## Files per instance
- nodes.csv: node coordinates, energy consumption Ec_i, and source/destination flags
- arcs.csv: directed arcs (i,j) with capacity u_ij (graph is undirected but stored symmetrically)
- demands.csv: b_i^s (sources positive, destinations negative). Sum_i b_i^s = 0 for each service.
- services.csv: service list and priority flag
- metadata.json: instance settings including chosen sources and destinations

## Mapping to model notation
N = nodes.csv.node
O = {i | nodes.csv.is_source = 1}
D = {i | nodes.csv.is_destination = 1}
S = services.csv.service
u_ij = arcs.csv.u_ij
Ec_i = nodes.csv.Ec_i
b_i^s = demands.csv.b_i_s

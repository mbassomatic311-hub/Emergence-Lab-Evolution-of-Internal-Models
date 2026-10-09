# Emergence Lab — Experiment 06

**Scientific status: exploratory computational model; not evidence of artificial consciousness.**

## What is tested?
Can Darwinian-style selection create a recurrent action–outcome comparison circuit in agents that initially have **no recurrent connections**?

The environment delivers a movement command at one time and an ambiguous sensory event later. If the event comes from the agent's action, approaching it is beneficial; if it comes from an external source, approaching it is harmful. The event alone does not identify the source. Selection rewards only survival payoff, not self/other identification labels. Mutation may add recurrent neural connections. A functioning comparator can preserve the earlier motor command and use it with the later sensory event.

This is an **engineered information-processing scenario**. We do *not* reproduce the origin of cells, neurons, subjective consciousness, or biological evolution. The environment, sensory encoding, mutation rules, payoff structure, and controller topology were all chosen by the authors.

## Reproduce

Python 3.11+; `pip install numpy scipy matplotlib`.

```bash
python -m unittest test_engine.py
OPENBLAS_NUM_THREADS=1 python run_resumable.py
python collate.py
python make_artifacts.py
```

Outputs: per-seed CSV, agent genomes, 4-condition trace data, visual charts, and a descriptive manuscript. The data-generating mechanism is fully specified in `engine.py`; the analysis plan was fixed in `STUDY_PROTOCOL.md` before the 24 held-out seeded runs, but **not publicly preregistered**.

## Essential baselines
- Recurrence suppressed while evolving.
- Random fitness selection; same size, genome and mutation mechanism.
- No genotype inheritance.
- Within-agent intervention removing all recurrence at test.
- Scrambled retained cues and reversed/informationally useless environments.

The source variable is hidden from the controller but not from the payoff-generating environment. Survival payoffs are different by source **by design**. The model implements two neural processing phases and does not discover this scheduling or the survival task.

## Meaning
Successful evolution would show that simple Darwinian optimization can construct a minimal sensorimotor comparator from available building blocks. It would **not** show that the comparator is subjective, aware, or conscious, nor that this mechanism is new to research. See related work on corollary discharge (Crapse & Sommer 2008), robot self-modeling (Bongard et al. 2006), and internal models of agency (Tanaka & Imamizu 2025).

## Scientific provenance
This protocol was formulated after exploratory Experiments 01–05; those earlier experiments do not constitute independent replication. The present study is computational and exploratory, using an internal pre-run checksum only. The frozen source, pilot exclusion seeds, and all seeds and results are supplied for scrutiny. Please do not describe it as a preregistered discovery.

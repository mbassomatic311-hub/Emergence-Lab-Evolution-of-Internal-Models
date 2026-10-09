# Emergence Lab / Experiment 07 reproducibility package

Status: Exploratory toy evolutionary simulation. Not biological research, not evidence of consciousness, not publicly preregistered.

1. Install Python 3.10+, numpy, matplotlib, reportlab.
2. Run `python -m unittest -q test_engine07.py`.
3. Reproduce 32-seed primary data: `python engine07.py --seeds 32 --seed-start 870000 --out primary`.
4. Regenerate paper, PDF and figures: `python build_report.py`.
5. Check original file hashes in `FROZEN_SHA256.txt`.

Read `PROTOCOL_FROZEN_BEFORE_MAIN.md` and `RESEARCH_NOTE.md` for design, limitations, and prior literature. All runs are simulated.

The pilot was run before freezing the protocol; the 32-seed study was later run from locally frozen source. Public preregistration has NOT occurred.

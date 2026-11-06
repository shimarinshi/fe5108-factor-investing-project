# Part 1: standalone analysis

Run from the repository root in the environment described in the main README:

```bash
python src/part_1/build_part1.py
```

The script reads `data/raw/ff_msci_shared.xlsx` and writes tables, figures and an audit summary to `outputs/part_1/`. It uses the shared pinned dependencies and runs offline. It is separate from `run_all.py --all`, which covers Parts 2–5.

This exposes the existing Part 1 numerical analysis. Its calculations are unchanged; input and output paths now use the shared repository layout. The old standalone HTML/README drafting stage is omitted. The [English report](../../reports/part_1/README.md), [numerical tables](../../outputs/part_1/tables/) and [final report](../../reports/final_report/FE5108_Final_Project_Report.pdf) can be read directly.

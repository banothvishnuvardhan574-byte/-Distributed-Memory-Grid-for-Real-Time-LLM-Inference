# Daily assignment PDFs

The inline schedule in `generate_daily_pdfs.py` defines the full 20-day roadmap:
Days 1-7 cover foundations, Days 8-14 implementation, and Days 15-20
integration and demo preparation. Every daily packet includes the goal,
assignments and expected outputs for all five members, GitHub review steps, and
an end-of-day checklist. Day 5 spells out the Member 1 team-lead work, and Day
10 includes the review-round-one integration checkpoint, verification commands,
and grid-clear endpoint assignment. The human-readable Day 10 sheet is
`day_10.md`.

## Generate the PDFs

From this directory, install fpdf2 and run the generator:

```text
pip install fpdf2
python generate_daily_pdfs.py
```

The script creates or refreshes `day_01.pdf` through `day_20.pdf` in this
folder. To regenerate one packet without refreshing the others, pass its day
number:

```text
python generate_daily_pdfs.py --day 10
```

The Day 5 packet includes the `/health` check, prompt and PDF route stubs,
teammate PR review, and the specified branch/commit/push workflow.

# More than a Hack 2027  Phase 1: ball possession

One notebook, end to end: it reads the gated match bundle straight from Google Drive, produces the
`frame,label` possession file, validates it with the organisers' own checker, scores it on the
public five-minute ground truth, and writes the technical document and reproducibility manifest that
`SUBMISSION.md` asks for.

```
mtah2027_possession_pipeline.ipynb     the pipeline (the only source file)
requirements.txt                       pinned dependencies
README.md                              this file
```

The match data is **not** in this repository and is not redistributable  see *Rules* below.

---

## What it produces

| file | what it is |
|---|---|
| `<team_name>.csv` | 199,319 rows, `frame,label` over `H`/`A`/`D`/`X`  the scored deliverable |
| `<team_name>.md` | the technical document, filled in with the numbers from that run |
| `manifest.json` | data files and sizes, config, seeds, repository commit, submission sha256 |
| `requirements.txt` | the exact versions that produced the run |

All four land in `<Drive>/mtah2027_work/submission/`. The CSV is also written to the competition
repository's `evaluation/results/` so the official scorer can read it.

---

## Inputs

1. **The match bundle** (gated; download after enrolment, see the competition's `DATA.md`). Put it
   anywhere in your Google Drive: the notebook searches for `*_tactical_atd.txt`, so a folder
   holding `tactical/` and `broadcast/` is found, a flat folder is staged, and a zip is extracted.
2. **The competition repository** `metrica-sports/more-than-a-hack-2027`  `games.py`, the metric
   library, the scorer, the public ground truth and the four baselines. The notebook finds a local
   clone, a clone already in the work folder, or clones it itself.

Nothing else. There is no model download and no external data.

---

## Run it

### Colab

Open the notebook, `Runtime → Run all`. It mounts Drive, finds the bundle and the repository from
the resolution order documented in §0, and writes the deliverables. Set the team name first:

```python
TEAM_NAME = "your-team-name"
```

Every setting can also come from an environment variable, which is how the headless run works.

### Headless (reproduces the same file)

```bash
pip install -r requirements.txt
export MTAH_TEAM=your-team-name
export MTAH_DATA_DIR='/path/to/bundle'      # the folder that contains tactical/
export MTAH_WORK_DIR='/path/to/output'
jupyter nbconvert --to notebook --execute mtah2027_possession_pipeline.ipynb --output executed.ipynb
```

On Colab add `MTAH_DRIVE_ROOT=/content/drive/MyDrive`; locally the notebook auto-detects a mounted
Drive, and runs without one if `MTAH_DATA_DIR` and `MTAH_WORK_DIR` are set.

| env var | default | what |
|---|---|---|
| `MTAH_TEAM` | `BAU` | names the CSV and the technical document, and the row on the board |
| `MTAH_DRIVE_ROOT` | auto / mount | Drive root |
| `MTAH_DATA_DIR` | auto-discovered on Drive | bundle root |
| `MTAH_WORK_DIR` | `<Drive>/mtah2027_work` | clone + deliverables |
| `MTAH_REPO_DIR` | auto (local → Drive → clone) | competition repository |
| `MTAH_STRICT_PARITY` | `1` | stop if the parsed tracking does not reproduce the repo's `baseline_raw.csv` |
| `MTAH_BOOTSTRAP` | `1000` | bootstrap draws for the confidence intervals |
| `MTAH_STRESS_DRAWS` | `10` | repeats of the ball-masked stress test |

---

## Reproducibility

The labels are deterministic: fixed seeds, no random initialisation, no training on the public
labels, and the CSV is written with `\n` line endings so a Windows run and a Linux run produce the
same bytes. `manifest.json` records the repository commit, the bundle's file sizes, the config and
the sha256 of the submitted CSV.

`MTAH_STRICT_PARITY=1` (the default) makes the run stop unless the parsed tracking, team mapping
and frame alignment reproduce the repository's own committed `baseline_raw.csv`, frame for frame.
That check is what makes "the same file" mean something rather than being a claim.

The one thing that cannot be reproduced locally is the score: the ranking ground truth covers the
full match and is private. §4 of the notebook reports the public five-minute result with bootstrap
intervals, a stress test against the match-wide ball visibility, and full-match diagnostics, and is
explicit about how little the five-minute window can decide.

---

## Rules

- **The labels come out of an algorithm**  a probabilistic decoder over ball geometry, Smart
  Tagging and self-supervised player-shape models. Nothing is hand-labelled or hand-corrected.
- **The private ground truth is not used.** Only the published five minutes, and only for
  evaluation  never for fitting or tuning.
- **The match data is not redistributed.** It stays in Drive and is never copied into this
  repository or into the deliverables folder; the run's checklist asserts that none of the bundle
  is tracked by git.

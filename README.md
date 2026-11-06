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

Nothing else is needed to rerun the pipeline. The tactical video is not decoded. No external dataset is loaded or required. The decoder is fixed from the tracking geometry and the possession definition: `lam_team=2.5`, `touch_dist=1.5 m`, `kappa=0.8`, `r_gate=7.0`, with no relative-speed touch gate. The earlier package used the public window to select constants, but every one of those values is reverted or replaced in this package; a later dead-model post-pass was evaluated on the public window and removed, and an external sample-game candidate was removed with every setting derived from it, so no public-window-selected or external-data constant or post-processing pass remains. The long-gap open-play guard (`gap_tag_after_s=20.0`, `w_tag_alive=1.0`) is a label-free structural prior fixed from the match-wide gap distribution and tag semantics; the public window has no ball gap longer than 14.6 s, so the guard cannot fire there. A dead-leading short-spell cleanup then applies the existing 5 s alive floor to short team runs immediately after dead ball; it adds no new constant.

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
same bytes. The final values are fixed from the tracking geometry and the possession definition:
`lam_team=2.5`, `touch_dist=1.5 m`, `kappa=0.8` and `r_gate=7.0`; there is no relative-speed
touch gate and no external dataset. The label-free long-gap open-play prior (`gap_tag_after_s=20.0`, `w_tag_alive=1.0`) is fixed from the match-wide gap structure and the tag scale, not from the public window. The dead-leading short-spell cleanup reuses the pre-registered `min_alive_s=5.0` floor. The restart visible-ball trim holds post-dead frames dead until the ball is visible; the self-touch trim then holds them dead until the possessing team has a controlled touch, and the short-spell cleanup is applied again after that trim, closing the pass under the same floor. The visible-ball trim is structural and changes no public frame; the self-touch trim and its cleanup are structural and do change public frames. A structural other-touch split reuses the same 5 s floor. The age hazard is disabled as the simpler flat structural rule. The
earlier package selected constants on the public window; every one of those values is reverted or
replaced here, the external-data candidate is removed, and no public-window-selected or external-data constant or post-processing pass remains. The selection history is recorded in
the technical document and `manifest.json`. `manifest.json` also records the team repository, the
competition-code commit, the bundle's file sizes, the config and the sha256 of the submitted CSV.

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
- **The private ground truth is not used.** The final values are fixed from the tracking geometry
  and the possession definition: `lam_team=2.5`, `touch_dist=1.5 m`, `kappa=0.8`, `r_gate=7.0`, with no
  relative-speed touch gate. No external dataset is used. A label-free long-gap open-play prior is fixed from the match-wide gap structure; it is inactive on the public window. The separate dead-leading short-spell cleanup reuses the existing 5 s alive floor and, including its post-trim closure, removes three public short runs; a restart lead-in trim holds post-dead frames dead until the ball is visible, a self-touch trim holds them dead until the possessing team has a controlled touch, and a structural other-touch split also reuses the 5 s floor. All are label-free; the visible-ball trim changes no public frame, while the self-touch trim and closure are structural and do change public frames. The published five minutes
  were also used to select constants in the earlier package; every one of those values is reverted
  or replaced in this package, the external-data candidate is removed, and no public-window-selected or external-data constant or post-processing pass remains. Details are in the technical document and `manifest.json`.
- **Zero hand labels from the provided game.** No frame was hand-labelled or hand-corrected, and no
  human labeller was used. No external dataset is used, loaded or redistributed.
- **No video is decoded.** The tactical video is not decoded or used; the match inputs are the
  bundle's ATD, Smart Tagging and homography.
- **The match data is not redistributed.** It stays in Drive and is never copied into this
  repository or into the deliverables folder; the run's checklist asserts that none of the bundle
  is tracked by git.

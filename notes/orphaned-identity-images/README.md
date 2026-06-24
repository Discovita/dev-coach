# Identity Images — Investigation, Manifests & Full Bucket Audit

**Date:** 2026-06-08
**Buckets:** `discovita-dev-coach-staging` and `discovita-dev-coach-production` (us-east-1, separate per env; local dev uses the staging bucket)

## TL;DR

Identity images weren't showing in any deployment. Root cause was **not** AWS/S3 —
S3 is healthy, public, CORS-correct, and every object the DB references actually
exists (0 missing files). Images don't show because the test-scenario templates
being instantiated carry **no `image` field**, so the resulting `identities_identity`
rows have `image = NULL` and the UI renders the "Image coming soon" placeholder.

Images live in **two S3 buckets**, under these prefixes:

| What | Path prefix | Source |
|--|--|--|
| **Gemini-generated identity images** | `media/identities/identity/<uuid>.png` | image-generator service → saved to S3 |
| Reference photos (input to Gemini) | `media/reference_images/referenceimage/<uuid>.*` | user uploads |
| Scenario-form identity uploads | `media/<uuid>/<name>.jpg` | manual upload in scenario builder |
| Session videos | `media/session-videos/*.mov` | CPV feature |
| Sized renditions (derivatives) | `media/__sized__/...` | django-versatileimagefield |
| **In-progress (unsaved) generations** | **not in S3** — `identities_identityimagechat.chat_history` (Postgres, base64) | Gemini multi-turn editing |

## Files in this folder

| File | What it is |
|--|--|
| `gemini-identity-images-manifest.csv` | The **Gemini-generated** identity images (`media/identities/identity/*`). 81 rows. Linked rows attributed directly from the DB (identity name → user email → scenario). |
| `orphaned-identity-images-manifest.csv` | The **scenario-form upload** identity images (`media/<uuid>/<name>.jpg`). 370 rows. Owner is best-effort name-matched (filename = identity name). |
| `full-bucket-inventory.csv` | Every non-derivative object in **both** buckets (originals + videos), 711 rows, with type / linked-or-orphan / attribution / url. |

Common columns: `status` (linked / orphan / IN USE), `upload_date`, `size`, `s3_key`,
`url` (direct public link — paste in a browser), `gsheet_preview` (`=IMAGE("url")` —
renders a thumbnail when imported into Google Sheets; enable "convert text to
formulas" on import and widen/tall the rows).

## Full bucket audit (2026-06-08)

### staging — 1,580 objects
| type | count | orphan (referenced by nothing) |
|--|--|--|
| gemini-identity | 80 | **39** |
| reference-image | 205 | **165** |
| scenario-upload | 392 | **354** |
| session-video | 12 | — |
| sized-rendition | 891 | 131 renditions whose original is gone |

### production — 52 objects
| type | count | orphan |
|--|--|--|
| gemini-identity | 1 | 0 |
| reference-image | 9 | 0 |
| session-video | 12 | — |
| sized-rendition | 30 | 0 |

### Key audit conclusions
- **Nothing the DB points to is missing.** 0 DB image references (identity rows,
  reference-image rows, scenario templates) lack a corresponding S3 object — no
  broken-link images anywhere.
- **No stray/unknown objects** — every object classifies into a known prefix.
- **Prod is clean**: every prod original is linked; only 1 Gemini identity image
  exists there total (this is the real "no images on prod" story).
- **Staging holds the orphan pile**: 39 Gemini + 165 reference + 354 scenario-upload
  originals reference nothing, plus 131 leftover sized renditions (harmless cruft).

## Why orphan ownership can't be cleanly recovered

- S3 object metadata is empty; owner is just the AWS account.
- The `<uuid>` in scenario-upload paths is a random `uuid4()` — 0 of 330 match any
  `users_user.id` or `identities_identity.id`.
- No usable backup: Render PITR only reaches back to 2026-05-31 (months after the
  orphaning); on-disk dumps in `server/backups/` are from 2025-08-04.
- Gemini orphans (`identities/identity/*`) likewise have random `uuid4()` filenames
  with no embedded name, so they can't even be name-matched — they're only
  recoverable if still referenced by a live identity row (the 41 "linked" ones).

> ⚠️ These CSVs contain client email addresses. Keep in the private repo only.

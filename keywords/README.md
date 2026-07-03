# Keywords — Adapt the Pipeline to Any Role

All keyword intelligence lives in JSON here — no Python knowledge needed to
retarget the whole pipeline at a different career.

## Files

- `data-eng.json` — Data & AI Engineering (the default)

`config.json` → `keywords_file` decides which pack is active.

## Make your own pack (PM, SWE, marketing, anything)

1. Copy the default: `cp keywords/data-eng.json keywords/my-role.json`
2. Edit the five sections:

   | Key              | What it is                                                            |
   | ---------------- | ---------------------------------------------------------------------- |
   | `known_keywords` | Every term worth matching for your field (~150 works well)            |
   | `aliases`        | Terms that count as each other (`"k8s": ["kubernetes"]`)              |
   | `skills_clusters`| Your resume's skills-section categories → which keywords belong where |
   | `archetypes`     | 4–6 flavors of your role + their signal words (used to classify JDs)  |
   | `common_words`   | Noise to ignore when scanning JDs for unknown terms                    |

3. Point `config.json` at it: `"keywords_file": "keywords/my-role.json"`

Easiest way to build one: paste 3–5 job descriptions for your target role into
Claude Code and ask it to draft the JSON in this format — then prune by hand.

Built a good pack? PRs welcome — that's one whole profession helped.

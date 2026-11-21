# SoilSutra_Web
Source of soilsutra.com: practical, source-backed vermicompost science, plus SoilSutra's soil tech and consulting.
Research content comes from the private SoilSutra_Agent, which writes one file per article into `content/articles/`.

## What is here

| Path | What |
|---|---|
| `content/_index.md` | Home page text (headline and one sentence). |
| `content/about.md`, `content/how-we-check.md` | Plain pages. Edit as ordinary Markdown. |
| `content/articles/*.md` | Articles written by the agent. Front matter holds the numbered references and exact quotes; the template draws them. |
| `data/learning_path.yaml` | The learning path: the stages (tabs) on the Guides page, ordered beginner to expert, and the topics in each. See below. |
| `layouts/`, `assets/css/main.css` | The design. Fonts are self-hosted in `static/fonts` (Literata, Bricolage Grotesque; both SIL Open Font License). |
| `hugo.toml` | Site settings: `signupAction` (email service form address), `contactEmail` (empty means that block is hidden) and `showPlannedTopics` (list topics that are planned but not yet published). |
| `.github/workflows/deploy.yml` | Builds with Hugo and publishes to GitHub Pages on every push to `main`. |

## An article's life

1. In SoilSutra_Agent: `python main.py draft feedstock` writes `content/articles/feedstock.md` with `draft: true`, `status: draft`.
2. You read it. Fix wording by hand if needed (keep the `[n](#sn)` links).
3. To publish, change two lines in the front matter: `status: approved` and `draft: false`. Commit and push.
4. The deploy action builds the site. It refuses to publish if any draft was built.

The agent will not overwrite an approved article.

## The learning path (Guides page)

The Guides page shows eight stages as tabs, from Basics (beginner) to Composition science (expert). The home page shows the same stages as numbered steps, and each article links back to its stage.

- The order, names and levels live in `data/learning_path.yaml`. Edit that file to rename, reorder, add or remove a stage or topic. No template change is needed.
- An article is placed by its front matter `topic:`. It appears under the stage whose topic `key` is equal to it. The existing `topic: "feedstock"` sits under Feeding.
- A topic with no published article is listed as planned. A stage with none says its guides are being researched. Nothing is invented to fill a stage.
- An article whose `topic` is missing from the file is not lost: it shows under "Other guides" and the build prints a warning. Add its key to the file to place it.
- Without JavaScript the tabs become plain sections in the same order, so the page still works.

## Rules for this public repo

- Only articles and site files live here. Never the research log, private findings, market notes or customer notes.
- Every sentence in an article cites a numbered source; do not delete the references block.

## Content contract

Front matter written by the agent: `title`, `topic` (must equal a topic `key` in `data/learning_path.yaml`), `status` (draft | approved), `draft`, `updated`, `confidence`, `sources`, `lang`,
`summary`, `lede`, `lede_refs`, `references` (each with `n`, `title`, `url`, `host`, `finding`, `quote`). Body: Markdown where each
sentence ends with links like `[2](#s2)`.

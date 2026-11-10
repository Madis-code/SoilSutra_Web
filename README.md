# SoilSutra_Web
Source of soilsutra.com: practical, source-backed vermicompost science, plus SoilSutra's soil tech and consulting.
Research content comes from the private SoilSutra_Agent, which writes one file per article into `content/articles/`.

## What is here

| Path | What |
|---|---|
| `content/_index.md` | Home page text (headline and one sentence). |
| `content/about.md`, `content/how-we-check.md` | Plain pages. Edit as ordinary Markdown. |
| `content/articles/*.md` | Articles written by the agent. Front matter holds the numbered references and exact quotes; the template draws them. |
| `layouts/`, `assets/css/main.css` | The design. Fonts are self-hosted in `static/fonts` (Literata, Bricolage Grotesque; both SIL Open Font License). |
| `hugo.toml` | Site settings: `signupAction` (email service form address) and `contactEmail`. Empty means that block is hidden. |
| `.github/workflows/deploy.yml` | Builds with Hugo and publishes to GitHub Pages on every push to `main`. |

## An article's life

1. In SoilSutra_Agent: `python main.py draft feedstock` writes `content/articles/feedstock.md` with `draft: true`, `status: draft`.
2. You read it. Fix wording by hand if needed (keep the `[n](#sn)` links).
3. To publish, change two lines in the front matter: `status: approved` and `draft: false`. Commit and push.
4. The deploy action builds the site. It refuses to publish if any draft was built.

The agent will not overwrite an approved article.

## Rules for this public repo

- Only articles and site files live here. Never the research log, private findings, market notes or customer notes.
- Every sentence in an article cites a numbered source; do not delete the references block.

## Content contract

Front matter written by the agent: `title`, `topic`, `status` (draft | approved), `draft`, `updated`, `confidence`, `sources`, `lang`,
`summary`, `lede`, `lede_refs`, `references` (each with `n`, `title`, `url`, `host`, `finding`, `quote`). Body: Markdown where each
sentence ends with links like `[2](#s2)`.

# SoilSutra_Web
Source of soilsutra.com: practical, source-backed vermicompost science, plus SoilSutra's soil tech and consulting.
Research content comes from the private SoilSutra_Agent, which writes one file per article into `content/articles/`.

## What is here

| Path | What |
|---|---|
| `content/_index.md` | Home page text (headline and one sentence). |
| `content/about.md`, `content/how-we-check.md` | Plain pages. Edit as ordinary Markdown. Hindi versions sit beside them as `about.hi.md` and so on. |
| `content/articles/*.md` | Articles written by the agent. Front matter holds the numbered references and exact quotes; the template draws them. |
| `data/learning_path.yaml` | The learning path: the stages (tabs) on the Guides page, ordered beginner to expert, and the topics in each. See below. |
| `layouts/`, `assets/css/main.css` | The design. Fonts are self-hosted in `static/fonts` (Literata, Bricolage Grotesque, and Noto Sans Devanagari for Hindi; all SIL Open Font License). |
| `i18n/en.yaml`, `i18n/hi.yaml` | Every word the design shows (buttons, labels, notes) in English and Hindi. Same keys in both files. |
| `tools/check_translation.py` | Checks a Hindi article against its English original. Runs in the deploy action. See "Languages". |
| `hugo.toml` | Site settings, including the two languages. `signupAction` (email service form address), `contactEmail` (empty means that block is hidden) and `showPlannedTopics` (list topics that are planned but not yet published). |
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

## Languages: English and Hindi

The header has an English | हिन्दी switch. English lives at `/`, Hindi at `/hi/`. Each page is a real page of its own, so a farmer searching in Hindi can find it and you can review it before it goes live.

- **Words in the design** (menus, buttons, notes) are in `i18n/en.yaml` and `i18n/hi.yaml`. Add a key to both files.
- **Stage and topic names** in `data/learning_path.yaml` carry an `en` and a `hi` text.
- **Pages** (`about`, `how-we-check`, home text, Guides intro) have a `.hi.md` twin next to the English file. Edit them as plain Markdown.
- **Articles** are translated one at a time (below). Until an article has a Hindi version, the Hindi Guides page still lists it, marked "English only", and links to the English page. Nothing is hidden and nothing is machine-translated on the fly.
- The switch remembers the last choice in the browser, and only uses it for someone arriving from outside the site, so a link to the English original always opens in English.
- Why not an automatic browser translation: it would also rewrite the exact quotes from sources and could change a number, and nobody can review what it produces. A translation here is a file you read before it ships.

### Translating an article

1. The English article must be approved and live first.
2. Copy `feedstock.md` to `feedstock.hi.md`. Set `draft: true`, `status: draft`, `lang: hi`.
3. Translate only: `title`, `summary`, `lede`, each reference's `finding`, and the body (headings and sentences).
   Copy everything else unchanged: `topic`, `updated`, `confidence`, `sources`, `lede_refs`, and every reference's `n`, `title`, `url`, `host` and **`quote`**. Quotes stay in the source's own English words.
4. Keep every `[n](#sn)` marker at the end of its sentence. Keep numbers as 0-9 digits (50:1, 12 to 24).
5. Run `python tools/check_translation.py` (needs `pip install pyyaml`). While the file is a draft it only warns; fix every warning.
6. Read it. When you are happy, change `status: approved` and `draft: false`, commit and push.
7. If the English article is updated later, its `updated` date changes and the check fails until the Hindi is redone from the new English and given the same date. A stale translation cannot go live.

The check proves the mechanical things: sources and quotes untouched, numbers unchanged, every sentence cited, nothing left in English, nothing added. It cannot prove the Hindi reads well. That is your reading. `python tools/test_check_translation.py` tests the check itself.

The agent (SoilSutra_Agent) stays English only. It never produces or stores Hindi.

## Rules for this public repo

- Only articles and site files live here. Never the research log, private findings, market notes or customer notes.
- Every sentence in an article cites a numbered source; do not delete the references block.

## Content contract

Front matter written by the agent: `title`, `topic` (must equal a topic `key` in `data/learning_path.yaml`), `status` (draft | approved), `draft`, `updated`, `confidence`, `sources`, `lang`,
`summary`, `lede`, `lede_refs`, `references` (each with `n`, `title`, `url`, `host`, `finding`, `quote`). Body: Markdown where each
sentence ends with links like `[2](#s2)`.

The source markers must stay as written, `[2](#s2)`: the evidence panel and the marker styling look for exactly that form (`layouts/_default/_markup/render-link.html` keeps Hugo from rewriting it).

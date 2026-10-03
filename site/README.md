# Site text for lineageimperative.org

The text of the site's pages lives here, one Markdown file per page. The site loads each file from this
repository when the page opens, the same way the Framework page loads the paper and the Citations page loads
`docs/CITATIONS.md`. A change to the site's text is a commit here: reviewed, versioned and diffable like
every other change to the project, and live once it is pushed to `main`.

| Page | File | Address |
|---|---|---|
| Home | `home.md` | / |
| Start Here | `start-here.md` | /start-here |
| About | `about.md` | /about |
| Engage | `engage.md` | /contact |
| Technical Resources | `resources.md` | /resources |
| Citations | `citations.md` (the page intro; the bibliography is `docs/CITATIONS.md`) | /citations |
| Results | `data.md`: the page intro and status notice; the dataset browser and the test archive stay in the site builder | /data |
| Primer (replaces Explore) | `primer.md`: the guided tour's text; the tour itself is built with the live view | /explore |

Each file is fetched from `https://raw.githubusercontent.com/MYotko/AI-Succession-Problem/main/site/<file>`.

## Conventions

The site renders a small, fixed subset of Markdown into its own styles:

- **Front matter** sets the page's `eyebrow` (the small label above the title), `title` and `subtitle`. The page's
  search title and description stay in the site builder, so that link previews and search engines see them
  without running the page.
- **`## LABEL`** starts a section. The label is shown in the site's spaced capitals.
- **`> text`** is a pull quote.
- **`### Heading`** inside a section is a card or a sub-block. A heading that begins with a number (`### 01
  Title`) is a numbered card.
- **A line made only of links**, separated by ` · `, is a row of buttons.
- **`{{name}}`** on its own line marks a component the site builder supplies itself: `{{essays}}`, `{{audio}}`,
  `{{author}}`, `{{contact}}`, `{{form}}`, `{{scenarios}}`, `{{simulation-files}}`, `{{validator-files}}`,
  `{{datasets}}` and `{{archive}}`.
- **Primer only:**
  - `{{visual: name}}` places a stop's illustration;
  - `{{game}}` places the interactive game;
  - `{{map: tour}}` shows the live view's framework map, walking its rings from the inside out;
  - `{{status: Label | one line}}` is the stop's status marker: the label shows, and the line appears on tap.
- Everything else is ordinary Markdown: paragraphs, **bold**, *italics*, lists and links.

## Rules for the text

- Claims match the project's current status: the README's status notice, the claims register and the latest
  update. Nothing here reports a sealed result.
- No em dashes. The author's employer is not named.
- Run `python site/check.py` before committing. It refuses withdrawn claims, em dashes and private details.

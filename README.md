# Seven Databases in Seven Weeks: Study Guide

A chapter-by-chapter study guide to *Seven Databases in Seven Weeks* (Eric Redmond and Jim R. Wilson, 2012). Every chapter and "Day" is explained step by step, with diagrams, extra examples, notes on what has changed since 2012, and a scored quiz at the end of each chapter.

## Structure

```
public/index.html     the finished site (one self-contained page), served by Netlify
src/chapters/*.md     chapter content, diagrams and quizzes
src/template.html     page layout, styles and the quiz engine
src/build.py          turns the chapters into public/index.html
netlify.toml          tells Netlify to publish the public/ folder
```

## Deploying on Netlify

1. In Netlify, choose **Add new site → Import an existing project → GitHub**, and pick this repository.
2. Leave the build command empty. The publish directory (`public`) is read from `netlify.toml`.
3. Deploy. Every push to the main branch redeploys automatically.

## Editing the content

Edit the Markdown files in `src/chapters/`, then rebuild the page and commit both the source and the result:

```bash
pip install markdown pygments
python3 src/build.py
git add . && git commit -m "Update chapter" && git push
```

Chapter files use a few extras on top of Markdown:

| Syntax | Meaning |
|---|---|
| `title:` / `lead:` at the top | Chapter title and intro line |
| `:::fig Caption` … `:::` | A figure; the body is an inline SVG diagram |
| `:::modern Title` … `:::` | A callout box (`modern`, `deep`, `tip`, `warn`, `analogy`, `key`, `example`) |
| `@@quiz` | Starts the quiz. `Q:` question, `C:` code line, `-` wrong option, `+` right option, `?` explanation |

Quiz scores are stored only in each reader's own browser (localStorage).

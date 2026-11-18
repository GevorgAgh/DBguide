#!/usr/bin/env python3
"""Assemble the study-guide page from chapter Markdown files.

Chapter file syntax (beyond Markdown):
  title: / lead:            front-matter lines at the top
  :::fig Caption            figure; body is raw SVG; ends with :::
  :::modern Title           callout (modern|deep|tip|warn|analogy|key|example); markdown body; ends with :::
  @@quiz                    starts the quiz section (to end of file)
     Q: question   C: code line   - wrong   + right   ? explanation
"""
import html, json, re, sys
from pathlib import Path
import markdown

ROOT = Path(__file__).parent
CH = ROOT / "chapters"

ORDER = [
    ("home", "", "Start here", "How to use this guide", "g-none", "home.md"),
    ("intro", "1", "Introduction", "The five genres", "g-none", "ch1.md"),
    ("postgresql", "2", "PostgreSQL", "Relational", "g-rel", "ch2.md"),
    ("riak", "3", "Riak", "Key-value", "g-kv", "ch3.md"),
    ("hbase", "4", "HBase", "Columnar", "g-col", "ch4.md"),
    ("mongodb", "5", "MongoDB", "Document", "g-doc", "ch5.md"),
    ("couchdb", "6", "CouchDB", "Document", "g-doc", "ch6.md"),
    ("neo4j", "7", "Neo4J", "Graph", "g-graph", "ch7.md"),
    ("redis", "8", "Redis", "Key-value", "g-kv", "ch8.md"),
    ("wrapup", "9", "Wrapping Up", "Choosing a database", "g-none", "ch9.md"),
    ("cap", "A", "The CAP Theorem", "Appendix", "g-none", "cap.md"),
]

EXT = ["fenced_code", "tables", "codehilite", "attr_list", "sane_lists"]
EXT_CFG = {"codehilite": {"css_class": "hl", "guess_lang": False}}

MARKERS = {
    "arr": 'fill="currentColor"', "arra": 'class="fa"', "arrg": 'class="fg"', "arrr": 'class="fr"',
    "arrw": 'class="fw"', "arrv": 'class="fv"', "arrp": 'class="fp"', "arrm": 'class="fm"', "arrx": 'class="gf"',
}
counter = {"svg": 0, "tok": 0}
stash = {}


def md(text):
    return markdown.markdown(text, extensions=EXT, extension_configs=EXT_CFG)


def inline_md(text):
    out = md(text).strip()
    if out.startswith("<p>") and out.endswith("</p>") and out.count("<p>") == 1:
        out = out[3:-4]
    return out


def token(htmlstr):
    counter["tok"] += 1
    t = f"STASHTOKEN{counter['tok']:05d}X"
    stash[t] = htmlstr
    return f"\n\n{t}\n\n"


def fix_svg(svg, label):
    counter["svg"] += 1
    n = counter["svg"]
    used = sorted(set(re.findall(r"url\(#(arr[a-z]?)\)", svg)))
    defs = ""
    for m in used:
        if m not in MARKERS:
            sys.exit(f"unknown marker {m}")
        defs += (f'<marker id="{m}-{n}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                 f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" {MARKERS[m]}/></marker>')
        svg = svg.replace(f"url(#{m})", f"url(#{m}-{n})")
    svg = svg.strip()
    head_end = svg.index(">") + 1
    head = svg[:head_end]
    if "role=" not in head:
        head = head[:-1] + f' role="img" aria-label="{html.escape(label, quote=True)}">'
    if defs:
        head += f"<defs>{defs}</defs>"
    return head + svg[head_end:]


def preprocess(text):
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^:::(\w+)\s*(.*)$", line)
        if m:
            kind, title = m.group(1), m.group(2).strip()
            body, i = [], i + 1
            depth = 0
            while i < len(lines):
                if re.match(r"^:::\w+", lines[i]):
                    depth += 1
                elif lines[i].strip() == ":::":
                    if depth == 0:
                        break
                    depth -= 1
                body.append(lines[i])
                i += 1
            if i >= len(lines):
                sys.exit(f"unclosed ::: block: {line}")
            inner = "\n".join(body)
            if kind == "fig":
                label = re.sub(r"<[^>]+>|\*\*|`", "", title)
                fig = (f'<figure class="fig"><div class="scroll">{fix_svg(inner, label)}</div>'
                       f'<figcaption>{inline_md(title)}</figcaption></figure>')
                out.append(token(fig))
            else:
                if kind not in ("modern", "deep", "tip", "warn", "analogy", "key", "example"):
                    sys.exit(f"unknown callout {kind}")
                ttl = f'<p class="ctitle">{inline_md(title)}</p>' if title else ""
                out.append(token(f'<div class="callout {kind}">{ttl}{md(preprocess(inner))}</div>'))
            i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def unstash(h):
    for _ in range(4):
        for t, v in stash.items():
            h = h.replace(f"<p>{t}</p>", v).replace(t, v)
    return h


def parse_quiz(text, vid):
    qs, cur = [], None
    for raw in text.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("Q: "):
            cur = {"q": line[3:].strip(), "options": [], "answer": None, "why": "", "code": ""}
            qs.append(cur)
        elif cur is None:
            continue
        elif line.startswith("C: ") or line == "C:":
            cur["code"] += line[3:] + "\n"
        elif line.startswith("+ "):
            cur["answer"] = len(cur["options"]); cur["options"].append(line[2:].strip())
        elif line.startswith("- "):
            cur["options"].append(line[2:].strip())
        elif line.startswith("? "):
            cur["why"] += line[2:].strip()
        elif cur["why"]:
            cur["why"] += " " + line.strip()
        else:
            sys.exit(f"{vid}: unparsed quiz line: {line}")
    for k, q in enumerate(qs):
        if q["answer"] is None or len(q["options"]) < 3 or not q["why"]:
            sys.exit(f"{vid} quiz q{k+1} incomplete: {q['q']}")
        if not q["code"]:
            del q["code"]
        else:
            q["code"] = q["code"].rstrip("\n")
    return qs


def build():
    tpl = (ROOT / "template.html").read_text()
    nav, views, quizdata = [], [], []
    stats = []
    present = [o for o in ORDER if (CH / o[5]).exists()]
    for idx, (vid, num, title, sub, genre, fname) in enumerate(present):
        src = (CH / fname).read_text()
        meta = {}
        while True:
            m = re.match(r"^(title|lead):\s*(.*)\n", src)
            if not m:
                break
            meta[m.group(1)] = m.group(2).strip(); src = src[m.end():]
        quiz = None
        if "@@quiz" in src:
            src, qtext = src.split("@@quiz", 1)
            quiz = parse_quiz(qtext, vid)
        body = unstash(md(preprocess(src)))
        body = re.sub(r"<table>", '<div class="tbl"><table>', body).replace("</table>", "</table></div>")
        # ids on h2 for day chips
        chips = []
        def h2id(m):
            text = re.sub(r"<[^>]+>", "", m.group(1))
            slug = f"{vid}-" + re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40]
            chips.append((slug, text))
            return f'<h2 id="{slug}">{m.group(1)}</h2>'
        body = re.sub(r"<h2>(.*?)</h2>", h2id, body)

        is_home = vid == "home"
        if is_home:
            cards = []
            for (cv, cn, ct, cs, cg, cf) in ORDER[1:]:
                blurb = ""
                if (CH / cf).exists():
                    mm = re.search(r"^lead:\s*(.*)$", (CH / cf).read_text(), re.M)
                    blurb = mm.group(1) if mm else ""
                k = f"Chapter {cn}" if cn.isdigit() else f"Appendix {cn}"
                cards.append(f'<a class="card {cg}" href="#{cv}" data-quiz="{cv}"><span class="k">{k} · {html.escape(cs)}</span>'
                             f'<b>{html.escape(ct)}</b><p>{inline_md(blurb)}</p><span class="st">Quiz not taken yet</span></a>')
            body = body.replace("<p>@@cards</p>", f'<div class="cards">{"".join(cards)}</div>')
            head = (f'<header class="hero"><span class="kicker">Study guide · 1st edition, 2012 · explained for 2026</span>'
                    f'<h1>{html.escape(meta.get("title", title))}</h1><p class="lead">{inline_md(meta.get("lead", ""))}</p></header>')
        else:
            k = f"Chapter {num}" if num.isdigit() else f"Appendix {num}"
            chip_html = "".join(f'<a href="#{vid}" data-jump="{s}">{html.escape(t)}</a>' for s, t in chips)
            head = (f'<header class="chap-head"><span class="kicker">{k} · {html.escape(sub)}</span>'
                    f'<h1>{html.escape(meta.get("title", title))}</h1><p class="lead">{inline_md(meta.get("lead", ""))}</p>'
                    f'<nav class="daychips" aria-label="Sections in this chapter">{chip_html}'
                    f'{"<a href=\"#" + vid + "\" data-jump=\"quiz-" + vid + "\">Quiz</a>" if quiz else ""}</nav></header>')
        quiz_html = ""
        if quiz:
            quizdata.append(f'<script type="application/json" id="quizdata-{vid}">{json.dumps(quiz, ensure_ascii=False).replace("</", "<\\/")}</script>')
            quiz_html = (f'<section class="quiz" id="quiz-{vid}" data-quiz="{vid}"><h2>Check your understanding</h2>'
                         f'<p class="qintro">{len(quiz)} questions. Pick an answer to see whether it is right and why. '
                         f'Score {round(len(quiz)*0.7+0.4)} or more to pass. The answer order is shuffled each time.</p>'
                         f'<div class="qscore"><span></span><div class="meter"><i></i></div></div><div class="qlist"></div>'
                         f'<div class="qresult" role="status"><h3></h3><p></p><button type="button" class="btn retry">Retake the quiz</button></div></section>')
        prev_ = present[idx - 1] if idx > 0 else None
        next_ = present[idx + 1] if idx + 1 < len(present) else None
        pager = '<nav class="pager" aria-label="Chapter navigation">'
        if prev_:
            pager += f'<a href="#{prev_[0]}"><small>Previous</small><b>{html.escape(prev_[2])}</b></a>'
        if next_:
            pager += f'<a class="next" href="#{next_[0]}"><small>Next</small><b>{html.escape(next_[2])}</b></a>'
        pager += "</nav>"
        hidden = "" if is_home else " hidden"
        views.append(f'<section class="view {genre}" data-view="{vid}" data-genre="{genre}" data-title="{html.escape(title)}"{hidden}>'
                     f'{head}<div class="prose">{body}</div>{quiz_html}{pager}</section>')
        numcell = num if num else "★"
        nav.append(f'<li><a class="{genre}" href="#{vid}" data-view="{vid}"' + (f' data-quiz="{vid}"' if quiz else "") +
                   f'><span class="num">{numcell}</span><span class="ttl">{html.escape(title)}<small>{html.escape(sub)}</small></span>'
                   f'<span class="badge"></span></a></li>')
        stats.append((vid, len(src.split()), counter["svg"], len(quiz) if quiz else 0))
    out = (tpl.replace("{{NAV}}", "\n".join(nav)).replace("{{VIEWS}}", "\n".join(views))
           .replace("{{QUIZDATA}}", "\n".join(quizdata)).replace("{{QUIZCOUNT}}", str(len(quizdata)))
           .replace("{{ORDER}}", json.dumps([o[0] for o in present])))
    if "STASHTOKEN" in out:
        sys.exit("unresolved stash token")
    out_path = ROOT.parent / "public" / "index.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out)
    prev_svg = 0
    for vid, words, svgs, nq in stats:
        print(f"{vid:12} words={words:6} figures={svgs - prev_svg:3} quiz={nq}")
        prev_svg = svgs
    print(f"total size {len(out)/1024:.0f} KB")


if __name__ == "__main__":
    build()

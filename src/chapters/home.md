title: Seven Databases in Seven Weeks
lead: A chapter-by-chapter walkthrough of the book by Eric Redmond and Jim R. Wilson. Every chapter and every "Day" is explained step by step, with diagrams, extra examples, notes on what has changed since 2012, and a quiz at the end of each chapter.

## How to use this guide

<ol class="steps">
<li>Read the chapters in order. Each database chapter follows the book's three "Days": basics first, then querying, then distribution and advanced features.</li>
<li>Look at every diagram. Most ideas in this book (joins, hashing rings, replication, graphs) are easier to see than to read.</li>
<li>Take the quiz at the end of the chapter. Each answer explains why it is right or wrong. Score 70% or more to pass.</li>
<li>Track your progress in the chapter list. Your best quiz score is saved in this browser.</li>
</ol>

## The map of the book

The book visits seven databases, picked so that together they cover the five big "genres" of databases. Keep this map in mind: every chapter is one point on it.

:::fig **Seven databases, five genres.** The horizontal axis shows how much of your data's structure the database understands. Graph databases sit on their own axis, because they are built around relationships rather than records.
<svg class="dg" viewBox="0 0 720 260">
<line x1="40" y1="70" x2="680" y2="70" class="ln" marker-end="url(#arr)"/>
<text x="40" y="40" class="s">Database sees an opaque value</text>
<text x="680" y="40" class="s" text-anchor="end">Database understands a typed schema</text>
<circle cx="100" cy="70" r="9" class="fw"/>
<circle cx="280" cy="70" r="9" class="fv"/>
<circle cx="460" cy="70" r="9" class="fg"/>
<circle cx="640" cy="70" r="9" class="fa"/>
<text x="100" y="104" text-anchor="middle" class="b tw">Key-value</text>
<text x="100" y="124" text-anchor="middle">Riak (ch. 3)</text>
<text x="100" y="142" text-anchor="middle">Redis (ch. 8)</text>
<text x="280" y="104" text-anchor="middle" class="b tv">Columnar</text>
<text x="280" y="124" text-anchor="middle">HBase (ch. 4)</text>
<text x="460" y="104" text-anchor="middle" class="b tg">Document</text>
<text x="460" y="124" text-anchor="middle">MongoDB (ch. 5)</text>
<text x="460" y="142" text-anchor="middle">CouchDB (ch. 6)</text>
<text x="640" y="104" text-anchor="middle" class="b ta">Relational</text>
<text x="640" y="124" text-anchor="middle">PostgreSQL (ch. 2)</text>
<rect x="190" y="172" width="340" height="68" rx="10" class="bp"/>
<circle cx="230" cy="196" r="7" class="fp"/><circle cx="262" cy="220" r="7" class="fp"/><circle cx="214" cy="224" r="7" class="fp"/>
<line x1="230" y1="196" x2="262" y2="220" class="lp"/><line x1="230" y1="196" x2="214" y2="224" class="lp"/><line x1="214" y1="224" x2="262" y2="220" class="lp"/>
<text x="290" y="200" class="b tp">Graph</text>
<text x="290" y="220">Neo4J (ch. 7): relationships first</text>
</svg>
:::

## Reading the boxes

Throughout the guide you will see four kinds of highlighted boxes:

:::modern What's changed since 2012
The book was written in 2012. These boxes tell you what is different today: renamed commands, removed features, new versions, or a database whose company no longer exists.
:::

:::deep Going deeper
Extra explanation for ideas that the book moves through quickly, such as how a B-tree finds a row or why vector clocks detect conflicts.
:::

:::analogy An everyday picture
A comparison with something familiar, to make an abstract idea stick.
:::

:::warn A common mistake
A trap that catches many readers, or a place where the book's wording is easy to misunderstand.
:::

## Chapters

@@cards

## About the book

*Seven Databases in Seven Weeks* (Pragmatic Bookshelf, 2012) does not try to make you an expert in any single database. Its goal is to give you enough hands-on experience with each one that you can answer a practical question: **which database, or which combination of databases, best fits my problem?** The authors call the habit of using several databases together *polyglot persistence*, and the book ends by building an application that does exactly that.

The version numbers in the book are old (PostgreSQL 9.1, MongoDB 2.0, Neo4J 1.7, Redis 2.4). The ideas have aged much better than the commands. This guide teaches the ideas as the book presents them, then points out where today's tools work differently.

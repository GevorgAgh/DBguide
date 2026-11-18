title: Introduction
lead: Why so many databases exist, the six questions to ask about any of them, and the five genres the whole book is organized around.

## 1.1 Why this book exists

For about thirty years, "where do I store my data?" had one default answer: a **relational database**. You designed tables, wrote SQL, and bought a bigger server when things got slow.

Around 2005 to 2010 that answer stopped being enough for some companies. Google, Amazon and Facebook had more data than any single machine could hold, users all over the world, and a need to stay online even while servers failed. They built new kinds of databases to cope, published papers about them (Google's *BigTable*, Amazon's *Dynamo*), and the open-source world copied the ideas. These new systems were grouped under the loose label **NoSQL**.

NoSQL databases traded away some of what relational databases give you (joins, strict schemas, transactions across many tables) in exchange for something else:

- **Different data shapes**: documents, graphs, sorted sets, sparse columns.
- **Easy replication**: keeping copies of data on several machines.
- **High availability**: the system keeps answering even when a server dies.
- **Horizontal scaling**: growing by adding cheap machines instead of buying one huge one.
- **New ways to query**: mapreduce, graph traversals, HTTP requests.

:::analogy A carpenter's toolbelt
The authors compare databases to tools. A hammer is a great tool, but you would not use it to cut a board. A good builder knows every tool on the belt and picks the right one for each job. This book hands you seven tools and lets you swing each one.
:::

## 1.2 The central question

The whole book exists to answer one question:

> **Which database, or combination of databases, best resolves your problem?**

Notice the phrase "or combination". The authors do not expect one winner. Real systems often use two or three databases side by side, each doing the job it is best at.

To answer the question you need to understand your options, so for every database the book asks the same six questions. They are worth memorizing, because they work just as well when you evaluate a database at work.

### Question 1: What type of datastore is this?

Which **genre** does it belong to: relational, key-value, columnar, document or graph? The genre tells you most of what the database is good and bad at before you read a single page of its manual. Section 1.3 covers the genres in detail.

### Question 2: What was the driving force?

Every database was built by people trying to solve a specific problem, and that problem shaped every design decision.

- Relational databases were designed when **query flexibility** mattered most: store the data once, ask any question later.
- Columnar databases like HBase were designed to store **enormous amounts of data across many machines**. Relationships between data took a back seat.
- Riak was designed to **never go down**, even while machines fail.
- Redis was designed to be **as fast as possible**, so it keeps everything in memory.

If you know the driving force, you can predict the trade-offs.

### Question 3: How do you talk to it?

Each database has its own interface. The book always starts with an interactive shell when one exists, then moves to other options.

| Database | Main way to talk to it in the book |
|---|---|
| PostgreSQL | SQL in the `psql` shell, plus PL/pgSQL for stored procedures |
| Riak | HTTP requests with `curl` (REST) |
| HBase | the HBase shell (JRuby) and Thrift |
| MongoDB | JavaScript in the `mongo` shell |
| CouchDB | HTTP requests with `curl` (REST), JavaScript for views |
| Neo4J | Gremlin (a Groovy-based graph language) and REST |
| Redis | short commands in `redis-cli` |

Most programming examples use Ruby or JavaScript. The final chapter ties several databases together with Node.js.

### Question 4: What makes it unique?

Every database can write data and read it back. The differences are in everything else:

- Can you query on **any field**, or only by key?
- Does it have **indexes** for fast lookups?
- Does it support **ad hoc queries** (questions you think of later), or must queries be planned in advance?
- Is the **schema** a rigid contract enforced by the database, or just a loose habit?

### Question 5: How does it perform?

How does it work internally, and what does that cost? Does it support **sharding** (splitting data across machines) and **replication** (copying data to several machines)? Does it spread data evenly using **consistent hashing**, or keep similar data together? Is it tuned for reading, for writing, or for something else? How much tuning control do you get?

:::deep Sharding and replication in one picture
These two words appear in almost every chapter, so here is the difference.
**Sharding** splits the data: server A holds customers A to M, server B holds N to Z. Each server holds *part* of the data, so together they can hold more than one server could.
**Replication** copies the data: servers A, B and C each hold a full copy (or a copy of the same shard). If one dies, another can answer.
Big systems do both: data is split into shards, and every shard is replicated.
:::

:::fig **Sharding splits the data; replication copies it.** Large distributed databases usually combine the two: each shard lives on several machines.
<svg class="dg" viewBox="0 0 720 230">
<text x="170" y="22" text-anchor="middle" class="lg">Sharding</text>
<text x="170" y="40" text-anchor="middle" class="s">each server holds a different part</text>
<rect x="20" y="60" width="90" height="120" rx="8" class="bw"/>
<text x="65" y="85" text-anchor="middle" class="b">Server 1</text>
<text x="65" y="112" text-anchor="middle" class="mono">A – H</text>
<rect x="125" y="60" width="90" height="120" rx="8" class="bw"/>
<text x="170" y="85" text-anchor="middle" class="b">Server 2</text>
<text x="170" y="112" text-anchor="middle" class="mono">I – Q</text>
<rect x="230" y="60" width="90" height="120" rx="8" class="bw"/>
<text x="275" y="85" text-anchor="middle" class="b">Server 3</text>
<text x="275" y="112" text-anchor="middle" class="mono">R – Z</text>
<text x="170" y="210" text-anchor="middle" class="s">more servers = room for more data</text>
<line x1="360" y1="20" x2="360" y2="210" class="ln2 dash"/>
<text x="550" y="22" text-anchor="middle" class="lg">Replication</text>
<text x="550" y="40" text-anchor="middle" class="s">each server holds the same copy</text>
<rect x="400" y="60" width="90" height="120" rx="8" class="ba"/>
<text x="445" y="85" text-anchor="middle" class="b">Server 1</text>
<text x="445" y="112" text-anchor="middle" class="mono">A – Z</text>
<rect x="505" y="60" width="90" height="120" rx="8" class="ba"/>
<text x="550" y="85" text-anchor="middle" class="b">Server 2</text>
<text x="550" y="112" text-anchor="middle" class="mono">A – Z</text>
<rect x="610" y="60" width="90" height="120" rx="8" class="ba"/>
<text x="655" y="85" text-anchor="middle" class="b">Server 3</text>
<text x="655" y="112" text-anchor="middle" class="mono">A – Z</text>
<text x="550" y="210" text-anchor="middle" class="s">one server dies, the others still answer</text>
</svg>
:::

### Question 6: How does it scale?

"Scalable" means nothing until you say *what* you want to scale to. The book keeps this part light, but it sorts the seven databases into two groups that matter a lot:

- **Horizontal scaling (scale out)**: add more ordinary machines. MongoDB, HBase and Riak are built for this.
- **Vertical scaling (scale up)**: move to a bigger, more powerful machine. PostgreSQL, Neo4J and Redis traditionally scale this way.

:::fig **Scaling up versus scaling out.** Scaling up hits a ceiling (the biggest machine you can buy). Scaling out has no fixed ceiling, but the database must know how to spread data and work across machines.
<svg class="dg" viewBox="0 0 720 250">
<text x="170" y="24" text-anchor="middle" class="lg">Scale up (vertical)</text>
<rect x="40" y="130" width="50" height="60" rx="6" class="box"/>
<line x1="48" y1="146" x2="82" y2="146" class="ln2"/><line x1="48" y1="158" x2="82" y2="158" class="ln2"/>
<line x1="105" y1="160" x2="175" y2="160" class="ln" marker-end="url(#arr)"/>
<text x="140" y="150" text-anchor="middle" class="s">upgrade</text>
<rect x="190" y="50" width="110" height="140" rx="8" class="ba"/>
<line x1="202" y1="74" x2="288" y2="74" class="ln2"/><line x1="202" y1="90" x2="288" y2="90" class="ln2"/>
<line x1="202" y1="106" x2="288" y2="106" class="ln2"/><line x1="202" y1="122" x2="288" y2="122" class="ln2"/>
<text x="245" y="168" text-anchor="middle" class="s">more CPU, RAM</text>
<text x="170" y="225" text-anchor="middle">PostgreSQL · Neo4J · Redis</text>
<line x1="360" y1="20" x2="360" y2="230" class="ln2 dash"/>
<text x="550" y="24" text-anchor="middle" class="lg">Scale out (horizontal)</text>
<rect x="400" y="130" width="50" height="60" rx="6" class="box"/>
<line x1="408" y1="146" x2="442" y2="146" class="ln2"/><line x1="408" y1="158" x2="442" y2="158" class="ln2"/>
<line x1="465" y1="160" x2="525" y2="160" class="ln" marker-end="url(#arr)"/>
<text x="495" y="150" text-anchor="middle" class="s">add more</text>
<rect x="540" y="60" width="50" height="60" rx="6" class="bw"/>
<rect x="600" y="60" width="50" height="60" rx="6" class="bw"/>
<rect x="660" y="60" width="50" height="60" rx="6" class="bw"/>
<rect x="540" y="130" width="50" height="60" rx="6" class="bw"/>
<rect x="600" y="130" width="50" height="60" rx="6" class="bw"/>
<rect x="660" y="130" width="50" height="60" rx="6" class="bw"/>
<text x="550" y="225" text-anchor="middle">Riak · HBase · MongoDB</text>
</svg>
:::

The authors are clear that the book is a tour, not a training course. Each of these databases deserves a whole book of its own. The goal is that by the end you understand each one's strengths and how they differ.

## 1.3 The five genres

Databases can be grouped into genres the way music can. Any song uses the same twelve notes, but some songs suit a quiet evening and some suit a party. Likewise, most data problems *could* be solved with most databases. The question is never "*can* I store this data here?" but "***should* I?**" The answer depends on your problem, your usage patterns and your resources.

To compare the genres fairly, we will store the same small piece of data in each one: **Ann has two friends, Bob and Cal, and Ann likes jazz.**

:::fig **The same data in five shapes.** Each genre gives the database a different amount of understanding about what it stores. Notice that the key-value store sees Ann's data as one opaque blob, while the graph stores the friendships themselves as data.
<svg class="dg wide" viewBox="0 0 720 500">
<rect x="0" y="0" width="350" height="150" rx="10" class="soft"/>
<text x="14" y="24" class="b ta">Relational</text>
<text x="14" y="48" class="s">users</text>
<rect x="14" y="54" width="130" height="80" rx="4" class="box"/>
<line x1="14" y1="74" x2="144" y2="74" class="ln2"/><line x1="44" y1="54" x2="44" y2="134" class="ln2"/>
<text x="20" y="68" class="mono b">id</text><text x="52" y="68" class="mono b">name</text>
<text x="20" y="90" class="mono">1</text><text x="52" y="90" class="mono">Ann</text>
<text x="20" y="108" class="mono">2</text><text x="52" y="108" class="mono">Bob</text>
<text x="20" y="126" class="mono">3</text><text x="52" y="126" class="mono">Cal</text>
<text x="170" y="48" class="s">friendships</text>
<rect x="170" y="54" width="160" height="62" rx="4" class="box"/>
<line x1="170" y1="74" x2="330" y2="74" class="ln2"/><line x1="245" y1="54" x2="245" y2="116" class="ln2"/>
<text x="176" y="68" class="mono b">user_id</text><text x="252" y="68" class="mono b">friend_id</text>
<text x="176" y="90" class="mono">1</text><text x="252" y="90" class="mono">2</text>
<text x="176" y="108" class="mono">1</text><text x="252" y="108" class="mono">3</text>
<text x="170" y="136" class="s">linked by id, joined by SQL</text>
<rect x="370" y="0" width="350" height="150" rx="10" class="soft"/>
<text x="384" y="24" class="b tw">Key-value</text>
<rect x="384" y="40" width="90" height="30" rx="4" class="bw"/>
<text x="429" y="60" text-anchor="middle" class="mono">user:1</text>
<line x1="478" y1="55" x2="508" y2="55" class="ln" marker-end="url(#arr)"/>
<rect x="512" y="40" width="194" height="30" rx="4" class="fm" opacity="0.25"/>
<text x="609" y="60" text-anchor="middle" class="mono">{name:Ann, friends:[2,3]}</text>
<rect x="384" y="80" width="90" height="30" rx="4" class="bw"/>
<text x="429" y="100" text-anchor="middle" class="mono">user:2</text>
<line x1="478" y1="95" x2="508" y2="95" class="ln" marker-end="url(#arr)"/>
<rect x="512" y="80" width="194" height="30" rx="4" class="fm" opacity="0.25"/>
<text x="609" y="100" text-anchor="middle" class="mono">{name:Bob}</text>
<text x="384" y="136" class="s">the value is a sealed box: fetch it by key, nothing else</text>
<rect x="0" y="166" width="350" height="160" rx="10" class="soft"/>
<text x="14" y="190" class="b tv">Columnar</text>
<text x="14" y="214" class="s mono">row key</text>
<text x="96" y="214" class="s mono">info:</text>
<text x="210" y="214" class="s mono">friends:</text>
<rect x="14" y="222" width="70" height="36" rx="4" class="bv"/>
<text x="49" y="245" text-anchor="middle" class="mono">ann</text>
<rect x="92" y="222" width="104" height="36" rx="4" class="box"/>
<text x="100" y="245" class="mono">name=Ann</text>
<rect x="204" y="222" width="130" height="36" rx="4" class="box"/>
<text x="212" y="245" class="mono">bob=· cal=·</text>
<rect x="14" y="266" width="70" height="36" rx="4" class="bv"/>
<text x="49" y="289" text-anchor="middle" class="mono">bob</text>
<rect x="92" y="266" width="104" height="40" rx="4" class="box"/>
<text x="100" y="283" class="mono">name=Bob</text>
<text x="100" y="297" class="mono">city=Paris</text>
<text x="210" y="289" class="s">no friends: no cells,</text>
<text x="210" y="303" class="s">no storage used</text>
<text x="14" y="320" class="s">each row has its own set of columns, grouped in families</text>
<rect x="370" y="166" width="350" height="160" rx="10" class="soft"/>
<text x="384" y="190" class="b tg">Document</text>
<rect x="384" y="200" width="322" height="112" rx="6" class="bg"/>
<text x="396" y="222" class="mono">{ "_id": 1,</text>
<text x="412" y="240" class="mono">"name": "Ann",</text>
<text x="412" y="258" class="mono">"likes": ["jazz"],</text>
<text x="412" y="276" class="mono">"friends": [ {"name":"Bob"},</text>
<text x="528" y="294" class="mono">{"name":"Cal"} ] }</text>
<rect x="0" y="342" width="720" height="158" rx="10" class="soft"/>
<text x="14" y="366" class="b tp">Graph</text>
<circle cx="200" cy="420" r="30" class="bp"/><text x="200" y="425" text-anchor="middle" class="b">Ann</text>
<circle cx="360" cy="380" r="26" class="bp"/><text x="360" y="385" text-anchor="middle">Bob</text>
<circle cx="360" cy="462" r="26" class="bp"/><text x="360" y="467" text-anchor="middle">Cal</text>
<circle cx="70" cy="440" r="26" class="box"/><text x="70" y="445" text-anchor="middle">jazz</text>
<line x1="228" y1="410" x2="332" y2="388" class="lp" marker-end="url(#arrp)"/>
<line x1="228" y1="430" x2="332" y2="455" class="lp" marker-end="url(#arrp)"/>
<line x1="171" y1="425" x2="98" y2="437" class="ln" marker-end="url(#arr)"/>
<text x="280" y="388" text-anchor="middle" class="s">FRIEND</text>
<text x="280" y="458" text-anchor="middle" class="s">FRIEND</text>
<text x="134" y="420" text-anchor="middle" class="s">LIKES</text>
<line x1="386" y1="384" x2="470" y2="410" class="ln dash" marker-end="url(#arr)"/>
<circle cx="500" cy="416" r="26" class="bp"/><text x="500" y="421" text-anchor="middle">Dee</text>
<text x="432" y="386" class="s">FRIEND</text>
<text x="540" y="400" class="s">"Friends of Ann's friends?"</text>
<text x="540" y="418" class="s">Just follow the arrows</text>
<text x="540" y="436" class="s">two steps out.</text>
</svg>
:::

### Relational

This is the model most people picture when they hear "database". A relational database management system (**RDBMS**) stores data in **tables** made of **rows** and **columns**. Every column has a **type** (number, text, date and so on), and the database enforces it. You talk to it in **SQL** (Structured Query Language).

Its secret weapon is its mathematical foundation, **set theory** (relational algebra). Because tables are mathematical sets, the database can **join** them, combine them and filter them into new tables you never stored. You do not have to know in advance which questions you will ask.

- **Database in the book:** PostgreSQL. The oldest and most battle-tested database in the book, very close to the SQL standard, so it serves as the baseline everything else is compared with.
- **Other examples:** MySQL, SQLite, H2, HSQLDB.
- **Strength:** flexible queries and strong guarantees about your data.
- **Cost:** you must design the structure (schema) before you store anything.

### Key-value

The simplest model. A key-value (KV) store is a giant dictionary or hash map: you give it a **key**, it gives you back a **value**. A file system is a good everyday example: the file path is the key, the file contents are the value.

Some KV stores let values be lists or hashes, and some let you loop through keys, but neither is required. Because the model asks so little, KV stores can be **extremely fast** and easy to spread across machines. The price is that they are poor at complex questions such as "all users older than 30 who live in Paris".

- **Databases in the book:** Riak and Redis, two very different takes on the idea.
  - **Riak** speaks HTTP and REST natively and is a faithful implementation of Amazon's *Dynamo* design. It uses *vector clocks* to resolve conflicts, *links* to connect keys, and was the first database in the book to support *mapreduce* queries.
  - **Redis** keeps data in memory and supports rich value types (lists, sets, sorted sets, hashes) plus publish-subscribe messaging and blocking queues. It is blazing fast, but it can lose recent writes if the machine fails, which makes it ideal for caches and message brokers. The book saves it for last so it can glue other databases together.
- **Other examples:** memcached, Voldemort.

### Columnar

In a **column-oriented** database, the values of one column are stored together on disk, instead of keeping each row together as relational databases do. That sounds like a small detail, but it changes a lot:

- Adding a column is cheap, and it happens **row by row**: each row can have different columns, or none at all.
- Empty cells take **no storage**, so very sparse tables cost nothing extra.
- In structure, columnar sits roughly **midway between relational and key-value**.

- **Database in the book:** HBase. Modeled on Google's *BigTable* paper and built on Hadoop, it is designed to run on clusters of cheap machines. It gives strong consistency, has tables with rows and columns (which feels familiar to SQL users), and offers **versioning** and **compression** out of the box.
- **Other examples:** Cassandra, Hypertable.

:::deep Row storage versus column storage on disk
Imagine a table of people with columns *name*, *age*, *city*.
A **row store** writes to disk: `Ann,31,Paris | Bob,25,Rome | Cal,40,Oslo`. Fetching one whole person is fast.
A **column store** writes: `Ann,Bob,Cal | 31,25,40 | Paris,Rome,Oslo`. Scanning one column across millions of rows (average age, say) is fast, and similar values next to each other compress very well.
HBase actually groups columns into **column families** and stores each family together, which is why the book calls it "column family" storage.
:::

### Document

A document database stores **documents**. A document is like a hash or JSON object: it has a unique ID, and its values can be numbers, strings, lists, or **other documents nested inside**. There is no fixed schema, so two documents in the same collection can look completely different. The database still understands the fields, so it can index and query them.

- **Databases in the book:** MongoDB and CouchDB.
  - **MongoDB** (from "humongous") is designed for huge data. It aims to stay **consistent**: after you write a value, the next read returns it. It supports atomic operations like incrementing a value, deep queries into nested documents, and mapreduce, all in JavaScript. People coming from SQL find it familiar.
  - **CouchDB** runs everywhere from data centers to phones. Written in Erlang, it is extremely hard to corrupt and stays available through network drops and hardware failures. Its queries are mapreduce **views** written in JavaScript, and those views are themselves stored as documents and replicated like any other data.

### Graph

A graph database stores **nodes** (things) and **relationships** between them. Both can carry properties, which are key-value pairs. Its real strength is **traversal**: starting at one node and following relationships to find connected data.

Questions like "friends of friends who also like jazz" are natural here and painful elsewhere. In SQL each extra hop means another join, and joins over large tables get slow. In a graph, each hop is just following a pointer.

- **Database in the book:** Neo4J, the most popular graph database. Common in social networks and recommendation engines.

### Polyglot persistence

In real systems, databases are rarely used alone. A single relational database is still common, but it is increasingly normal to use **several databases together**, each doing what it does best, so that the whole is stronger than any part. This is called **polyglot persistence**, by analogy with a person who speaks many languages.

:::fig **Polyglot persistence: one application, several databases.** Each store holds the data whose shape and access pattern it suits best. The book builds a smaller version of this at the end of the Redis chapter, with Redis, CouchDB and Neo4J.
<svg class="dg" viewBox="0 0 720 230">
<rect x="260" y="14" width="200" height="50" rx="10" class="box"/>
<text x="360" y="44" text-anchor="middle" class="b">Online shop application</text>
<rect x="20" y="150" width="190" height="62" rx="10" class="ba"/>
<text x="115" y="176" text-anchor="middle" class="b">PostgreSQL</text>
<text x="115" y="196" text-anchor="middle" class="s">relational</text>
<rect x="265" y="150" width="190" height="62" rx="10" class="bw"/>
<text x="360" y="176" text-anchor="middle" class="b">Redis</text>
<text x="360" y="196" text-anchor="middle" class="s">key-value, in memory</text>
<rect x="510" y="150" width="190" height="62" rx="10" class="bp"/>
<text x="605" y="176" text-anchor="middle" class="b">Neo4J</text>
<text x="605" y="196" text-anchor="middle" class="s">graph</text>
<line x1="300" y1="66" x2="140" y2="146" class="ln" marker-end="url(#arr)"/>
<line x1="360" y1="66" x2="360" y2="146" class="ln" marker-end="url(#arr)"/>
<line x1="420" y1="66" x2="580" y2="146" class="ln" marker-end="url(#arr)"/>
<text x="190" y="98" text-anchor="end" class="s">orders, payments</text>
<text x="190" y="114" text-anchor="end" class="s">(must never be wrong)</text>
<text x="366" y="104" class="s">sessions, cart, cache</text>
<text x="366" y="120" class="s">(must be fast)</text>
<text x="528" y="98" class="s">"customers who bought</text>
<text x="528" y="114" class="s">this also bought…"</text>
</svg>
:::

## 1.4 Onward and upward

The authors describe the moment as a **Cambrian explosion** of data storage: a sudden burst of new species, like the explosion of animal life 500 million years ago. Their predictions:

- No single approach, relational or otherwise, will dominate everything.
- Databases will become more **specialized**, each suited to a particular set of problems, with plenty of overlap.
- Just as companies hire relational DBAs today, there will be specialists in non-relational databases.

Their advice is to treat databases like programming languages and libraries: tools every developer should know. You cannot master the craft without knowing your options.

:::modern Were they right?
Mostly, yes. In 2026 it is completely normal for one company to run PostgreSQL, Redis, a search engine such as Elasticsearch or OpenSearch, and a cloud key-value store like Amazon DynamoDB side by side.
Two twists the authors could not see coming:
- **Relational databases fought back.** PostgreSQL added JSON documents (the `jsonb` type), full-text search, and vector search through extensions such as pgvector. For many projects it now covers jobs that once needed a separate NoSQL database, and it is one of the most widely used databases in the world.
- **New genres appeared.** *Vector databases* (for AI similarity search), *time-series databases*, and *distributed SQL* systems (such as CockroachDB and Google Spanner, which scale out like NoSQL but speak SQL with transactions).
The book's core lesson, choosing the right tool by understanding trade-offs, matters even more now.
:::

:::key Chapter 1 in a nutshell
- The book's question: **which database, or combination of databases, fits my problem?**
- Ask six questions of any database: its **genre**, its **driving force**, **how you talk to it**, **what makes it unique**, **how it performs**, and **how it scales**.
- Five genres: **relational** (tables and joins), **key-value** (a giant dictionary), **columnar** (sparse rows stored by column family), **document** (nested JSON-like records), **graph** (nodes and relationships).
- **Scale up** means a bigger machine; **scale out** means more machines.
- **Polyglot persistence** means using several databases together, each for what it does best.
:::

@@quiz
Q: What is the central question the book sets out to answer?
- Which database is the fastest in benchmarks?
+ Which database, or combination of databases, best resolves your problem?
- How do you replace SQL with NoSQL?
- How do you become an expert in seven databases in seven weeks?
? The authors say plainly that the book will not make you an expert in any one database. Its goal is that you can pick the right database (or databases) for a given problem, which is why "or combination" matters.

Q: Which genre does each database belong to? Pick the correct pairing.
- Redis: document, HBase: key-value, Neo4J: graph
+ Riak: key-value, HBase: columnar, CouchDB: document
- MongoDB: columnar, PostgreSQL: relational, Riak: graph
- CouchDB: key-value, Redis: columnar, MongoDB: document
? The book's lineup is one relational database (PostgreSQL), two key-value stores (Riak and Redis), one columnar database (HBase), two document databases (MongoDB and CouchDB) and one graph database (Neo4J).

Q: You store user sessions for a website. Each session is read by its session ID, must be returned very quickly, and has nothing to do with other users' sessions. Which genre fits best?
+ Key-value
- Graph
- Relational
- Columnar
? Sessions are looked up by one key, need speed, and are unrelated to each other. That is the textbook case for a key-value store. The book's Wrap-Up chapter uses exactly this example.

Q: Which statement about scaling is correct, according to the book?
- PostgreSQL, Neo4J and Redis are designed mainly for horizontal scaling
+ MongoDB, HBase and Riak are geared toward horizontal scaling; PostgreSQL, Neo4J and Redis toward vertical scaling
- All seven databases scale the same way
- Vertical scaling means adding more machines to a cluster
? Horizontal scaling (scale out) adds machines; vertical scaling (scale up) buys a bigger machine. The book places MongoDB, HBase and Riak in the first group and PostgreSQL, Neo4J and Redis in the second.

Q: What is the main difference between sharding and replication?
- Sharding copies all data to every server; replication splits data between servers
+ Sharding splits data so each server holds a part; replication keeps copies of the same data on several servers
- They are two names for the same thing
- Sharding is only used by relational databases
? Sharding lets a cluster hold more data than one machine could. Replication keeps the data available when a machine dies. Large systems usually do both.

Q: Why can a relational database answer questions you did not plan for when you designed it?
- Because it stores every possible query result in advance
+ Because tables are mathematical sets that can be joined, filtered and combined into new tables at query time
- Because it has no schema
- Because it keeps all data in memory
? Relational databases are built on set theory (relational algebra). Joins let you combine tables in ways you never planned, so you pay the cost of designing a schema up front and get query flexibility later.

Q: In a columnar database such as HBase, what happens when a row has no value for a column?
- The database stores a NULL that takes up space
- The insert fails because every column is required
+ Nothing is stored for that cell, so sparse rows cost no extra storage
- The database fills in a default value
? Columns are added row by row in a columnar store. A row without a value simply has no cell there, so very sparse tables are cheap.

Q: What does "polyglot persistence" mean?
- Storing data in several human languages
- Using one database that supports many query languages
+ Using several different databases together, each for the job it does best
- Translating data between SQL and NoSQL formats
? Like a person who speaks many languages, a polyglot system uses several databases, for example PostgreSQL for orders, Redis for caching and Neo4J for recommendations.

Q: Which question is the graph genre especially good at answering?
- "What is the average order value in March?"
- "Give me the value stored under key `user:42`."
+ "Which friends of my friends also like jazz?"
- "Store 10 terabytes of web pages with version history."
? Graph databases shine at traversals: start at one node and follow relationships. The other questions suit relational, key-value and columnar databases respectively.

Q: According to the book, how does Redis get its amazing speed, and what is the trade-off?
- It compresses all data; the trade-off is slow writes
+ It keeps data in memory before writing to disk; the trade-off is a risk of losing data if the hardware fails
- It uses SQL; the trade-off is a rigid schema
- It shards data across thousands of nodes; the trade-off is high cost
? Redis works in memory and saves to disk later, which makes it extremely fast but means recent writes can be lost in a crash. That makes it a good fit for caches and message brokers, not for critical records.

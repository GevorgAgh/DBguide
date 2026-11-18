title: Wrapping Up
lead: The five genres revisited, what each is good and bad at, how to choose a database (or several), and the book's comparison tables in one place.

## 9.1 Where we ended up

You have now used seven databases. The authors hope you will use at least one of them in a project, and they would be happiest if you used **several together**, as in the Redis chapter's band service. Their view of the future is **polyglot persistence**: using more than one database in a project, while the idea of one general-purpose relational database for everything fades away.

This chapter steps back to see how the seven fit into the wider landscape. It revisits the five genres with a clear "good for / not so good for" for each, discusses how to make a choice, and points to what comes next.

## 9.2 Genres redux

### Relational

Data lives in typed, two-dimensional tables based on set theory. Types are strictly enforced (numbers, strings, dates, blobs), though PostgreSQL showed that extensions can add arrays, cubes and more.

| Good for | Not so good for |
|---|---|
| Data whose **layout is known in advance**, even if how you will use it is not. You pay the cost of organizing up front and get **query flexibility** later. Orders, shipments, inventory, shopping carts: regular data where enforcing that regularity helps, and questions like "how many orders did we ship in February?" come later. | **Highly variable or deeply hierarchical** data. With a schema fixed up front, records that differ a lot from each other are painful. The book's example: a database of every creature in nature. Listing every possible attribute (hasHair, numLegs, laysEggs…) would be hopeless. |

### Key-value

The simplest model: keys mapped to (possibly complex) values, like a huge hashtable. That simplicity gives the most freedom of implementation: Redis used it for raw **speed**, Riak for **easy distribution** across a cluster.

| Good for | Not so good for |
|---|---|
| Data that is **not highly related**, where you need horizontal scale, extreme speed, or both. Few or no indexes to maintain. The classic example: **user session data** in a web app, where each user's session is independent of everyone else's. | Anything beyond basic CRUD. KV stores usually lack indexes and scanning, so they **can't help you query** your data in other ways. |

### Columnar

Shares features with both key-value stores (values are looked up by key) and relational databases (values are groups of columns), but each row can have any set of columns, and data is stored **by column family** rather than by row. Columns are cheap to add, versioning is trivial, and empty cells cost nothing. HBase is the classic implementation.

| Good for | Not so good for |
|---|---|
| **Big data** on clusters of tens to thousands of nodes, built with horizontal scaling as the main goal, often with **compression and versioning** built in. The canonical example: **indexing web pages**, which are mostly text (compressible), somewhat interrelated, and change over time (versioned). | Situations where you can't define **how the data will be queried** in advance. Columnar schemas are designed around query patterns, so fast **ad hoc reporting** is a poor fit. |

### Document

Objects with any number of fields, nested to any depth, usually expressed as **JSON** (as in MongoDB and CouchDB). Documents don't relate to each other the way rows do, which makes them **easy to shard and replicate**. MongoDB aims at availability through huge, managed data centers; CouchDB at simplicity and durability through **master-master replication** of fairly independent nodes.

| Good for | Not so good for |
|---|---|
| **Highly variable domains**, where you don't know in advance exactly what your data will look like. Documents also map naturally to **objects in code**, so there is less "impedance mismatch" between the database model and the application model. | Elaborate **joins** across highly normalized data. A document should contain most of what you need for normal use, so **denormalized data (copies) is normal**, where a relational design would avoid copies that can get out of sync. |

### Graph

Focused on the **free interrelation of data** more than on the values. Instead of grouping similar things into buckets, queries **traverse** relationships between nodes. Social networks first, then recommendation engines, access control lists and geographic data.

| Good for | Not so good for |
|---|---|
| **Networks**: the prototypical social network, where nodes are people with many kinds of relationships. Also a great match for **object-oriented** systems. "If you can model your data on a whiteboard, you can model it in a graph." | **Partitioning across machines.** Fast traversal can't afford network hops between servers, so graph databases **don't scale out well**. Often the graph is one part of a larger system, holding only the relationships while the bulk of the data lives elsewhere. |

:::fig **The five genres side by side.** Each genre makes a different trade between how much structure the database understands, how freely you can query, and how easily data spreads across machines.
<svg class="dg wide" viewBox="0 0 720 300">
<text x="150" y="24" class="s b">ad hoc queries</text><text x="320" y="24" class="s b">schema flexibility</text><text x="490" y="24" class="s b">scales out easily</text>
<g>
<text x="10" y="62" class="b ta">Relational</text>
<rect x="150" y="48" width="140" height="18" rx="4" class="soft"/><rect x="150" y="48" width="140" height="18" rx="4" class="fa"/>
<rect x="320" y="48" width="140" height="18" rx="4" class="soft"/><rect x="320" y="48" width="35" height="18" rx="4" class="fa"/>
<rect x="490" y="48" width="140" height="18" rx="4" class="soft"/><rect x="490" y="48" width="40" height="18" rx="4" class="fa"/>
</g>
<g>
<text x="10" y="112" class="b tw">Key-value</text>
<rect x="150" y="98" width="140" height="18" rx="4" class="soft"/><rect x="150" y="98" width="25" height="18" rx="4" class="fw"/>
<rect x="320" y="98" width="140" height="18" rx="4" class="soft"/><rect x="320" y="98" width="140" height="18" rx="4" class="fw"/>
<rect x="490" y="98" width="140" height="18" rx="4" class="soft"/><rect x="490" y="98" width="130" height="18" rx="4" class="fw"/>
</g>
<g>
<text x="10" y="162" class="b tv">Columnar</text>
<rect x="150" y="148" width="140" height="18" rx="4" class="soft"/><rect x="150" y="148" width="40" height="18" rx="4" class="fv"/>
<rect x="320" y="148" width="140" height="18" rx="4" class="soft"/><rect x="320" y="148" width="95" height="18" rx="4" class="fv"/>
<rect x="490" y="148" width="140" height="18" rx="4" class="soft"/><rect x="490" y="148" width="140" height="18" rx="4" class="fv"/>
</g>
<g>
<text x="10" y="212" class="b tg">Document</text>
<rect x="150" y="198" width="140" height="18" rx="4" class="soft"/><rect x="150" y="198" width="95" height="18" rx="4" class="fg"/>
<rect x="320" y="198" width="140" height="18" rx="4" class="soft"/><rect x="320" y="198" width="130" height="18" rx="4" class="fg"/>
<rect x="490" y="198" width="140" height="18" rx="4" class="soft"/><rect x="490" y="198" width="100" height="18" rx="4" class="fg"/>
</g>
<g>
<text x="10" y="262" class="b tp">Graph</text>
<rect x="150" y="248" width="140" height="18" rx="4" class="soft"/><rect x="150" y="248" width="90" height="18" rx="4" class="fp"/>
<rect x="320" y="248" width="140" height="18" rx="4" class="soft"/><rect x="320" y="248" width="125" height="18" rx="4" class="fp"/>
<rect x="490" y="248" width="140" height="18" rx="4" class="soft"/><rect x="490" y="248" width="25" height="18" rx="4" class="fp"/>
</g>
<text x="360" y="292" text-anchor="middle" class="s">a qualitative summary of the book's 2012 view, not a benchmark</text>
</svg>
:::

## 9.3 Making a choice

The authors open this section with a slogan: **data is the new oil**. There is an ocean of it, but it is useless until refined into information, and refining starts with choosing where to store it.

Choosing is more than matching a genre to the shape of your data:

- **Scale can override shape.** A social graph seems made for a graph database, but if you are Facebook you simply have too much data for one. You would pick a big-data store such as HBase or Riak instead, which forces a columnar or key-value design.
- **Guarantees aren't always where you expect.** A relational database seems obvious for bank transactions, but Neo4J also supports ACID transactions, which widens your options.

As a general rule, **as data size grows, some genres run out of room sooner**. Columnar stores are often built to span data centers and handle the largest datasets; graph databases generally handle the smallest. But it is not absolute: within key-value, Riak is designed to shard across hundreds or thousands of nodes, while Redis was built to run on one machine, with a few replicas or client-managed shards.

:::fig **How far each database scaled out of the box in 2012.** Bars show the typical deployment the book describes, from one server to thousands. Today several of these limits have moved (Redis Cluster, Neo4J clustering, PostgreSQL partitioning), but the relative picture still guides first choices.
<svg class="dg wide" viewBox="0 0 720 300">
<line x1="160" y1="270" x2="700" y2="270" class="ln2"/>
<text x="200" y="290" text-anchor="middle" class="s">1 server</text><text x="360" y="290" text-anchor="middle" class="s">a few</text><text x="520" y="290" text-anchor="middle" class="s">dozens</text><text x="700" y="290" text-anchor="end" class="s">hundreds–thousands</text>
<text x="10" y="34" class="b">Neo4J</text><rect x="160" y="20" width="110" height="20" rx="4" class="fp"/><text x="280" y="35" class="s">one graph, HA copies</text>
<text x="10" y="70" class="b">Redis</text><rect x="160" y="56" width="140" height="20" rx="4" class="fw"/><text x="310" y="71" class="s">fits in RAM; client shards</text>
<text x="10" y="106" class="b">PostgreSQL</text><rect x="160" y="92" width="160" height="20" rx="4" class="fa"/><text x="330" y="107" class="s">one big machine + replicas</text>
<text x="10" y="142" class="b">CouchDB</text><rect x="160" y="128" width="260" height="20" rx="4" class="fg"/><text x="430" y="143" class="s">full replicas; BigCouch shards</text>
<text x="10" y="178" class="b">MongoDB</text><rect x="160" y="164" width="400" height="20" rx="4" class="fg"/><text x="570" y="179" class="s">sharded clusters</text>
<text x="10" y="214" class="b">Riak</text><rect x="160" y="200" width="520" height="20" rx="4" class="fw"/>
<text x="10" y="250" class="b">HBase</text><rect x="160" y="236" width="540" height="20" rx="4" class="fv"/>
</svg>
:::

### Dimensions to weigh

Beyond genre and size, the authors list more questions to ask:

| Dimension | Question |
|---|---|
| **Durability** | How bad is it to lose the last second (or minute) of writes? |
| **Availability** | Must the system answer even while machines or networks fail? |
| **Consistency** | Must every read see the latest write? (See the CAP appendix.) |
| **Scalability** | Up (one bigger machine) or out (many machines)? |
| **Security** | Users, groups, permissions, network exposure? |
| **Querying** | Do you need **ad hoc** queries, or will **mapreduce** or precomputed views do? |
| **Interface** | Is HTTP/REST important, or is a driver for a custom binary protocol fine? |
| **Operations** | Bulk loaders, backups, monitoring, how many machines to run. |

:::fig **A first-pass decision guide, built from the book's "good for" lists.** Real decisions weigh several dimensions at once and often end with more than one database, but these questions point to the right starting genre.
<svg class="dg wide" viewBox="0 0 720 400">
<rect x="250" y="10" width="220" height="44" rx="10" class="box"/><text x="360" y="37" text-anchor="middle" class="b">What is your data like?</text>
<line x1="270" y1="56" x2="110" y2="96" class="ln" marker-end="url(#arr)"/><line x1="320" y1="56" x2="290" y2="96" class="ln" marker-end="url(#arr)"/>
<line x1="400" y1="56" x2="440" y2="96" class="ln" marker-end="url(#arr)"/><line x1="450" y1="56" x2="610" y2="96" class="ln" marker-end="url(#arr)"/>
<rect x="10" y="100" width="190" height="64" rx="8" class="box"/><text x="105" y="124" text-anchor="middle" class="s">regular, well known;</text><text x="105" y="142" text-anchor="middle" class="s">questions unknown</text><text x="105" y="158" text-anchor="middle" class="s">(and strong guarantees)</text>
<rect x="210" y="100" width="160" height="64" rx="8" class="box"/><text x="290" y="124" text-anchor="middle" class="s">varied, nested,</text><text x="290" y="142" text-anchor="middle" class="s">changing shape</text>
<rect x="380" y="100" width="150" height="64" rx="8" class="box"/><text x="455" y="124" text-anchor="middle" class="s">mostly about</text><text x="455" y="142" text-anchor="middle" class="s">connections</text>
<rect x="540" y="100" width="170" height="64" rx="8" class="box"/><text x="625" y="124" text-anchor="middle" class="s">simple values</text><text x="625" y="142" text-anchor="middle" class="s">looked up by key</text>
<line x1="105" y1="166" x2="105" y2="296" class="ln" marker-end="url(#arr)"/>
<line x1="290" y1="166" x2="290" y2="196" class="ln" marker-end="url(#arr)"/>
<line x1="455" y1="166" x2="455" y2="296" class="ln" marker-end="url(#arr)"/>
<line x1="625" y1="166" x2="625" y2="196" class="ln" marker-end="url(#arr)"/>
<rect x="210" y="200" width="160" height="56" rx="8" class="box"/><text x="290" y="222" text-anchor="middle" class="s">must it sync with offline</text><text x="290" y="240" text-anchor="middle" class="s">or flaky devices?</text>
<rect x="540" y="200" width="170" height="56" rx="8" class="box"/><text x="625" y="222" text-anchor="middle" class="s">huge and must never</text><text x="625" y="240" text-anchor="middle" class="s">go down? or just fast?</text>
<line x1="250" y1="258" x2="230" y2="296" class="ln" marker-end="url(#arr)"/><line x1="330" y1="258" x2="350" y2="296" class="ln" marker-end="url(#arr)"/>
<text x="216" y="282" class="s">yes</text><text x="348" y="282" class="s">no</text>
<line x1="580" y1="258" x2="560" y2="296" class="ln" marker-end="url(#arr)"/><line x1="670" y1="258" x2="680" y2="296" class="ln" marker-end="url(#arr)"/>
<text x="530" y="282" class="s">huge</text><text x="684" y="282" class="s">fast</text>
<rect x="30" y="300" width="150" height="56" rx="8" class="ba"/><text x="105" y="324" text-anchor="middle" class="b">Relational</text><text x="105" y="342" text-anchor="middle" class="s">PostgreSQL</text>
<rect x="180" y="300" width="100" height="56" rx="8" class="bg"/><text x="230" y="324" text-anchor="middle" class="b">Document</text><text x="230" y="342" text-anchor="middle" class="s">CouchDB</text>
<rect x="290" y="300" width="100" height="56" rx="8" class="bg"/><text x="340" y="324" text-anchor="middle" class="b">Document</text><text x="340" y="342" text-anchor="middle" class="s">MongoDB</text>
<rect x="400" y="300" width="110" height="56" rx="8" class="bp"/><text x="455" y="324" text-anchor="middle" class="b">Graph</text><text x="455" y="342" text-anchor="middle" class="s">Neo4J</text>
<rect x="520" y="300" width="90" height="56" rx="8" class="bw"/><text x="565" y="324" text-anchor="middle" class="b">KV</text><text x="565" y="342" text-anchor="middle" class="s">Riak</text>
<rect x="620" y="300" width="90" height="56" rx="8" class="bw"/><text x="665" y="324" text-anchor="middle" class="b">KV</text><text x="665" y="342" text-anchor="middle" class="s">Redis</text>
<rect x="120" y="368" width="480" height="28" rx="8" class="bv"/><text x="360" y="387" text-anchor="middle" class="s">enormous, append-mostly, versioned data (web pages, logs)? → <tspan class="b">Columnar: HBase</tspan></text>
</svg>
:::

## 9.4 The comparison tables (Appendix 1)

The book's first appendix collects the seven databases in a set of tables. They reflect the **2012 versions** (MongoDB 2.0, CouchDB 1.1, Riak 1.0, Redis 2.4, PostgreSQL 9.1, Neo4J 1.7, HBase 0.90.3), and the authors warn that such details change quickly. Here they are, regrouped for easier reading.

### Data model and interface

| | Genre | Datatypes | Relations | Standard object | Written in | Protocol | HTTP/REST |
|---|---|---|---|---|---|---|---|
| **MongoDB** | Document | Typed | None | JSON | C++ | Custom over TCP | Simple |
| **CouchDB** | Document | Typed | None | JSON | Erlang | HTTP | Yes |
| **Riak** | Key-value | Blob | Ad hoc (links) | Text | Erlang | HTTP, protobuf | Yes |
| **Redis** | Key-value | Semi-typed | None | String | C/C++ | Simple text over TCP | No |
| **PostgreSQL** | Relational | Predefined and typed | Predefined | Table | C | Custom over TCP | No |
| **Neo4J** | Graph | Untyped | Ad hoc (edges) | Hash | Java | HTTP | Yes |
| **HBase** | Columnar | Predefined and typed | None | Columns | Java | Thrift, HTTP | Yes |

### Querying, scaling and durability

| | Ad hoc query | Mapreduce | Scalable | Durability |
|---|---|---|---|---|
| **MongoDB** | Commands, mapreduce | JavaScript | Datacenter | Write-ahead journaling, safe mode |
| **CouchDB** | Temporary views | JavaScript | Datacenter (via BigCouch) | Crash-only |
| **Riak** | Weak support, Lucene | JavaScript, Erlang | Datacenter | Durable write quorum |
| **Redis** | Commands | No | Cluster (via master-slave) | Append-only log |
| **PostgreSQL** | SQL | No | Cluster (via add-ons) | ACID |
| **Neo4J** | Graph walking, Cypher, search | No (in the distributed sense) | Cluster (via HA) | ACID |
| **HBase** | Weak | Hadoop | Datacenter | Write-ahead logging |

### Features

| | Secondary indexes | Versioning | Bulk load | Very large files | Requires compaction |
|---|---|---|---|---|---|
| **MongoDB** | Yes | No | mongoimport | GridFS | No |
| **CouchDB** | Yes | Yes | Bulk Doc API | Attachments | File rewrite |
| **Riak** | Yes | Yes | No | Lewak (deprecated) | No |
| **Redis** | No | No | No | No | Snapshot |
| **PostgreSQL** | Yes | No | COPY command | BLOBs | No |
| **Neo4J** | Yes (via Lucene) | No | No | No | No |
| **HBase** | No | Yes | No | No | No |

### Distribution, transactions and security

| | Replication | Sharding | Concurrency | Transactions | Triggers | Security | Multitenancy |
|---|---|---|---|---|---|---|---|
| **MongoDB** | Master-slave (replica sets) | Yes | Write lock | No | No | Users | Yes |
| **CouchDB** | Master-master | Yes (filters, BigCouch) | Lock-free MVCC | No | Update validation, Changes API | Users | Yes |
| **Riak** | Peer-based, master-master | Yes | Vector clocks | No | Pre/post-commits | None | No |
| **Redis** | Master-slave | Add-ons (client) | None | Multi-operation queues | No | Passwords | No |
| **PostgreSQL** | Master-slave | Add-ons (PL/Proxy) | Table/row writer lock | ACID | Yes | Users/groups | Yes |
| **Neo4J** | Master-slave (Enterprise) | No | Write lock | ACID | Transaction event handlers | None | No |
| **HBase** | Master-slave | Yes via HDFS | Consistent per row | Yes (when enabled) | No | Kerberos via Hadoop | No |

### In one line each

| | Main differentiator | Weakness |
|---|---|---|
| **MongoDB** | Easily query big data | Embeddability |
| **CouchDB** | Durable and embeddable clusters | Queryability |
| **Riak** | Highly available | Queryability |
| **Redis** | Very, very fast | Complex data |
| **PostgreSQL** | Best of open-source RDBMS model | Distributed availability |
| **Neo4J** | Flexible graph | Blobs or terabyte scale |
| **HBase** | Very large scale, Hadoop infrastructure | Flexible growth, queryability |

:::modern The 2012 tables in 2026
Several cells are now out of date. The biggest changes:
- **MongoDB:** multi-document ACID transactions, document-level concurrency (WiredTiger), joins with `$lookup`, the aggregation pipeline instead of mapreduce.
- **CouchDB:** built-in sharding and clustering (2.0), Mango queries.
- **Riak:** maintained by a small community after Basho closed; JavaScript mapreduce and links deprecated, CRDT data types added.
- **Redis:** Redis Cluster for sharding, Sentinel for failover, ACLs and TLS for security, Streams for messaging.
- **PostgreSQL:** native partitioning, logical replication, `jsonb`, and sharding through extensions such as Citus.
- **Neo4J:** clustering with Raft, schema indexes and constraints, Cypher and the GQL standard; Gremlin and the old REST API removed.
- **HBase:** still the Hadoop-ecosystem wide-column store, with Phoenix for SQL; many teams use Cassandra, ScyllaDB or Cloud Bigtable for this genre.
:::

## 9.5 Where do we go from here?

The authors argue that most application scaling problems are now **data management** problems. Programming languages, frameworks, operating systems, and even hardware (thanks to virtual machines and the cloud) have become cheap and easy enough that choosing them is largely a matter of taste. The **database is most likely your real bottleneck**, so choosing it, or them, deserves real thought. Helping you make that choice was the book's main purpose.

Their suggested next steps: study in depth the databases that caught your interest, and explore others, such as **Cassandra**, **Drizzle** or **OrientDB**. Then get your hands dirty.

:::modern Where to go in 2026
Of the book's suggestions, **Cassandra** became a major database (and a good next step after Riak and HBase, since it combines Dynamo-style distribution with a column-family model). Drizzle, a MySQL fork, was abandoned. New genres worth knowing about now:
- **Distributed SQL** ("NewSQL"): CockroachDB, YugabyteDB, Google Spanner, TiDB. SQL and ACID transactions with horizontal scaling.
- **Cloud-native managed stores:** Amazon DynamoDB, Google Firestore and Bigtable, Azure Cosmos DB.
- **Analytics and columnar warehouses:** ClickHouse, DuckDB, Snowflake, BigQuery (column storage for analytical queries, a different use of "columnar" than HBase's).
- **Search engines:** Elasticsearch and OpenSearch.
- **Time-series databases:** TimescaleDB (a PostgreSQL extension), InfluxDB.
- **Vector databases** for AI similarity search: pgvector, Pinecone, Milvus, Weaviate, Qdrant, plus vector search in most databases above.
A natural sequel is the second edition of this book, *Seven Databases in Seven Weeks* (2018), which replaces Riak with Amazon DynamoDB and teaches Neo4J with Cypher instead of Gremlin, along with *Designing Data-Intensive Applications* by Martin Kleppmann for the theory behind all of them.
:::

:::key Chapter 9 in a nutshell
- **Relational:** known structure, unknown questions. **Key-value:** unrelated data, speed or scale. **Columnar:** big data with known query patterns. **Document:** variable, nested data that maps to objects. **Graph:** relationships first, but hard to scale out.
- Choosing involves **size**, **durability**, **availability**, **consistency**, **scalability**, **security**, **query style** and **interface**, not only data shape.
- Expect to use **several databases together** (polyglot persistence), with one system of record.
- The database is most likely your application's real bottleneck, so the choice deserves care.
:::

@@quiz
Q: According to the book, when is a relational database a good fit?
- When every record looks different from every other record
+ When the layout of the data is known in advance, but how you will query it later is not
- When you need to scale across thousands of servers
- When data is deeply hierarchical and changes shape often
? You pay the cost of designing a schema up front in exchange for query flexibility later. Highly variable data is the relational model's weak spot.

Q: Which use case does the book give as ideal for key-value stores?
- Indexing web pages with version history
+ Storing web session data, where each user's session is unrelated to others
- Modeling a social network
- Ad hoc business reporting
? Session data is looked up by key, needs speed and scale, and has no relationships between users, which suits key-value stores.

Q: What is the canonical example of a good columnar data problem?
- A shopping cart
- A family tree
+ Indexing web pages: mostly text, somewhat interrelated, and changing over time
- A leaderboard
? Web pages benefit from compression (text) and versioning (they change), and the data is huge, which plays to HBase's strengths.

Q: What is a weakness common to columnar databases?
- They cannot store text
+ You should design the schema around how the data will be queried, so fast ad hoc reporting is a poor fit
- They cannot be distributed
- They require a fixed list of columns per table
? Columnar schemas (row keys, families) are shaped by expected access patterns. Unplanned queries usually mean full scans.

Q: In a document database, why is denormalized (duplicated) data considered normal?
+ A document should contain most of what is needed for normal use, because there are no efficient joins to reassemble it
- Because document databases cannot store references
- Because duplication makes writes faster in every case
- Because JSON requires it
? Without joins, related data is embedded where it is read. The cost is keeping copies in sync, which relational normalization avoids.

Q: Why do graph databases generally not scale out well?
- They store data in a single file
+ Fast traversals can't afford network hops between servers, so splitting a highly connected graph across machines hurts performance
- They don't support replication
- They only run on Java
? Following relationships is fast in memory on one machine. If neighbors live on other servers, every hop becomes a network call.

Q: The book says that if you are Facebook, you would likely not store your social graph in a graph database. Why?
- Graph databases cannot model friendships
+ The sheer amount of data pushes you toward a big-data store like HBase or Riak
- Facebook uses only relational databases
- Graph databases lack transactions
? Scale can override data shape. Too much data for one graph database means choosing a distributed columnar or key-value store.

Q: According to the book's tables, which database's main differentiator is "very, very fast" and whose weakness is "complex data"?
- PostgreSQL
- Neo4J
+ Redis
- HBase
? Redis is extremely fast because it works in memory, but it is not designed for complex, deeply related data.

Q: What do the authors identify as most likely the real bottleneck when scaling a modern application?
- The programming language
- The web framework
- The operating system
+ The database (or databases) you choose
? Languages, frameworks, operating systems and even hardware have become cheap and easy; data management is where scaling problems now live.

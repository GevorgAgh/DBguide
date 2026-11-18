title: The CAP Theorem
lead: Why a distributed database must choose between consistency and availability when the network fails, what eventual consistency means, and where each of the seven databases stands.

## A2.1 The theorem in plain words

Choosing a genre is one part of choosing a database. The other recurring theme of the book is the **CAP theorem**, which states an uncomfortable truth about every database that runs on more than one machine.

It concerns three properties:

| Letter | Property | Meaning |
|---|---|---|
| **C** | **Consistency** | Writes are atomic, and every request after a write sees the new value. All nodes agree on the current data. |
| **A** | **Availability** | The database always returns a value, as long as at least one server is running. |
| **P** | **Partition tolerance** | The system keeps working even if servers temporarily can't talk to each other (a **network partition**). |

The theorem (proposed by Eric Brewer in 2000 and proved by Seth Gilbert and Nancy Lynch in 2002) says you can build a distributed database that has **any two** of these, but **never all three at once**:

- **CP**: consistent and partition-tolerant. During a partition, some requests are refused.
- **AP**: available and partition-tolerant. During a partition, some answers may be out of date.
- **CA**: consistent and available, but not partition-tolerant, which in practice means **not distributed**.

:::fig **The CAP triangle with the book's seven databases**, placed by their default or common behavior as the authors describe it. Riak sits on the AP–CP edge because you tune it per request. Most of these can be configured to move elsewhere.
<svg class="dg wide" viewBox="0 0 720 380">
<polygon points="360,30 90,340 630,340" class="box" style="stroke-width:2px"/>
<circle cx="360" cy="30" r="22" class="ba"/><text x="360" y="35" text-anchor="middle" class="b">C</text>
<circle cx="90" cy="340" r="22" class="bg"/><text x="90" y="345" text-anchor="middle" class="b">A</text>
<circle cx="630" cy="340" r="22" class="bw"/><text x="630" y="345" text-anchor="middle" class="b">P</text>
<text x="400" y="34" class="s">Consistency</text><text x="40" y="374" class="s">Availability</text><text x="580" y="374" class="s">Partition tolerance</text>
<rect x="110" y="140" width="150" height="70" rx="8" class="ba"/>
<text x="185" y="132" text-anchor="middle" class="b ta">CA</text>
<text x="185" y="162" text-anchor="middle" class="s">PostgreSQL</text><text x="185" y="180" text-anchor="middle" class="s">Redis · Neo4J</text><text x="185" y="198" text-anchor="middle" class="s">(single server)</text>
<rect x="460" y="140" width="150" height="56" rx="8" class="bv"/>
<text x="535" y="132" text-anchor="middle" class="b tv">CP</text>
<text x="535" y="162" text-anchor="middle" class="s">MongoDB</text><text x="535" y="180" text-anchor="middle" class="s">HBase</text>
<rect x="285" y="270" width="150" height="56" rx="8" class="bg"/>
<text x="360" y="262" text-anchor="middle" class="b tg">AP</text>
<text x="360" y="292" text-anchor="middle" class="s">CouchDB</text><text x="360" y="310" text-anchor="middle" class="s">Neo4J HA</text>
<rect x="470" y="230" width="140" height="44" rx="8" class="bw"/><text x="540" y="250" text-anchor="middle" class="s b">Riak</text><text x="540" y="266" text-anchor="middle" class="s">tunable: AP ↔ CP</text>
</svg>
:::

:::warn P is not really optional
If your database runs on more than one machine, networks **will** fail sometimes: a cable is unplugged, a switch reboots, a data center loses its link. You can't decide that partitions won't happen. So for a distributed database the real choice is: **when a partition happens, give up consistency (AP) or give up availability (CP)?** "CA" only describes systems that aren't distributed, which is why the book adds that CAP makes little sense for them.
:::

### The story of the desert island

The book explains CAP with a memorable story (summarized here). Imagine the whole world is one giant distributed database: wherever there are people and technology, you can get an answer to a question.

You are a big fan of a pop singer. In 2006, at a party celebrating her second album, a freak wave sweeps you out to sea, and you wash up on a desert island. You have no way to communicate: you are **partitioned** from the rest of the system. Five years pass.

In 2011, a ship's captain finds you and shouts: **"How many studio albums does she have?"** You have two choices:

- **Answer** with what you know ("two"), which is five years old. You are **available**, but your answer may be **inconsistent** with the rest of the world.
- **Refuse** to answer, because you know you have been cut off and might be wrong. The world's knowledge stays **consistent** (the captain can sail home and find the right answer), but you are **not available**.

As a partitioned node, you can help keep the world's data consistent, or be available, but not both.

:::fig **The island as a partitioned node.** Cut off from the rest of the system, a node asked for data must choose: answer with what it has (available, maybe stale) or refuse (consistent, but unavailable).
<svg class="dg wide" viewBox="0 0 720 260">
<rect x="10" y="30" width="260" height="190" rx="14" class="ba" fill-opacity="0.5"/>
<text x="140" y="56" text-anchor="middle" class="b">the rest of the world</text>
<text x="140" y="86" text-anchor="middle" class="s">knows the latest value:</text><text x="140" y="104" text-anchor="middle" class="s b">albums = 4</text>
<circle cx="80" cy="160" r="18" class="ba"/><circle cx="140" cy="150" r="18" class="ba"/><circle cx="200" cy="170" r="18" class="ba"/>
<line x1="98" y1="158" x2="122" y2="152" class="ln2"/><line x1="158" y1="154" x2="182" y2="166" class="ln2"/>
<line x1="290" y1="40" x2="290" y2="220" class="lr dash" style="stroke-width:3px"/>
<text x="300" y="130" class="s tr b">partition</text>
<ellipse cx="420" cy="140" rx="70" ry="44" class="bw"/><text x="420" y="136" text-anchor="middle" class="b">island node</text><text x="420" y="154" text-anchor="middle" class="s">albums = 2 (old)</text>
<text x="420" y="60" text-anchor="middle" class="s">"How many albums?"</text>
<line x1="420" y1="66" x2="420" y2="92" class="ln" marker-end="url(#arr)"/>
<line x1="492" y1="124" x2="560" y2="84" class="lgr" marker-end="url(#arrg)"/><line x1="492" y1="156" x2="560" y2="196" class="lv" marker-end="url(#arrv)"/>
<rect x="564" y="56" width="146" height="56" rx="8" class="bg"/><text x="637" y="78" text-anchor="middle" class="b">answer "2"</text><text x="637" y="96" text-anchor="middle" class="s">available, stale</text>
<rect x="564" y="170" width="146" height="56" rx="8" class="bv"/><text x="637" y="192" text-anchor="middle" class="b">refuse</text><text x="637" y="210" text-anchor="middle" class="s">consistent, unavailable</text>
<text x="637" y="132" text-anchor="middle" class="s tg b">AP</text><text x="637" y="160" text-anchor="middle" class="s tv b">CP</text>
</svg>
:::

## A2.2 Eventual consistency

Because distributed databases must tolerate partitions, many choose **availability**. CAP says they then can't have perfect consistency, but they can have **eventual consistency**:

- Every node is always available to answer requests.
- Changes spread to the other nodes **in the background**.
- At any moment some nodes may be out of date, but if writes stop, all nodes **eventually** converge to the same value.

The internet's **Domain Name System (DNS)** is the classic example. When you register a domain or change its address, the change can take hours or days to reach every DNS server in the world. Yet at no point is a DNS server unavailable: each one answers with the best information it has.

The island story continues: in 2009, three years into your exile, a **bottle** washes ashore. Whenever the singer releases an album, someone writes the date and the album count on paper, seals it in a bottle and throws it into the sea, so that people cut off from the world eventually learn the truth. Your bottle says "three albums". When the captain asks in 2011, you answer "three": you are **available**, and your answer is reasonably current but not guaranteed to be the latest (she released a fourth in 2011). The bottles are the background propagation of eventual consistency. And once you are rescued and back on land, you no longer need partition tolerance: you can be consistent and available again.

:::fig **Eventual consistency over time.** A write lands on node 1. Nodes 2 and 3 keep answering during propagation, briefly with the old value, until the change reaches them. If no new writes arrive, all nodes converge.
<svg class="dg wide" viewBox="0 0 720 220">
<text x="10" y="54" class="b">node 1</text><text x="10" y="114" class="b">node 2</text><text x="10" y="174" class="b">node 3</text>
<line x1="90" y1="50" x2="700" y2="50" class="ln2"/><line x1="90" y1="110" x2="700" y2="110" class="ln2"/><line x1="90" y1="170" x2="700" y2="170" class="ln2"/>
<rect x="100" y="40" width="120" height="20" rx="4" class="box"/><text x="160" y="55" text-anchor="middle" class="mono s">v1</text>
<rect x="220" y="40" width="480" height="20" rx="4" class="bg"/><text x="460" y="55" text-anchor="middle" class="mono s">v2</text>
<rect x="100" y="100" width="300" height="20" rx="4" class="box"/><text x="250" y="115" text-anchor="middle" class="mono s">v1 (still answering)</text>
<rect x="400" y="100" width="300" height="20" rx="4" class="bg"/><text x="550" y="115" text-anchor="middle" class="mono s">v2</text>
<rect x="100" y="160" width="420" height="20" rx="4" class="box"/><text x="310" y="175" text-anchor="middle" class="mono s">v1 (still answering)</text>
<rect x="520" y="160" width="180" height="20" rx="4" class="bg"/><text x="610" y="175" text-anchor="middle" class="mono s">v2</text>
<line x1="220" y1="20" x2="220" y2="38" class="ln" marker-end="url(#arr)"/><text x="220" y="16" text-anchor="middle" class="s b">write v2</text>
<line x1="400" y1="62" x2="400" y2="96" class="ln dash" marker-end="url(#arr)"/><line x1="520" y1="62" x2="520" y2="156" class="ln dash" marker-end="url(#arr)"/>
<text x="610" y="206" text-anchor="middle" class="s tg b">converged</text>
<text x="300" y="206" text-anchor="middle" class="s">inconsistency window</text>
</svg>
:::

## A2.3 CAP in the wild

Some partition-tolerant databases let you tune the trade-off **per request**. Riak is the book's example: with N, R and W you decide, request by request, how consistent you need to be (see the Riak chapter). The others mostly sit in one corner by default:

| Database | CAP (default) | Why |
|---|---|---|
| **PostgreSQL** | CA | A single server: nothing to partition. (Arguably CAP doesn't apply.) |
| **Redis** | CA | Single server by default. |
| **Neo4J** | CA (single) / AP (HA) | Single server: CA. The HA cluster serves possibly lagging reads from slaves: AP. |
| **MongoDB** | CP | A replica set refuses some operations during a partition (for example, writes without a reachable primary, or reads when secondaries aren't allowed: `slaveOk` false). |
| **HBase** | CP | Strongly consistent; refuses requests rather than serve stale data if too few nodes remain. |
| **CouchDB** | AP | Every copy accepts reads and writes; replicas can disagree until they sync. |
| **Riak** | AP or CP, per request | Tune N, R, W: low R/W favors availability, R + W > N favors consistency. |

The book notes that in practice, CP systems handle ordinary hardware failures gracefully (other nodes take over), so they **seem** available most of the time. Strictly in the CAP sense, though, they are unavailable for some requests during a partition. And most of these databases can be configured into a different corner (MongoDB can behave as CA, CouchDB as CP).

## A2.4 The latency trade-off

CAP is not the whole story. Many architects care just as much about **latency** (speed). Amazon's Dynamo paper talks about availability, but also about strict latency requirements, because for some applications a small delay costs a lot of money. Yahoo's **PNUTS** database famously gives up availability during normal operation and consistency during partitions to achieve **lower latency**.

The authors' conclusion: understand CAP when you work with distributed databases, but know that distributed systems theory doesn't stop there.

:::deep PACELC: CAP plus latency
In 2010, Daniel Abadi (whose blog post the book cites for the PNUTS example) proposed extending CAP into **PACELC**: *if there is a **P**artition, choose **A**vailability or **C**onsistency; **E**lse (normal operation), choose **L**atency or **C**onsistency.* The "else" half matters because partitions are rare, while the latency cost of consistency (waiting for replicas to agree) is paid on every request.

| System | During a partition | Normal operation |
|---|---|---|
| Dynamo, Riak, Cassandra (default) | PA: stay available | EL: favor low latency |
| HBase, traditional relational clusters | PC: stay consistent | EC: favor consistency |
| PNUTS | PC | EL |
:::

:::fig **PACELC as a decision tree.** CAP only describes what happens during a partition. The rest of the time, a distributed database still trades latency against consistency, because waiting for replicas to agree takes time.
<svg class="dg" viewBox="0 0 720 220">
<rect x="270" y="10" width="180" height="44" rx="10" class="box"/><text x="360" y="37" text-anchor="middle" class="b">network partition?</text>
<line x1="320" y1="56" x2="180" y2="96" class="ln" marker-end="url(#arr)"/><line x1="400" y1="56" x2="540" y2="96" class="ln" marker-end="url(#arr)"/>
<text x="232" y="66" text-anchor="end" class="s b">yes (P)</text><text x="474" y="66" class="s b">no (Else)</text>
<rect x="90" y="100" width="180" height="44" rx="10" class="box"/><text x="180" y="127" text-anchor="middle" class="s">choose</text>
<rect x="450" y="100" width="180" height="44" rx="10" class="box"/><text x="540" y="127" text-anchor="middle" class="s">choose</text>
<line x1="150" y1="146" x2="100" y2="176" class="ln" marker-end="url(#arr)"/><line x1="210" y1="146" x2="260" y2="176" class="ln" marker-end="url(#arr)"/>
<line x1="510" y1="146" x2="460" y2="176" class="ln" marker-end="url(#arr)"/><line x1="570" y1="146" x2="620" y2="176" class="ln" marker-end="url(#arr)"/>
<rect x="30" y="180" width="130" height="34" rx="8" class="bg"/><text x="95" y="202" text-anchor="middle" class="s b">Availability</text>
<rect x="200" y="180" width="130" height="34" rx="8" class="ba"/><text x="265" y="202" text-anchor="middle" class="s b">Consistency</text>
<rect x="390" y="180" width="130" height="34" rx="8" class="bw"/><text x="455" y="202" text-anchor="middle" class="s b">Latency</text>
<rect x="560" y="180" width="130" height="34" rx="8" class="ba"/><text x="625" y="202" text-anchor="middle" class="s b">Consistency</text>
</svg>
:::

:::modern CAP in 2026
- **"Two out of three" is now considered too simple.** In 2012, Eric Brewer himself wrote *CAP Twelve Years Later*, explaining that the choice only applies **during** a partition, that systems can make different choices for different operations, and that the real design work is detecting partitions and recovering afterwards.
- **Consistency is a spectrum**, not a yes/no: linearizable (strongest), sequential, causal, read-your-writes, eventual. Many modern databases let you pick per request, like Riak did: Cassandra's consistency levels (ONE, QUORUM, ALL), DynamoDB's eventually or strongly consistent reads, MongoDB's read and write concerns.
- **Distributed SQL databases** such as Google Spanner and CockroachDB are CP systems built with consensus algorithms (Paxos or Raft). They are so carefully engineered that, in practice, unavailability is very rare, which led Brewer to describe Spanner as "effectively CA" in normal conditions. They still pay the PACELC cost: consistent writes wait for a majority of replicas, so they are slower than eventually consistent writes.
- **CRDTs** (Conflict-free Replicated Data Types), which arrived in Riak 2.0 and power many collaborative apps, let AP systems merge concurrent updates automatically, softening the pain of choosing availability.
:::

:::key The CAP appendix in a nutshell
- **C**onsistency, **A**vailability, **P**artition tolerance: a distributed database can't guarantee all three at once.
- Distributed systems must tolerate partitions, so the real choice during a partition is **consistency (CP)** or **availability (AP)**.
- **Eventual consistency** keeps every node available and lets changes spread in the background; DNS is the classic example.
- Book placements: **CA** PostgreSQL, Redis, single Neo4J; **CP** MongoDB, HBase; **AP** CouchDB, Neo4J HA; **tunable** Riak.
- **Latency** is another trade-off (PACELC): even without partitions, stronger consistency costs time.
:::

@@quiz
Q: What does the C in CAP mean?
- Constraints are never violated, as in ACID
+ After a write succeeds, every subsequent request sees the new value (all nodes agree)
- The database is cheap to run
- Data is compressed
? CAP consistency is about all nodes returning the latest value. It is different from the C in ACID, which means the database's rules are never broken.

Q: Which statement best describes the CAP theorem?
- Every database must choose one of the three properties
+ A distributed database cannot guarantee consistency, availability and partition tolerance all at the same time
- Partition tolerance is always optional
- Availability and consistency can always be combined if you buy enough servers
? You can have at most two of the three at once. Because real networks do partition, distributed systems effectively choose between C and A when a partition happens.

Q: In the desert island story, what does answering the captain with your five-year-old information represent?
+ Choosing availability over consistency (AP)
- Choosing consistency over availability (CP)
- Being consistent and available (CA)
- Recovering from the partition
? You respond (available), but your answer may disagree with the rest of the world (inconsistent).

Q: Why do the authors say CA "basically means not distributed"?
- CA databases cannot store data
+ If a system must be both consistent and available, it cannot tolerate network partitions, and any multi-machine system will eventually face one
- CA is only possible with graph databases
- CA systems always use HTTP
? Partitions happen whenever data spans a network. Only a single-server system can avoid them, which is why PostgreSQL, Redis and single Neo4J are labeled CA.

Q: What is eventual consistency?
- Every read always returns the latest write
+ Nodes stay available and changes spread in the background, so nodes may briefly disagree but converge if writes stop
- Data is written to disk eventually, never immediately
- The database becomes consistent only after a restart
? Eventual consistency is the AP compromise: always answer, propagate changes asynchronously, converge over time.

Q: Which real system does the book use as the classic example of eventual consistency?
- A bank's ledger
+ The Domain Name System (DNS)
- PostgreSQL replication
- A spreadsheet
? A DNS change takes time to reach every server, yet each server keeps answering with the best data it has.

Q: Where does the book place HBase and MongoDB by default?
- AP
+ CP
- CA
- Tunable per request
? Both favor consistency. During a severe partition they refuse some requests rather than return possibly stale data.

Q: Which database lets you choose your CAP trade-off per request, with N, R and W?
- HBase
- PostgreSQL
+ Riak
- Neo4J
? Riak, following the Dynamo paper, lets each request decide how many replicas must respond, trading consistency against availability.

Q: What does the latency trade-off (and PACELC) add to CAP?
- Partitions don't matter if latency is low
+ Even when there is no partition, stronger consistency costs time, so systems also trade latency against consistency in normal operation
- Latency only matters for single-server databases
- It replaces availability with speed
? CAP describes behavior during partitions. Waiting for replicas to agree slows every request, so databases also choose between latency and consistency the rest of the time.

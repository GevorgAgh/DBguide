title: Neo4J
lead: A graph database: if you can draw it on a whiteboard, you can store it. Nodes, relationships, Gremlin and Cypher on Day 1; REST, indexes and graph algorithms on Day 2; transactions, high availability and backups on Day 3.

## Overview: Neo4J is whiteboard friendly

Every other database in the book groups similar things together: rows in tables, documents in collections, values in buckets. A **graph database** cares most about how things are **connected**. Its data model has only two building blocks:

- **Nodes** (the book also says *vertices*): the things. A person, a wine, a magazine.
- **Relationships** (also called *edges*): directed, named connections between two nodes, like `LIKES`, `PRODUCED`, `FRIENDS`.

Both nodes and relationships can carry **properties**: key-value pairs such as `name: "Alice"` or `weight: 95`. This is called the **property graph** model.

The authors' motto for Neo4J is **"whiteboard friendly"**: the diagram you sketch on a whiteboard while discussing a problem *is* the data model. There is no translation into tables.

:::fig **The book's wine graph, as you would draw it on a whiteboard.** A winery produced wines, each wine has a grape type, a magazine reported on a wine, and people like wines, trust the magazine and are friends with each other. Every arrow is a stored relationship with a name: black arrows are `produced`, purple `grape_type`, dashed `reported_on`, green `likes` and `trusts`, pink `friends`.
<svg class="dg wide" viewBox="0 0 720 344">
<circle cx="110" cy="70" r="46" class="bw"/><text x="110" y="66" text-anchor="middle" class="b">Prancing</text><text x="110" y="82" text-anchor="middle" class="b">Wolf Winery</text>
<circle cx="330" cy="50" r="40" class="bp"/><text x="330" y="46" text-anchor="middle" class="s b">Ice Wine</text><text x="330" y="62" text-anchor="middle" class="s">2007</text>
<circle cx="330" cy="150" r="40" class="bp"/><text x="330" y="146" text-anchor="middle" class="s b">Kabinett</text><text x="330" y="162" text-anchor="middle" class="s">2002</text>
<circle cx="200" cy="230" r="40" class="bp"/><text x="200" y="226" text-anchor="middle" class="s b">Spätlese</text><text x="200" y="242" text-anchor="middle" class="s">2007</text>
<circle cx="500" cy="110" r="38" class="bv"/><text x="500" y="114" text-anchor="middle" class="b">riesling</text>
<circle cx="560" cy="250" r="44" class="box"/><text x="560" y="246" text-anchor="middle" class="s b">Wine Expert</text><text x="560" y="262" text-anchor="middle" class="s b">Monthly</text>
<circle cx="420" cy="290" r="30" class="bg"/><text x="420" y="295" text-anchor="middle" class="b">Tom</text>
<circle cx="660" cy="60" r="30" class="bg"/><text x="660" y="65" text-anchor="middle" class="b">Alice</text>
<circle cx="660" cy="170" r="30" class="bg"/><text x="660" y="175" text-anchor="middle" class="b">Patty</text>
<line x1="152" y1="56" x2="288" y2="50" class="ln" marker-end="url(#arr)"/><text x="220" y="44" text-anchor="middle" class="s">produced</text>
<line x1="152" y1="88" x2="290" y2="138" class="ln" marker-end="url(#arr)"/>
<line x1="132" y1="112" x2="178" y2="194" class="ln" marker-end="url(#arr)"/>
<line x1="368" y1="62" x2="464" y2="98" class="lv" marker-end="url(#arrv)"/><text x="430" y="70" class="s tv">grape_type</text>
<line x1="370" y1="146" x2="462" y2="118" class="lv" marker-end="url(#arrv)"/>
<line x1="240" y1="222" x2="472" y2="136" class="lv" marker-end="url(#arrv)"/>
<line x1="540" y1="210" x2="360" y2="76" class="ln dash" marker-end="url(#arr)"/><text x="468" y="186" text-anchor="end" class="s">reported_on</text>
<line x1="630" y1="60" x2="372" y2="50" class="lgr" marker-end="url(#arrg)"/><text x="520" y="42" class="s tg">likes</text>
<line x1="396" y1="276" x2="362" y2="176" class="lgr" marker-end="url(#arrg)"/><text x="340" y="232" class="s tg">likes</text>
<line x1="450" y1="286" x2="514" y2="264" class="lgr" marker-end="url(#arrg)"/><text x="468" y="306" class="s tg">trusts</text>
<line x1="660" y1="140" x2="660" y2="92" class="lp" marker-end="url(#arrp)"/><text x="668" y="120" class="s tp">friends</text>
<path d="M650,198 C660,330 500,335 449,302" class="lp" marker-end="url(#arrp)"/><text x="596" y="336" class="s tp">friends</text>
</svg>
:::

:::analogy Why a graph instead of tables?
In SQL, "friends of friends who like riesling" means joining a friendships table to itself, then to a likes table, then to wines, then to grapes. Each join compares large sets of rows. In a graph you start at one person and **walk**: friends, then their likes, then the grape. Each step only touches the neighbors of the nodes you are standing on, so the cost depends on how much you visit, not on how big the whole database is.
:::

:::fig **Joins versus traversals.** Finding friends of friends in SQL repeats a self-join over the whole friendships table for every hop. In a graph, each hop follows pointers from the current nodes only.
<svg class="dg wide" viewBox="0 0 720 220">
<text x="170" y="22" text-anchor="middle" class="b ta">SQL: one self-join per hop</text>
<rect x="20" y="40" width="130" height="120" rx="6" class="ba"/><text x="85" y="60" text-anchor="middle" class="s b">friendships</text>
<g class="mono s"><text x="34" y="82">Ann | Bob</text><text x="34" y="100">Bob | Cal</text><text x="34" y="118">Cal | Dee</text><text x="34" y="136">… millions</text></g>
<rect x="190" y="40" width="130" height="120" rx="6" class="ba"/><text x="255" y="60" text-anchor="middle" class="s b">friendships</text>
<g class="mono s"><text x="204" y="82">Ann | Bob</text><text x="204" y="100">Bob | Cal</text><text x="204" y="118">Cal | Dee</text><text x="204" y="136">… millions</text></g>
<text x="170" y="104" text-anchor="middle" class="b">⋈</text>
<text x="170" y="190" text-anchor="middle" class="s">f1 JOIN f2 ON f1.friend = f2.person</text>
<line x1="360" y1="20" x2="360" y2="210" class="ln2 dash"/>
<text x="545" y="22" text-anchor="middle" class="b tp">Graph: follow the edges</text>
<circle cx="420" cy="110" r="26" class="bp"/><text x="420" y="115" text-anchor="middle" class="b">Ann</text>
<circle cx="520" cy="70" r="24" class="bp"/><text x="520" y="75" text-anchor="middle">Bob</text>
<circle cx="520" cy="150" r="24" class="bp"/><text x="520" y="155" text-anchor="middle">Eve</text>
<circle cx="630" cy="50" r="24" class="bg"/><text x="630" y="55" text-anchor="middle">Cal</text>
<circle cx="630" cy="120" r="24" class="bg"/><text x="630" y="125" text-anchor="middle">Fay</text>
<circle cx="630" cy="185" r="24" class="bg"/><text x="630" y="190" text-anchor="middle">Gus</text>
<line x1="444" y1="100" x2="496" y2="78" class="lp" marker-end="url(#arrp)"/><line x1="444" y1="120" x2="496" y2="144" class="lp" marker-end="url(#arrp)"/>
<line x1="544" y1="66" x2="606" y2="54" class="lgr" marker-end="url(#arrg)"/><line x1="544" y1="76" x2="606" y2="114" class="lgr" marker-end="url(#arrg)"/><line x1="544" y1="156" x2="606" y2="180" class="lgr" marker-end="url(#arrg)"/>
<text x="545" y="212" text-anchor="middle" class="s">touches only Ann's neighborhood</text>
</svg>
:::

## Day 1 · Graphs, Groovy and CRUD

### Step 1: Starting Neo4J

```bash
bin/neo4j start
curl http://localhost:7474/db/data/        # the REST API answers
```

Neo4J 1.7 shipped with a browser-based **web admin** (`http://localhost:7474/webadmin/`) with a dashboard, a **data browser** to create and inspect nodes and relationships by clicking, and a built-in **Gremlin console**.

In the data browser the book creates the first few nodes: a wine, *Prancing Wolf Ice Wine 2007*; its grape type, *riesling*; and a magazine, *Wine Expert Monthly*, connected with relationships `grape_type` and `reported_on`. Node IDs are assigned automatically (the first one is 0).

### Step 2: Gremlin, a language for walking graphs

**Gremlin** is a graph traversal language from the TinkerPop project, built on **Groovy** (a scripting language for the Java Virtual Machine). A Gremlin query is a **pipeline**: you start with some elements, and each step transforms the current set into a new one.

```groovy
gremlin> g.V                     // all vertices (nodes)
==>v[0]
==>v[1]
==>v[2]
gremlin> g.E                     // all edges (relationships)
==>e[0][1-reported_on->0]
==>e[1][0-grape_type->2]
gremlin> g.v(0)                  // the vertex with id 0
==>v[0]
gremlin> g.v(0).map()            // its properties
==>name=Prancing Wolf Ice Wine 2007
```

`g` is the graph. `V` and `E` are all vertices and all edges. An edge prints as `e[id][from-label->to]`, so `e[0][1-reported_on->0]` means "edge 0 goes from vertex 1 (the magazine) to vertex 0 (the ice wine), labeled reported_on". Vertex 2 is riesling. `filter{ ... }` keeps the elements for which a Groovy closure returns true; inside it, `it` is the current element.

```groovy
gremlin> g.V.filter{it.name=='riesling'}
==>v[2]

// from the magazine (v[1]): its outgoing edges, then the vertices those edges point into
gremlin> g.V.filter{it.name=='Wine Expert Monthly'}.outE
==>e[0][1-reported_on->0]
gremlin> g.V.filter{it.name=='Wine Expert Monthly'}.outE.inV.name
==>Prancing Wolf Ice Wine 2007

// out is a shortcut for outE.inV
gremlin> g.V.filter{it.name=='Wine Expert Monthly'}.out.name
==>Prancing Wolf Ice Wine 2007
```

:::fig **A Gremlin pipeline, step by step.** Each step takes the elements produced by the previous step and transforms them. Reading left to right: all vertices, keep the magazine, follow its outgoing edges, move to the vertices those edges point at, read their names.
<svg class="dg wide" viewBox="0 0 720 200">
<g class="mono s">
<rect x="0" y="30" width="80" height="34" rx="6" class="box"/><text x="40" y="52" text-anchor="middle">g.V</text>
<rect x="96" y="30" width="170" height="34" rx="6" class="box"/><text x="181" y="52" text-anchor="middle">.filter{name=='WEM'}</text>
<rect x="282" y="30" width="80" height="34" rx="6" class="box"/><text x="322" y="52" text-anchor="middle">.outE</text>
<rect x="378" y="30" width="80" height="34" rx="6" class="box"/><text x="418" y="52" text-anchor="middle">.inV</text>
<rect x="474" y="30" width="80" height="34" rx="6" class="box"/><text x="514" y="52" text-anchor="middle">.name</text>
</g>
<line x1="80" y1="47" x2="94" y2="47" class="ln" marker-end="url(#arr)"/><line x1="266" y1="47" x2="280" y2="47" class="ln" marker-end="url(#arr)"/><line x1="362" y1="47" x2="376" y2="47" class="ln" marker-end="url(#arr)"/><line x1="458" y1="47" x2="472" y2="47" class="ln" marker-end="url(#arr)"/>
<circle cx="20" cy="110" r="10" class="bp"/><circle cx="44" cy="110" r="10" class="bp"/><circle cx="68" cy="110" r="10" class="bp"/><circle cx="32" cy="136" r="10" class="bp"/><circle cx="56" cy="136" r="10" class="bp"/>
<text x="40" y="170" text-anchor="middle" class="s">every node</text>
<circle cx="181" cy="122" r="14" class="box"/><text x="181" y="170" text-anchor="middle" class="s">the magazine</text>
<line x1="300" y1="122" x2="346" y2="122" class="lp" marker-end="url(#arrp)"/><text x="322" y="170" text-anchor="middle" class="s">reported_on edge</text>
<circle cx="418" cy="122" r="14" class="bp"/><text x="418" y="170" text-anchor="middle" class="s">the wine</text>
<text x="514" y="126" text-anchor="middle" class="mono s b">"Prancing Wolf</text><text x="514" y="142" text-anchor="middle" class="mono s b">Ice Wine 2007"</text>
<text x="620" y="52" class="s">out = outE.inV</text><text x="620" y="70" class="s">in = inE.outV</text><text x="620" y="88" class="s">both = either</text>
</svg>
:::

:::deep Gremlin and jQuery
The book compares Gremlin with **jQuery**, the JavaScript library for web pages. In jQuery, `$('#navigation').children('li').each(...)` starts at an element and walks the document tree step by step. Gremlin does the same on a graph: `g.V.filter{...}.out.filter{...}`. If you have chained jQuery calls, Gremlin's style will feel natural.
:::

### Step 3: Creating nodes and relationships

```groovy
gremlin> pwolf = g.addVertex([name : 'Prancing Wolf Winery'])
==>v[3]
gremlin> g.addEdge(pwolf, g.v(0), 'produced')
==>e[2][3-produced->0]

gremlin> kabinett = g.addVertex([name : 'Prancing Wolf Kabinett 2002'])
==>v[4]
gremlin> g.addEdge(pwolf, kabinett, 'produced')
==>e[3][3-produced->4]
gremlin> spatlese = g.addVertex([name : 'Prancing Wolf Spatlese 2007'])
==>v[5]
gremlin> g.addEdge(pwolf, spatlese, 'produced')
==>e[4][3-produced->5]

// relationships can have properties too
gremlin> riesling = g.V.filter{it.name=='riesling'}.next()
==>v[2]
gremlin> g.addEdge([style:'kabinett'], kabinett, riesling, 'grape_type')
==>e[5][4-grape_type->2]
gremlin> g.addEdge([style:'spatlese'], spatlese, riesling, 'grape_type')
```

`addVertex(properties)` creates a node; `addEdge(from, to, label)` creates a directed relationship; an optional first argument gives the edge properties. `.next()` takes the first element out of a pipeline, so you get the vertex itself rather than a pipe.

:::fig **The property graph model.** Nodes and relationships both hold key-value properties. Every relationship has exactly one type (its label), a direction, a start node and an end node.
<svg class="dg" viewBox="0 0 720 194">
<circle cx="130" cy="95" r="68" class="bp"/>
<text x="130" y="72" text-anchor="middle" class="b">node 4</text>
<text x="130" y="94" text-anchor="middle" class="mono s">name:</text><text x="130" y="110" text-anchor="middle" class="mono s">"Prancing Wolf</text><text x="130" y="126" text-anchor="middle" class="mono s">Kabinett 2002"</text>
<circle cx="575" cy="95" r="60" class="bv"/>
<text x="575" y="82" text-anchor="middle" class="b">node 1</text><text x="575" y="102" text-anchor="middle" class="mono s">name:</text><text x="575" y="118" text-anchor="middle" class="mono s">"riesling"</text>
<line x1="200" y1="95" x2="512" y2="95" class="lv" marker-end="url(#arrv)"/>
<rect x="270" y="56" width="160" height="30" rx="6" class="box"/><text x="350" y="76" text-anchor="middle" class="mono s b">type: grape_type</text>
<rect x="270" y="104" width="160" height="30" rx="6" class="box"/><text x="350" y="124" text-anchor="middle" class="mono s">style: "kabinett"</text>
<text x="350" y="160" text-anchor="middle" class="s">relationship: type + direction + properties</text>
<text x="130" y="182" text-anchor="middle" class="s">start node</text><text x="575" y="176" text-anchor="middle" class="s">end node</text>
</svg>
:::

### Step 4: Cypher, the declarative alternative

Gremlin says **how** to walk. Neo4J's own language, **Cypher**, says **what pattern** to find, drawn as ASCII art: `()` is a node, `-[:TYPE]->` is a relationship.

```cypher
START ice_wine=node(0)
MATCH (ice_wine) -[:grape_type]-> () <-[:grape_type]- (similar)
RETURN similar
```

Read it as: "start at node 0; find a node it points to with `grape_type`; find other nodes that point to that same node with `grape_type`; return them." In other words: **wines made from the same grape**.

:::fig **A Cypher pattern is a drawing of what you want.** The query matches every way this shape occurs in the graph, binding `similar` to each wine that shares the ice wine's grape type.
<svg class="dg" viewBox="0 0 720 170">
<text x="360" y="26" text-anchor="middle" class="mono">(ice_wine) -[:grape_type]-&gt; () &lt;-[:grape_type]- (similar)</text>
<circle cx="120" cy="100" r="40" class="bp"/><text x="120" y="96" text-anchor="middle" class="s b">ice_wine</text><text x="120" y="112" text-anchor="middle" class="s">node(0)</text>
<circle cx="360" cy="100" r="36" class="bv"/><text x="360" y="105" text-anchor="middle" class="s">riesling</text>
<circle cx="610" cy="100" r="50" class="bg"/><text x="610" y="90" text-anchor="middle" class="s b">similar</text><text x="610" y="107" text-anchor="middle" class="s">Kabinett,</text><text x="610" y="122" text-anchor="middle" class="s">Spätlese</text>
<line x1="162" y1="100" x2="320" y2="100" class="lv" marker-end="url(#arrv)"/>
<line x1="558" y1="100" x2="400" y2="100" class="lv" marker-end="url(#arrv)"/>
<text x="240" y="90" text-anchor="middle" class="s tv">grape_type</text><text x="480" y="90" text-anchor="middle" class="s tv">grape_type</text>
<text x="360" y="158" text-anchor="middle" class="s">() is an anonymous node: "any node here"</text>
</svg>
:::

A richer version from the book uses an index lookup, a regular-expression filter and aggregation:

```cypher
START ice_wine=node:wines(name="Prancing Wolf Ice Wine 2007")
MATCH ice_wine -[:grape_type]-> wine_type <-[:grape_type]- similar
WHERE wine_type.name =~ /(?i)riesl.*/
RETURN wine_type.name, collect(similar.name) as wines, count(*) as wine_count
ORDER BY wine_count desc
LIMIT 10
```

| | Gremlin | Cypher |
|---|---|---|
| Style | Imperative: a pipeline of steps | Declarative: a pattern to match |
| Origin | TinkerPop, works on many graph databases | Created by Neo4J |
| Strength | Fine control, custom steps, algorithms | Readable, close to the whiteboard drawing |

### Step 5: A small social network

The book adds three people and connects them to the wines and the magazine:

```groovy
alice = g.addVertex([name:'Alice'])
ice_wine = g.V.filter{it.name=='Prancing Wolf Ice Wine 2007'}.next()
g.addEdge(alice, ice_wine, 'likes')

tom = g.addVertex([name:'Tom'])
kabinett = g.V.filter{it.name=='Prancing Wolf Kabinett 2002'}.next()
g.addEdge(tom, kabinett, 'likes')
g.addEdge(tom, ice_wine, 'likes')
g.addEdge(tom, g.V.filter{it.name=='Wine Expert Monthly'}.next(), 'trusts')

patty = g.addVertex([name:'Patty'])
g.addEdge(patty, tom, 'friends')
g.addEdge(patty, alice, 'friends')
```

Some useful traversal steps:

```groovy
// back(n) returns to the element n steps earlier: Alice's out-edges, their targets, back to Alice
gremlin> alice.outE.inV.back(2).name
==>Alice

// groupCount: count how often each value appears
gremlin> name_map = [:]
gremlin> g.V.name.groupCount( name_map )
gremlin> name_map
==>Prancing Wolf Ice Wine 2007=1
==>riesling=1
...

// how many wines does each person like?
gremlin> wines_count = [:]
gremlin> g.V.outE('likes').outV.name.groupCount( wines_count )
gremlin> wines_count
==>Alice=1
==>Tom=2

// transform: output a custom value per element, here each friendship as a pair
gremlin> g.V.outE('friends').transform{[it.outV.name.next(), it.inV.name.next()]}
==>[Patty, Tom]
==>[Patty, Alice]

// both: follow edges in either direction; dedup: remove duplicates
gremlin> g.V.both('friends').dedup.name
==>Tom
==>Patty
==>Alice
```

`friends` is stored with one direction, but friendship is mutual, which is why `both` matters here.

### Step 6: Defining your own steps

Gremlin lets you package a traversal as a new, reusable **step**. The book defines two.

`varietal`: from a wine, go to its grape type:

```groovy
Gremlin.defineStep( 'varietal',
  [Vertex, Pipe],
  {_().out('grape_type').dedup}
)

gremlin> g.V.filter{it.name=='Prancing Wolf Ice Wine 2007'}.varietal.name
==>riesling
```

`friendsuggest`: from a person, find wines their friends like (excluding the person themself):

```groovy
Gremlin.defineStep( 'friendsuggest',
  [Vertex, Pipe],
  {
    _().sideEffect{start = it}.both('friends').
    except([start]).out('likes').dedup
  }
)

gremlin> g.V.filter{it.name=='Patty'}.friendsuggest.name
==>Prancing Wolf Ice Wine 2007
==>Prancing Wolf Kabinett 2002

// steps compose: grapes of the wines Patty's friends like
gremlin> g.V.filter{it.name=='Patty'}.friendsuggest.varietal.name
==>riesling
```

`_()` is the identity pipe, the starting point of a custom step. `sideEffect{start = it}` remembers the starting person, so `except([start])` can remove them.

:::fig **The friendsuggest step.** From Patty, walk to her friends (in either direction), drop Patty herself, follow their likes, and remove duplicates. The result is a list of wines to recommend to Patty.
<svg class="dg wide" viewBox="0 0 720 220">
<circle cx="90" cy="110" r="36" class="bg"/><text x="90" y="115" text-anchor="middle" class="b">Patty</text>
<circle cx="290" cy="60" r="32" class="bg"/><text x="290" y="65" text-anchor="middle" class="b">Tom</text>
<circle cx="290" cy="170" r="32" class="bg"/><text x="290" y="175" text-anchor="middle" class="b">Alice</text>
<circle cx="520" cy="60" r="40" class="bp"/><text x="520" y="56" text-anchor="middle" class="s b">Kabinett</text><text x="520" y="72" text-anchor="middle" class="s">2002</text>
<circle cx="520" cy="170" r="40" class="bp"/><text x="520" y="166" text-anchor="middle" class="s b">Ice Wine</text><text x="520" y="182" text-anchor="middle" class="s">2007</text>
<line x1="124" y1="96" x2="258" y2="66" class="lp" marker-end="url(#arrp)"/><line x1="124" y1="124" x2="258" y2="164" class="lp" marker-end="url(#arrp)"/>
<text x="180" y="66" class="s tp">friends</text><text x="180" y="166" class="s tp">friends</text>
<line x1="322" y1="60" x2="478" y2="60" class="lgr" marker-end="url(#arrg)"/><line x1="320" y1="74" x2="482" y2="156" class="lgr" marker-end="url(#arrg)"/><line x1="322" y1="170" x2="478" y2="170" class="lgr" marker-end="url(#arrg)"/>
<text x="400" y="52" class="s tg">likes</text><text x="410" y="190" class="s tg">likes</text>
<text x="574" y="104" class="s">Ice Wine is reached</text><text x="574" y="120" class="s">twice; dedup keeps</text><text x="574" y="136" class="s">it once</text>
</svg>
:::

### Step 7: Updating and deleting

Properties on nodes and edges are changed like Groovy object fields:

```groovy
gremlin> e = g.V.filter{it.name=='Alice'}.outE('likes').next()
gremlin> e.weight = 95
gremlin> e.save
gremlin> e.removeProperty('weight')
gremlin> e.save

// delete every vertex (and with them their edges)…
gremlin> g.V.each{ g.removeVertex(it) }
// …or every edge…
gremlin> g.E.each{ g.removeEdge(it) }
// …or simply everything
gremlin> g.clear()
gremlin> g.shutdown()       // when using an embedded graph, close it cleanly
```

### Day 1 homework, solved

**Find:** the Neo4J wiki and the Gremlin steps documentation; the other shells were the **Cypher** console and the **Neo4J shell** (`neo4j-shell`) in the web admin.

**1. Query all node names with Cypher** (1.7 syntax):

```cypher
START n=node(*)
RETURN n.name?
```

`n.name?` returns null instead of failing for nodes without a `name` (the `?` operator of early Cypher).

**2. Delete all nodes and relationships:**

```cypher
START n=node(*)
MATCH n-[r?]-()
DELETE n, r
```

(In Gremlin: `g.clear()`.)

**3. A family graph** in Gremlin:

```groovy
grandma = g.addVertex([name:'Anahit', born:1945])
mom     = g.addVertex([name:'Lilit',  born:1972])
dad     = g.addVertex([name:'Aram',   born:1970])
me      = g.addVertex([name:'Gor',    born:1998])
sister  = g.addVertex([name:'Mane',   born:2001])
g.addEdge(grandma, mom, 'parent_of')
[mom, dad].each { p -> [me, sister].each { c -> g.addEdge(p, c, 'parent_of') } }
g.addEdge(mom, dad, 'married_to')
g.addEdge(me, sister, 'sibling_of')

// grandchildren of Anahit
g.V.filter{it.name=='Anahit'}.out('parent_of').out('parent_of').name
```

## Day 2 · REST, indexes and algorithms

### Step 1: The REST interface

Neo4J can run **embedded** inside a Java application, or as a **server** with a REST API that any language can use. The REST API represents every node and relationship as a URL:

```bash
curl -i -X POST http://localhost:7474/db/data/node \
  -H "Content-Type: application/json" \
  -d '{"name": "P.G. Wodehouse", "genre": "British Humour"}'
# HTTP/1.1 201 Created
# Location: http://localhost:7474/db/data/node/9
# { "self": ".../node/9", "properties": ".../node/9/properties",
#   "outgoing_relationships": ".../node/9/relationships/out", ... }

curl http://localhost:7474/db/data/node/9/properties/genre
# "British Humour"
```

The response is full of links to related resources (properties, relationships, traversals), so a client can discover the API by following them.

Create a book and a relationship from the author:

```bash
curl -X POST http://localhost:7474/db/data/node \
  -H "Content-Type: application/json" \
  -d '{"name" : "Jeeves Takes Charge", "style" : "short story"}'
# Location: .../node/10

curl -X POST http://localhost:7474/db/data/node/9/relationships \
  -H "Content-Type: application/json" \
  -d '{"to": "http://localhost:7474/db/data/node/10", "type": "WROTE",
       "data": {"published": "November 28, 1924"}}'
```

**Paths** between two nodes, using a built-in algorithm:

```bash
curl -X POST http://localhost:7474/db/data/node/9/paths \
  -H "Content-Type: application/json" \
  -d '{"to":"http://localhost:7474/db/data/node/1",
       "relationships": {"type" : "WROTE"},
       "algorithm" : "shortestPath", "max_depth" : 10}'
```

### Step 2: Indexes

Walking from a node is fast, but how do you find the **starting** node? Scanning every node with `filter{it.name == ...}` is slow on a big graph. Neo4J 1.x used **Lucene** (a search engine library) for **indexes**: you explicitly add a node to an index under a key and value, then look it up.

```bash
# add node 9 to the "authors" index under name = "P.G. Wodehouse"
curl -X POST http://localhost:7474/db/data/index/node/authors \
  -H "Content-Type: application/json" \
  -d '{ "uri" : "http://localhost:7474/db/data/node/9",
        "key" : "name", "value" : "P.G.+Wodehouse"}'

curl http://localhost:7474/db/data/index/node/authors/name/P.G.+Wodehouse

# a full-text index allows wildcard and fuzzy queries
curl -X POST http://localhost:7474/db/data/index/node \
  -H "Content-Type: application/json" \
  -d '{"name" : "fulltext", "config" : {"type":"fulltext","provider":"lucene"}}'
curl http://localhost:7474/db/data/index/node/fulltext?query=name:P*
```

:::fig **Index first, then traverse.** An index answers "which node is P.G. Wodehouse?" in one lookup. From there, every further question is a walk along relationships. This "find the start, then traverse" pattern is how almost every graph query works.
<svg class="dg wide" viewBox="0 0 720 180">
<rect x="10" y="40" width="196" height="100" rx="10" class="bw"/>
<text x="105" y="62" text-anchor="middle" class="b">index "authors"</text>
<g class="mono s"><text x="22" y="86">name=P.G. Wodehouse → 9</text><text x="22" y="106">name=Jane Austen → 14</text><text x="22" y="126">…</text></g>
<line x1="208" y1="86" x2="288" y2="86" class="lw" marker-end="url(#arrw)"/><text x="245" y="76" text-anchor="middle" class="s">1. lookup</text>
<circle cx="340" cy="86" r="46" class="bp"/><text x="340" y="82" text-anchor="middle" class="s b">node 9</text><text x="340" y="98" text-anchor="middle" class="s">Wodehouse</text>
<line x1="388" y1="70" x2="500" y2="44" class="lp" marker-end="url(#arrp)"/><line x1="388" y1="100" x2="500" y2="128" class="lp" marker-end="url(#arrp)"/>
<text x="440" y="46" class="s tp">WROTE</text><text x="440" y="136" class="s tp">WROTE</text>
<rect x="504" y="24" width="200" height="40" rx="8" class="box"/><text x="604" y="49" text-anchor="middle" class="s">Jeeves Takes Charge</text>
<rect x="504" y="110" width="200" height="40" rx="8" class="box"/><text x="604" y="135" text-anchor="middle" class="s">Right Ho, Jeeves</text>
<text x="450" y="172" text-anchor="middle" class="s">2. traverse from there</text>
</svg>
:::

### Step 3: Gremlin over REST

The server includes a **Gremlin plug-in**, so you can send a whole Gremlin script over HTTP and get the result as JSON:

```bash
curl -X POST \
  http://localhost:7474/db/data/ext/GremlinPlugin/graphdb/execute_script \
  -H "content-type:application/json" \
  -d '{"script":"g.V.name"}'
```

This combines the best of both: REST for access from any language, Gremlin for expressive traversals executed on the server.

### Step 4: A big dataset: movies and actors

To try graph algorithms on real data, the book imports a large tab-separated file of film performances (actor, movie, role) from **Freebase**, an open knowledge base. A Ruby script reads each line and creates actor nodes, movie nodes and relationships between them through the REST API, using an index so each actor and movie is created only once.

```bash
ruby importer.rb performance.tsv
```

#### Six degrees of Kevin Bacon

A famous game says every actor is connected to Kevin Bacon through a short chain of films. In a graph, "connected through films" is just a **path**: actor → movie → actor → movie → … → Kevin Bacon.

The book first defines a **`costars`** step, similar to `friendsuggest`: from an actor, go out along `ACTED_IN` to their movies, back in along `ACTED_IN` to everyone in those movies, drop the starting actor, and remove duplicates.

```groovy
Gremlin.defineStep( 'costars',
  [Vertex, Pipe],
  {
    _().sideEffect{start = it}.outE('ACTED_IN').
    inV.inE('ACTED_IN').outV.filter{
      !start.equals(it)
    }.dedup
  }
)
```

Then it walks outward from Elvis Presley, repeating `costars` with `loop`, and keeps only walks that reach Kevin Bacon:

```groovy
gremlin> bacon = g.V.filter{it.name=='Kevin Bacon'}.next()
gremlin> elvis = g.V.filter{it.name=='Elvis Presley'}.next()

gremlin> (elvis.costars.loop(1){
           it.loops < 4 & !it.object.equals(bacon)
         }.filter{it.equals(bacon)}.paths >> 1).name.grep{it}
==>Elvis Presley
==>Double Trouble
==>Roddy McDowall
==>The Big Picture
==>Kevin Bacon
```

How to read it, piece by piece:

- `loop(1){ … }` jumps back **one step** (to `costars`) and repeats it while the closure is true. `it.loops` counts the repetitions, so `it.loops < 4` stops at four degrees of separation, and `!it.object.equals(bacon)` stops a walk once it reaches Bacon.
- `filter{it.equals(bacon)}` keeps only the walks that ended at Bacon.
- `paths` returns the whole route of each walk, not just its end point. Because a traversal reaches near nodes first, the first path is a shortest one; `>> 1` takes it.
- `.name.grep{it}` prints each element's name and drops the edges, which have no name.

:::fig **The path the book finds from Elvis Presley to Kevin Bacon.** Actors and movies alternate along the path, so two movies separate them. The authors admit they didn't know who Roddy McDowall was, which is the point: the graph found the answer without them knowing it.
<svg class="dg wide" viewBox="0 0 720 170">
<circle cx="60" cy="80" r="40" class="bp"/><text x="60" y="76" text-anchor="middle" class="s b">Elvis</text><text x="60" y="92" text-anchor="middle" class="s b">Presley</text>
<rect x="140" y="58" width="120" height="44" rx="8" class="box"/><text x="200" y="78" text-anchor="middle" class="s">Double</text><text x="200" y="94" text-anchor="middle" class="s">Trouble</text>
<circle cx="340" cy="80" r="40" class="bp"/><text x="340" y="76" text-anchor="middle" class="s b">Roddy</text><text x="340" y="92" text-anchor="middle" class="s b">McDowall</text>
<rect x="420" y="58" width="120" height="44" rx="8" class="box"/><text x="480" y="78" text-anchor="middle" class="s">The Big</text><text x="480" y="94" text-anchor="middle" class="s">Picture</text>
<circle cx="640" cy="80" r="40" class="bg"/><text x="640" y="76" text-anchor="middle" class="s b">Kevin</text><text x="640" y="92" text-anchor="middle" class="s b">Bacon</text>
<line x1="100" y1="80" x2="138" y2="80" class="ln"/><line x1="262" y1="80" x2="298" y2="80" class="ln"/><line x1="380" y1="80" x2="418" y2="80" class="ln"/><line x1="542" y1="80" x2="598" y2="80" class="ln"/>
<text x="200" y="130" text-anchor="middle" class="s">ACTED_IN</text><text x="480" y="130" text-anchor="middle" class="s">ACTED_IN</text>
<text x="360" y="156" text-anchor="middle" class="s">two movies between Elvis and Kevin Bacon</text>
</svg>
:::

#### Who is most central?

Another question for the movie graph: **which actors have the most connections?** The book counts, for each vertex, how many edges lead into it, using `groupCount` inside a loop:

```groovy
role_count = [:]; count = 0
g.V.in.groupCount(role_count).loop(2){ count++ < 1000 }; ''
role_count.sort{a,b -> a.value <=> b.value}       // the last entries have the most credits
```

The map is keyed by vertex, with the number of edges as the value. Sorted, its last entry in the book's data was the voice actor **Mel Blanc**, with 424 acting credits. (The trailing `; ''` just stops the console from printing a huge result.)

For serious analysis the book plugs in **JUNG** (Java Universal Network/Graph Framework), a library of graph algorithms. Gremlin's `GraphJung` wrapper lets JUNG work directly on a Neo4J graph. The book uses the `BarycenterScorer`, which scores each node by its distance to all other nodes: the **lower** the score, the more central the node. If Kevin Bacon really were the center of Hollywood, his score would be among the lowest.

```groovy
j = new GraphJung( g )
// only follow ACTED_IN edges, so the algorithm works on actors and their movies
t = new EdgeLabelTransformer(['ACTED_IN'] as Set, false)

import edu.uci.ics.jung.algorithms.scoring.BarycenterScorer
barycenter = new BarycenterScorer<Vertex,Edge>( j, t )

bacon = g.V.filter{it.name=='Kevin Bacon'}.next()
bacon_score = barycenter.getVertexScore(bacon)
==>~0.0166

// which of Bacon's costars are even more central than he is?
connected = [:]
bacon.costars.each{
  score = barycenter.getVertexScore(it);
  if(score < bacon_score) { connected[it] = score; }
}
connected.collect{k,v -> k.name + " => " + v}
==>Donald Sutherland => 0.00925
```

Scoring every actor would take a very long time, so the book only scores Bacon's costars. In its data, **Donald Sutherland** turned out to be better connected than Kevin Bacon. (The dataset changes over time, so your results may differ.)

### Day 2 homework, solved

**1. A reusable `actor_path` function:**

```groovy
// 1. the path-finding part as its own step
Gremlin.defineStep( 'actor_path_to',
  [Vertex, Pipe],
  { target, maxLoops ->
    _().costars.loop(1){
      it.loops < maxLoops & !it.object.equals(target)
    }.filter{it.equals(target)}.paths
  }
)

// 2. a general function: the shortest path between two named actors
def actor_path(g, name1, name2) {
  def from = g.V.filter{it.name == name1}.next()
  def to   = g.V.filter{it.name == name2}.next()
  def path = from.actor_path_to(to, 4) >> 1      // first path found = a shortest one
  path ? path.name.grep{it} : null               // drop unnamed edges
}

actor_path(g, 'Elvis Presley', 'Kevin Bacon')
// [Elvis Presley, Double Trouble, Roddy McDowall, The Big Picture, Kevin Bacon]
```

The path alternates actor, movie, actor, so the number of movies on it is the "degree of separation" (2 here). Returning `null` means no path within the loop limit; try a larger limit.

**2. Run a JUNG algorithm**, for example PageRank on the whole graph:

```groovy
import edu.uci.ics.jung.algorithms.scoring.PageRank
j = new GraphJung(g)
pr = new PageRank<Vertex,Edge>(j, 0.15d)
pr.evaluate()
g.V.sort{ -pr.getVertexScore(it) }[0..9].name
```

**3. A company graph and its best-connected person.** Create people as nodes with `REPORTS_TO` and `WORKS_WITH` edges, then score each by **closeness**: the average shortest-path distance to everyone else (smaller is better connected):

```groovy
import edu.uci.ics.jung.algorithms.scoring.ClosenessCentrality
j = new GraphJung(g)
cc = new ClosenessCentrality<Vertex,Edge>(j)
// JUNG returns the inverse of the average distance, so a higher score = more central
g.V.sort{ -cc.getVertexScore(it) }.name.next()   // the most central person
```

## Day 3 · Distributed high availability

### Step 1: Transactions

Unlike most NoSQL databases of 2012, Neo4J is fully **ACID**. Every change happens inside a transaction (the REST API and the web console create one per request automatically). In Gremlin you can control transactions manually, so several changes succeed or fail together:

```groovy
g.setTransactionMode(TransactionalGraph.Mode.MANUAL)
g.startTransaction()
  ann = g.addVertex([name:'Ann'])
  g.addEdge(ann, g.V.filter{it.name=='Alice'}.next(), 'friends')
g.stopTransaction(TransactionalGraph.Conclusion.SUCCESS)    // commit
// or g.stopTransaction(TransactionalGraph.Conclusion.FAILURE) to roll back
```

:::tip Why transactions matter more for graphs
A graph change often touches several elements at once: a new node plus its relationships. Without a transaction, a crash halfway could leave a relationship pointing at nothing, or a node cut off from the rest of the graph. ACID transactions keep the graph's structure intact.
:::

### Step 2: High availability (HA)

Neo4J's **Enterprise** edition can replicate a graph across several servers in an **HA cluster**. In the 1.x design:

- One server is the **master**; the others are **slaves**.
- Unlike MongoDB's secondaries, **slaves accept writes**. A write sent to a slave is synchronized with the master, which then passes it on to the other slaves. The book warns that because slaves are not updated at the same instant, HA gives up strict ACID guarantees across the cluster for a brief moment.
- Slaves **pull** updates from the master periodically (`ha.pull_interval`). Until a slave pulls, it can serve slightly old data.
- A **ZooKeeper** cluster (the same coordination service HBase uses; Neo4J shipped it as the `neo4j-coordinator`) keeps track of the members and **elects a new master** if the current one dies.

:::fig **The Neo4J HA cluster from the book.** Three Neo4J servers, one of them master, coordinated by three ZooKeeper instances. All writes reach the master; slaves pull its changes on an interval, so reads from a slave may briefly lag. If the master fails, the coordinators elect a new one.
<svg class="dg wide" viewBox="0 0 720 270">
<rect x="250" y="20" width="220" height="70" rx="10" class="bp"/><text x="360" y="48" text-anchor="middle" class="b">Neo4J master</text><text x="360" y="68" text-anchor="middle" class="s">has every write</text>
<rect x="40" y="170" width="200" height="70" rx="10" class="box"/><text x="140" y="198" text-anchor="middle" class="b">slave 1</text><text x="140" y="218" text-anchor="middle" class="s">full copy of the graph</text>
<rect x="480" y="170" width="200" height="70" rx="10" class="box"/><text x="580" y="198" text-anchor="middle" class="b">slave 2</text><text x="580" y="218" text-anchor="middle" class="s">full copy of the graph</text>
<line x1="270" y1="92" x2="170" y2="166" class="ln dash" marker-end="url(#arr)"/><line x1="450" y1="92" x2="550" y2="166" class="ln dash" marker-end="url(#arr)"/>
<text x="50" y="130" class="s">pull every N seconds</text>
<line x1="230" y1="166" x2="290" y2="94" class="lp" marker-end="url(#arrp)"/><text x="266" y="150" class="s tp">write via slave:</text><text x="266" y="164" class="s tp">synced to master</text>
<rect x="290" y="180" width="140" height="70" rx="10" class="bw"/><text x="360" y="206" text-anchor="middle" class="b">ZooKeeper ×3</text><text x="360" y="226" text-anchor="middle" class="s">membership,</text><text x="360" y="242" text-anchor="middle" class="s">master election</text>
<line x1="360" y1="178" x2="360" y2="94" class="ln2"/><line x1="288" y1="215" x2="242" y2="205" class="ln2"/><line x1="432" y1="215" x2="478" y2="205" class="ln2"/>
</svg>
:::

The book's configuration starts three coordinators and three Neo4J servers, each with settings like:

```properties
# conf/neo4j.properties on server 1
ha.server_id=1
ha.coordinators=localhost:2181,localhost:2182,localhost:2183
ha.server=localhost:6001
ha.pull_interval=1
```

```properties
# conf/neo4j-server.properties
org.neo4j.server.database.mode=HA
```

Servers 2 and 3 use `ha.server_id=2` and `3`, and `ha.server` ports 6002 and 6003. The book then writes on one slave and checks the others: the write goes to the master first and then reaches the other slave on its next pull.

:::deep Why HA is "read-mostly"
All writes funnel through one master, so adding servers increases **read** capacity, not write capacity. And because slaves pull changes on an interval, a read from a slave right after a write may not see it yet: the cluster is **eventually consistent** across servers. That is why the authors recommend Neo4J HA for **read-mostly** workloads.
:::

### Step 3: Backups

The Enterprise edition includes **online backups**: you copy a running database without stopping it, either a full copy or only what changed since the last backup.

```bash
# full backup of the HA cluster into a directory named after today's date
bin/neo4j-backup -full -from ha://localhost:2181,localhost:2182,localhost:2183 \
  -to /mnt/backups/neo4j-`date +%Y.%m.%d`.db

# on a single server, change the mode to single; later backups the same day can be incremental
bin/neo4j-backup -incremental -from single://localhost \
  -to /mnt/backups/neo4j-`date +%Y.%m.%d`.db
```

Pointing the backup at the coordinators means it copies from the cluster's most up-to-date data. An incremental backup only works on top of a full one in the same directory, and the result is a complete, usable database directory: to restore, replace a server's data directory with it.

:::warn The licence matters
Everything on Day 3 (HA, online backups) required **Neo4J Enterprise**, licensed under the AGPL or a commercial licence. The Community edition used on Days 1 and 2 is GPL. If you run a closed-source service on the Enterprise features, you need a commercial licence from Neo Technology (now Neo4j, Inc.).
:::

### Day 3 homework, solved

**Find:** the licensing guide on the Neo4J site. The **maximum size** in Neo4J 1.x: about **34.4 billion nodes, 34.4 billion relationships** and 68.7 billion properties.

**1. Replicate across three physical servers.** On each machine, install Neo4J Enterprise and a coordinator; list all three coordinators in `ha.coordinators` on every server (using real hostnames instead of `localhost`), give each a unique `ha.server_id`, set `database.mode=HA`, start the coordinators first and then the three databases.

**2. A load balancer in front of the cluster.** An Nginx configuration that spreads REST requests over the three servers:

```nginx
upstream neo4j_cluster {
  server neo1.example.com:7474;
  server neo2.example.com:7474;
  server neo3.example.com:7474;
}
server {
  listen 80;
  location / {
    proxy_pass http://neo4j_cluster;
  }
}
```

```bash
curl -X POST http://loadbalancer/db/data/ext/GremlinPlugin/graphdb/execute_script \
  -H "content-type:application/json" -d '{"script":"g.V.count()"}'
```

## Wrap-up · Strengths and weaknesses

Neo4J is a leading open-source example of the (then rare) graph database. Modeling is simple: create nodes, connect them, hang key-value pairs on both. Querying is just as simple: declare how to walk the graph from a starting node.

### Strengths

- **Perfect for unstructured, connected data**, arguably even more so than document stores: it is typeless, schemaless and puts no limits on how data relates.
- **Big enough for most uses**: 34.4 billion nodes and relationships in 1.x (enough for more than 42 nodes for each of Facebook's 800 million users in 2012).
- **Fast traversals.** Moving from a node to a neighbor is always one step, however large the graph grows. There is no bulk join and filter.
- **Good tooling**: Lucene indexes, Gremlin, Cypher and the REST interface.
- **High availability** for read-heavy sites, in the Enterprise edition.

### Weaknesses

- In the book's version, a relationship could not point from a node back to itself.
- The terms *node*/*relationship* instead of the usual *vertex*/*edge* can complicate communication.
- **HA replicates the whole graph** to every server; it cannot shard a graph into pieces, which caps the graph's size (in the tens of billions).
- **Licensing**: the Enterprise features (HA, backups) need the AGPL or a paid licence.

### Neo4J and CAP

When distributed, the name says it: Neo4J **High Availability** is **AP**. Each slave returns what it currently has, which may briefly lag behind the master. You can shorten the lag with a smaller pull interval, but it remains **eventually consistent** across servers. That is why HA suits read-mostly workloads.

### Parting thoughts

Neo4J's simplicity can be off-putting if you are not used to modeling graphs, and in 2012 it had relatively few users despite years of production use. The authors put that down to unfamiliarity, because graphs match how people naturally think: we picture families as trees and friends as networks, not as self-referencing tables. For social networks Neo4J is the obvious choice, but give it a thought for less obvious problems too, such as recommendations, access control, routing and dependency tracking.

:::modern Neo4J in 2026
- **Cypher won.** Neo4J's own language became the standard way to use it, and it changed a lot: **labels** arrived in 2.0 (2013), so you write `MATCH (w:Wine {name: "Ice Wine"})` instead of `START w=node(0)`; `START` and the `?` operator were removed; indexes and uniqueness **constraints** are declared on labels with `CREATE INDEX` / `CREATE CONSTRAINT`, replacing manual Lucene indexes.
- **A standard query language.** In 2024 ISO published **GQL** (ISO/IEC 39075), the first new ISO database language since SQL, heavily based on Cypher. openCypher implementations exist in other databases too.
- **Gremlin moved elsewhere.** The Gremlin plug-in and the old `/db/data` REST API are gone from Neo4J (removed by 4.0). Gremlin lives on in **Apache TinkerPop**, used by JanusGraph, Amazon Neptune and Azure Cosmos DB.
- **New protocols and drivers.** Clients use the binary **Bolt** protocol (since 3.0) with official drivers, or an HTTP endpoint that runs Cypher in transactions.
- **New version numbers.** After 5.26 LTS (December 2024), the last "5.x" release, Neo4J switched to calendar versions such as 2025.01 and 2026.06, released roughly monthly. Cypher itself now has versions (Cypher 5 and Cypher 25), with Cypher 25 tracking the GQL standard.
- **Clustering.** The master/slave HA of the book was replaced by **Causal Clustering** (3.1), based on the Raft consensus algorithm, and later by the more flexible clustering of Neo4J 5 and later, with primaries and secondaries hosting many databases. Size limits like 34 billion nodes no longer apply.
- **Algorithms built in.** Instead of JUNG, the **Graph Data Science** library offers PageRank, community detection, shortest paths, similarity and graph embeddings. Graphs are also popular for AI "GraphRAG" systems, which combine knowledge graphs with language models.
- **Cloud:** Neo4J AuraDB is the managed service. The Community edition remains GPLv3; Enterprise is commercial.
:::

:::key Chapter 7 in a nutshell
- **Model:** nodes and directed, typed relationships, both with properties. If you can draw it, you can store it.
- **Day 1:** Gremlin pipelines (`g.V`, `filter`, `out`/`in`/`both`, `outE`/`inV`, `groupCount`, `transform`, `dedup`, `back`); `addVertex`, `addEdge`, properties; Cypher patterns with ASCII art; custom steps like `varietal` and `friendsuggest`.
- **Day 2:** the REST API (nodes, relationships, paths), Lucene indexes to find starting nodes, Gremlin over REST; a big movie graph, Kevin Bacon paths with `loop`, centrality with `groupCount` and JUNG.
- **Day 3:** ACID transactions; HA master/slave clusters with ZooKeeper (eventually consistent, read-mostly); online backups; licensing.
- **Choose it when** relationships are the point of your data: social networks, recommendations, routes, permissions. **Avoid it** for huge datasets that must be sharded, or for big binary blobs.
:::

@@quiz
Q: What are the two building blocks of Neo4J's data model?
- Tables and rows
- Buckets and keys
+ Nodes and relationships, both of which can have properties
- Documents and collections
? Neo4J stores a property graph: nodes (things) connected by directed, typed relationships, with key-value properties on both.

Q: Why is "friends of friends" usually faster in a graph database than in SQL?
- Graph databases keep all data in memory
+ Each hop follows relationships from the current nodes only, while SQL performs a join across whole tables for every hop
- SQL cannot express friends of friends
- Graph databases cache every possible query
? A traversal's cost depends on the part of the graph it visits. A SQL self-join compares large sets of rows for every additional hop.

Q: In Gremlin, what does `g.V.filter{it.name=='Wine Expert Monthly'}.out.name` return?
- The magazine's name
- Every edge in the graph
+ The names of the nodes the magazine has outgoing relationships to (the wine it reported on)
- The number of vertices
? `out` is a shortcut for `outE.inV`: follow outgoing edges to the nodes they point at, then read their `name`.

Q: Which Gremlin step follows relationships regardless of direction?
- `out`
- `inV`
+ `both`
- `back`
? `out` follows outgoing edges, `in` incoming ones, and `both` either direction. That matters for symmetric relationships like friendship stored in one direction.

Q: What does this Cypher pattern find?
C: MATCH (ice_wine) -[:grape_type]-> () <-[:grape_type]- (similar)
- Wines with no grape type
- The grape type of the ice wine only
+ Other wines that share the ice wine's grape type
- Every relationship of type grape_type
? Both the ice wine and `similar` point to the same anonymous node `()` with `grape_type` relationships, so `similar` binds to wines of the same grape.

Q: Why do graph queries usually start with an index lookup?
- Indexes are required for every relationship
+ To find the starting node quickly; after that, the query walks relationships instead of scanning
- Indexes store the traversal results
- Because Cypher cannot read properties
? Scanning every node to find "P.G. Wodehouse" is slow. An index finds the start in one lookup; the rest of the query is a traversal.

Q: In the friendsuggest step, what does `except([start])` do?
+ Removes the starting person so Patty is not counted among her own friends' results
- Excludes wines Patty already likes
- Stops the traversal after one hop
- Deletes the start vertex
? `sideEffect{start = it}` remembers the person, and `both('friends')` could lead back to her, so `except` filters her out before following `likes`.

Q: How does the book's Gremlin search for a path from Elvis Presley to Kevin Bacon keep from running forever?
- It uses a full-text index
+ The `loop` closure stops when `it.loops` reaches a limit or the current node is Kevin Bacon
- Neo4J limits all traversals to two steps
- It deletes visited nodes
? `loop(1){ it.loops < 4 & !it.object.equals(bacon) }` repeats the `costars` step while both conditions hold, capping the depth at four degrees.

Q: In Neo4J's 1.x HA cluster, why can a read from a slave return slightly old data?
- Slaves do not store the graph
+ Slaves pull changes from the master on an interval, so they may lag behind recent writes
- The master deletes old writes
- ZooKeeper caches reads for an hour
? HA is eventually consistent across servers. Shortening `ha.pull_interval` reduces the lag but does not remove it, so HA is recommended for read-mostly workloads.

Q: Which statement about Neo4J and transactions is correct?
- Neo4J has no transactions, like most NoSQL databases
+ Neo4J is fully ACID, and Gremlin can group several changes into one manual transaction
- Transactions only work in the Community edition
- Transactions apply to nodes but not to relationships
? Neo4J supports ACID transactions. With `TransactionalGraph.Mode.MANUAL`, `startTransaction()` and `stopTransaction(SUCCESS or FAILURE)` group changes together.

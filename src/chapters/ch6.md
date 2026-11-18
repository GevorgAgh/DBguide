title: CouchDB
lead: A robust document database that speaks HTTP and replicates anywhere, from phones to data centers. Futon, cURL and revisions on Day 1; mapreduce views on Day 2; reducers, the Changes API and replication conflicts on Day 3.

## Overview: relaxing on the couch

CouchDB is the second document database in the book. Like MongoDB it stores **JSON documents** without a schema, but its priorities are different:

- **Robustness first.** CouchDB is written in **Erlang** and uses a **crash-only** design: its data files are append-only, so the server can be killed at any moment (power cut, crash, `kill -9`) and will start again with intact data. There is no "shutdown procedure".
- **HTTP all the way.** Every operation, including administration and replication, is a REST call. Any HTTP client is a CouchDB client; a browser can talk to it directly.
- **Replication anywhere.** Any two CouchDB databases can sync with each other, in either direction, even if they are only occasionally connected. The book says CouchDB targets everything from the **data center to the desktop to the smartphone**.
- **Queries are views.** You do not run ad hoc queries. You define **views**: JavaScript mapreduce functions whose results CouchDB stores as indexes and keeps up to date.

:::fig **CouchDB runs everywhere and syncs in every direction.** Each copy is a full, independent database that accepts reads and writes. Replication copies changes between any pair, whenever they can reach each other. This is master-master replication.
<svg class="dg" viewBox="0 0 720 240">
<rect x="270" y="20" width="180" height="70" rx="10" class="bg"/><text x="360" y="50" text-anchor="middle" class="b">data center</text><text x="360" y="70" text-anchor="middle" class="s">CouchDB cluster</text>
<rect x="60" y="150" width="160" height="70" rx="10" class="bg"/><text x="140" y="180" text-anchor="middle" class="b">laptop</text><text x="140" y="200" text-anchor="middle" class="s">CouchDB</text>
<rect x="500" y="150" width="160" height="70" rx="10" class="bg"/><text x="580" y="180" text-anchor="middle" class="b">phone</text><text x="580" y="200" text-anchor="middle" class="s">offline most of the day</text>
<line x1="290" y1="92" x2="180" y2="146" class="lgr" marker-end="url(#arrg)" marker-start="url(#arrg)"/>
<line x1="430" y1="92" x2="540" y2="146" class="lgr" marker-end="url(#arrg)" marker-start="url(#arrg)"/>
<line x1="224" y1="185" x2="496" y2="185" class="lgr dash" marker-end="url(#arrg)" marker-start="url(#arrg)"/>
<text x="360" y="176" text-anchor="middle" class="s">sync when connected</text>
<text x="225" y="112" text-anchor="end" class="s">replicate</text><text x="490" y="112" class="s">replicate</text>
</svg>
:::

:::analogy Git for data
Think of each CouchDB database as a Git repository. Every copy has the whole history it needs, you can work offline, and when copies meet they exchange changes. If two copies changed the same document, you get a conflict that someone has to resolve, exactly like a merge conflict.
:::

## Day 1 · CRUD, Futon and cURL redux

### Step 1: Futon, the web interface

CouchDB includes a web admin interface called **Futon**, at `http://localhost:5984/_utils/`. Through it you can create databases, create and edit documents, write views and start replication, all by clicking.

The book creates a database named **`music`** and a document for a band:

```json
{
  "_id": "74c7a8d2a8548c8b97da748f43000ac4",
  "_rev": "3-717cba2f1d9eb1fa2f07ae0f0fd7a5f1",
  "name": "The Beatles",
  "albums": [
    { "title": "Help!",               "year": 1965 },
    { "title": "Sgt. Pepper's Lonely Hearts Club Band", "year": 1967 },
    { "title": "Abbey Road",          "year": 1969 }
  ]
}
```

Two fields are special, and both start with an underscore:

| Field | Meaning |
|---|---|
| `_id` | The document's unique ID. CouchDB generates a UUID if you don't supply one. |
| `_rev` | The **revision**: a counter and a hash, like `3-717cba…`. It changes on every update. |

### Step 2: Revisions and MVCC

CouchDB never locks a document. Instead it uses **MVCC** (multi-version concurrency control): to update or delete a document, you must send the `_rev` you last read. If someone else updated it since, your `_rev` is out of date and CouchDB refuses with **409 Conflict**. You then re-read the document and try again.

:::fig **How `_rev` prevents lost updates.** Two clients read revision 1. Ann saves first and the document becomes revision 2. Bob's save still says "I am editing revision 1", so CouchDB rejects it instead of silently overwriting Ann's change. Bob must fetch revision 2 and reapply his edit.
<svg class="dg wide" viewBox="0 0 720 240">
<text x="10" y="54" class="b">Ann</text><text x="10" y="134" class="b tg">CouchDB</text><text x="10" y="214" class="b">Bob</text>
<line x1="90" y1="50" x2="710" y2="50" class="ln2"/><line x1="90" y1="130" x2="710" y2="130" class="lgr"/><line x1="90" y1="210" x2="710" y2="210" class="ln2"/>
<rect x="100" y="110" width="110" height="40" rx="8" class="bg"/><text x="155" y="135" text-anchor="middle" class="mono s">rev 1-aaa</text>
<line x1="170" y1="108" x2="210" y2="60" class="ln dash" marker-end="url(#arr)"/><line x1="170" y1="152" x2="210" y2="200" class="ln dash" marker-end="url(#arr)"/>
<text x="196" y="88" class="s">GET</text><text x="196" y="180" class="s">GET</text>
<rect x="250" y="30" width="150" height="40" rx="8" class="box"/><text x="325" y="55" text-anchor="middle" class="mono s">PUT, _rev 1-aaa</text>
<line x1="330" y1="72" x2="380" y2="108" class="lgr" marker-end="url(#arrg)"/>
<rect x="386" y="110" width="110" height="40" rx="8" class="bg"/><text x="441" y="135" text-anchor="middle" class="mono s">rev 2-bbb</text>
<text x="300" y="98" class="s tg">201 Created</text>
<rect x="470" y="190" width="150" height="40" rx="8" class="box"/><text x="545" y="215" text-anchor="middle" class="mono s">PUT, _rev 1-aaa</text>
<line x1="540" y1="188" x2="520" y2="156" class="lr" marker-end="url(#arrr)"/>
<text x="560" y="168" class="s tr b">409 Conflict</text><text x="560" y="184" class="s">rev 1 is stale</text>
</svg>
:::

:::deep Append-only storage
CouchDB's file is a **B-tree that is only ever appended to**. An update never overwrites the old bytes; it writes the new version (and the changed B-tree nodes) at the end of the file, then a new header pointing to them. If the server dies mid-write, the old header still points to a complete, consistent tree. That is why CouchDB is so hard to corrupt and why it needs no recovery procedure. The price: the file grows, so you occasionally run **compaction**, which copies only the live data into a fresh file.
:::

### Step 3: CRUD with cURL

Futon is just a client of CouchDB's REST API, and so is `curl`. The server listens on port **5984**:

```bash
curl http://localhost:5984/
# {"couchdb":"Welcome","version":"1.1.1"}

curl http://localhost:5984/music/
# {"db_name":"music","doc_count":1,"doc_del_count":0,"update_seq":4, ...}

curl http://localhost:5984/music/74c7a8d2a8548c8b97da748f43000ac4
# the Beatles document, with its _id and _rev
```

**Create** with POST (CouchDB picks the ID):

```bash
curl -i -X POST "http://localhost:5984/music/" \
  -H "Content-Type: application/json" \
  -d '{ "name": "Wings" }'
# HTTP/1.1 201 Created
# Location: http://localhost:5984/music/2ac58771c197f70461056f7c7e00c0f9
# {"ok":true,"id":"2ac58771c197f70461056f7c7e00c0f9","rev":"1-2fe1dd1911153eb9df8460747dfe75a0"}
```

**Update** with PUT, sending the current `_rev` in the body (or in an `If-Match` header). A PUT replaces the whole document:

```bash
curl -i -X PUT "http://localhost:5984/music/2ac58771c197f70461056f7c7e00c0f9" \
  -H "Content-Type: application/json" \
  -d '{
    "_id": "2ac58771c197f70461056f7c7e00c0f9",
    "_rev": "1-2fe1dd1911153eb9df8460747dfe75a0",
    "name": "Wings",
    "albums": ["Wild Life", "Band on the Run", "London Town"]
  }'
# {"ok":true,"id":"2ac58771…","rev":"2-17e4ce41cd33d6a38f04a8452d5a860b"}
```

**Delete** with DELETE, again naming the current revision:

```bash
curl -i -X DELETE "http://localhost:5984/music/2ac58771c197f70461056f7c7e00c0f9" \
  -H "If-Match: 2-17e4ce41cd33d6a38f04a8452d5a860b"
# {"ok":true,"id":"2ac58771…","rev":"3-42aafb7411c092614ce7c9f4ab79dc8b"}
```

A deleted document is not erased: CouchDB stores a new revision marked as deleted (a "tombstone"), so the deletion can replicate to other copies.

| Operation | HTTP | Notes |
|---|---|---|
| Create, ID chosen by CouchDB | `POST /db/` | Returns `id` and `rev`. |
| Create or update, ID chosen by you | `PUT /db/id` | Updates must include the current `_rev`. |
| Read | `GET /db/id` | `?rev=…` fetches an older revision (until compaction). |
| Delete | `DELETE /db/id` | Needs `?rev=…` or `If-Match`. |
| List everything | `GET /db/_all_docs` | Add `?include_docs=true` for full documents. |

### Day 1 homework, solved

**Find:** the HTTP Document API is in the CouchDB docs. Besides GET, POST, PUT and DELETE, CouchDB supports **HEAD** (headers only, a cheap way to get the current `_rev` via the `ETag`) and **COPY** (duplicate a document to a new ID).

```bash
# 1. PUT a document with your own _id
curl -X PUT http://localhost:5984/music/the-kinks \
  -H "Content-Type: application/json" -d '{"name": "The Kinks"}'

# 2. create and then delete a database
curl -X PUT    http://localhost:5984/scratch
curl -X DELETE http://localhost:5984/scratch

# 3. a document with a text attachment, then fetch just the attachment
curl -X PUT http://localhost:5984/music/notes -H "Content-Type: application/json" -d '{}'
#   -> {"ok":true,"id":"notes","rev":"1-967a00dff5e02add41819138abb3284d"}
curl -X PUT "http://localhost:5984/music/notes/readme.txt?rev=1-967a00dff5e02add41819138abb3284d" \
  -H "Content-Type: text/plain" --data-binary @readme.txt
curl http://localhost:5984/music/notes/readme.txt
```

Attachments live at `/db/docid/attachment-name` and are stored, revised and replicated together with their document.

## Day 2 · Creating and querying views

In CouchDB you do not search documents directly. You build a **view**, which is the output of a **map function** run over every document, stored as a **sorted index** of key/value pairs. You then query the view by key or by key range.

### Step 1: The simplest views

In Futon you can try a **temporary view**. The map function receives each document and calls `emit(key, value)` zero or more times:

```javascript
function(doc) {
  emit(null, doc);
}
```

This emits one row per document, with key `null` and the whole document as the value. More useful: emit the ID with the revision.

```javascript
function(doc) {
  emit(doc._id, { rev: doc._rev });
}
```

That is essentially what the built-in **`_all_docs`** view does:

```bash
curl http://localhost:5984/music/_all_docs
curl http://localhost:5984/music/_all_docs?include_docs=true
```

:::warn Temporary views are slow
A temporary view runs the map function over **every document, every time** you query it. Fine for experimenting with a handful of documents, terrible for production. Save views in a design document instead (next step) so CouchDB builds the index once and then keeps it updated.
:::

### Step 2: Design documents and saved views

Saved views live in a **design document**: a special document whose ID starts with `_design/`. Like any document it can be created through Futon or a PUT, and it **replicates** with the database, so your queries travel with your data.

```javascript
// _design/artists, view "by_name"
function(doc) {
  if ('name' in doc) {
    emit(doc.name, doc._id);
  }
}
```

```javascript
// _design/albums, view "by_name": one row per album
function(doc) {
  if ('name' in doc && 'albums' in doc) {
    doc.albums.forEach(function(album){
      var
        key = album.title || album.name,
        value = { by: doc.name, album: album };
      emit(key, value);
    });
  }
}
```

The `if` checks are important: in a schemaless database, a map function must not assume a field exists.

```bash
curl http://localhost:5984/music/_design/artists/_view/by_name
curl http://localhost:5984/music/_design/albums/_view/by_name
curl 'http://localhost:5984/music/_design/albums/_view/by_name?key="Help!"'
# {"total_rows":3,"offset":0,"rows":[
#   {"id":"74c7a8d2…","key":"Help!","value":{"by":"The Beatles","album":{"title":"Help!","year":1965}}}
# ]}
```

:::fig **How a view works.** The map function runs once per document and emits key/value rows. CouchDB stores the rows in a B-tree **sorted by key**, so finding one key or a range of keys is fast. When documents change, only the changed documents are re-mapped, the next time the view is queried.
<svg class="dg wide" viewBox="0 0 720 260">
<text x="90" y="20" text-anchor="middle" class="b">documents</text>
<rect x="10" y="34" width="160" height="50" rx="8" class="bg"/><text x="20" y="56" class="mono s">The Beatles</text><text x="20" y="74" class="mono s">albums: Help!, …</text>
<rect x="10" y="96" width="160" height="50" rx="8" class="bg"/><text x="20" y="118" class="mono s">Wings</text><text x="20" y="136" class="mono s">albums: Wild Life, …</text>
<rect x="10" y="158" width="160" height="50" rx="8" class="bg"/><text x="20" y="180" class="mono s">Cream</text><text x="20" y="198" class="mono s">albums: Disraeli…</text>
<rect x="210" y="96" width="120" height="50" rx="8" class="bv"/><text x="270" y="118" text-anchor="middle" class="b">map()</text><text x="270" y="136" text-anchor="middle" class="s">emit per album</text>
<line x1="172" y1="59" x2="208" y2="110" class="ln" marker-end="url(#arr)"/><line x1="172" y1="121" x2="208" y2="121" class="ln" marker-end="url(#arr)"/><line x1="172" y1="183" x2="208" y2="132" class="ln" marker-end="url(#arr)"/>
<line x1="332" y1="121" x2="368" y2="121" class="ln" marker-end="url(#arr)"/>
<text x="540" y="20" text-anchor="middle" class="b">view index, sorted by key</text>
<rect x="372" y="34" width="338" height="200" rx="8" class="ba"/>
<g class="mono s">
<text x="384" y="58" class="b">key</text><text x="560" y="58" class="b">value</text>
<text x="384" y="84">"Abbey Road"</text><text x="560" y="84">by: Beatles</text>
<text x="384" y="108">"Band on the Run"</text><text x="560" y="108">by: Wings</text>
<text x="384" y="132">"Disraeli Gears"</text><text x="560" y="132">by: Cream</text>
<text x="384" y="156" class="ta b">"Help!"</text><text x="560" y="156" class="ta b">by: Beatles</text>
<text x="384" y="180">"London Town"</text><text x="560" y="180">by: Wings</text>
<text x="384" y="204">"Wild Life"</text><text x="560" y="204">by: Wings</text>
</g>
<text x="540" y="252" text-anchor="middle" class="s">?key="Help!" jumps straight to its row</text>
</svg>
:::

### Step 3: Importing real data

A few bands are not enough to see views shine, so the book imports a database dump from **Jamendo** (a free-music site): thousands of artists, each with albums, tracks and tags. The Ruby script uses `libxml-ruby` to parse the huge XML file as a **stream** (SAX style, like the HBase Wikipedia import) and the **couchrest** gem to save each artist as one CouchDB document:

```bash
gem install libxml-ruby couchrest
zcat dbdump_artistalbumtrack.xml.gz | ruby import_from_jamendo.rb
```

Each artist document nests albums, which nest tracks, which nest tags, and the script adds a `random` number property to every artist, album, track and tag (used in the homework).

### Step 4: Querying views with parameters

| Parameter | Effect |
|---|---|
| `key="X"` | Only rows with exactly this key. |
| `startkey="A"` / `endkey="B"` | Rows in this key range (inclusive). |
| `limit=5` | At most 5 rows. |
| `skip=10` | Skip the first 10 rows. |
| `descending=true` | Walk the index backwards. |
| `include_docs=true` | Include each row's full document. |
| `reduce=false` / `group=true` | Control reduce functions (Day 3). |

```bash
# the first five artists
curl 'http://localhost:5984/music/_design/artists/_view/by_name?limit=5'

# artists whose names start with C (keys from "C" up to "D")
curl 'http://localhost:5984/music/_design/artists/_view/by_name?startkey=%22C%22&endkey=%22D%22&limit=5'

# the same range backwards: note that start and end swap!
curl 'http://localhost:5984/music/_design/artists/_view/by_name?startkey=%22D%22&endkey=%22C%22&descending=true&limit=5'
```

`%22` is a URL-encoded double quote: keys are JSON, so string keys must be quoted.

:::fig **Range queries on a sorted index.** `startkey` and `endkey` select a slice of the sorted keys. With `descending=true` CouchDB walks backwards, so the start key must be the larger one: `startkey="D"`, `endkey="C"`.
<svg class="dg wide" viewBox="0 0 720 180">
<g class="mono s">
<rect x="10" y="60" width="96" height="40" rx="6" class="box"/><text x="58" y="85" text-anchor="middle">"Bjork"</text>
<rect x="110" y="60" width="96" height="40" rx="6" class="ba"/><text x="158" y="85" text-anchor="middle">"Cake"</text>
<rect x="210" y="60" width="96" height="40" rx="6" class="ba"/><text x="258" y="85" text-anchor="middle">"Can"</text>
<rect x="310" y="60" width="96" height="40" rx="6" class="ba"/><text x="358" y="85" text-anchor="middle">"Cream"</text>
<rect x="410" y="60" width="96" height="40" rx="6" class="ba"/><text x="458" y="85" text-anchor="middle">"Cure"</text>
<rect x="510" y="60" width="96" height="40" rx="6" class="box"/><text x="558" y="85" text-anchor="middle">"Daft Punk"</text>
<rect x="610" y="60" width="96" height="40" rx="6" class="box"/><text x="658" y="85" text-anchor="middle">"Doors"</text>
</g>
<line x1="110" y1="40" x2="506" y2="40" class="la" marker-end="url(#arra)"/>
<text x="110" y="30" class="s ta b">startkey="C"</text><text x="506" y="30" text-anchor="end" class="s ta b">endkey="D"</text>
<line x1="506" y1="124" x2="110" y2="124" class="lw" marker-end="url(#arrw)"/>
<text x="506" y="146" text-anchor="end" class="s tw b">startkey="D"</text><text x="110" y="146" class="s tw b">endkey="C"</text>
<text x="308" y="170" text-anchor="middle" class="s">descending=true walks the same slice backwards</text>
</svg>
:::

:::deep Keys don't have to be strings
`emit()` keys can be any JSON: numbers, strings, arrays, objects, `null`. CouchDB sorts them by a fixed **collation** order: `null`, then `false`, `true`, numbers, strings, arrays, objects. **Array keys** sort element by element, which makes them powerful. Emit `[artist, year]` and then `startkey=["Cream"]&endkey=["Cream",{}]` returns all of Cream's albums sorted by year (`{}` sorts after everything, so it acts as "the end").
:::

### Day 2 homework, solved

**Find:** keys may be any JSON value (see the box above). Useful URL parameters are listed in the table in Step 4, plus `inclusive_end`, `stale=ok` (return the current index without updating it) and `group_level`.

**1. A view keyed by the random number:**

```javascript
// _design/random, view "artist"
function(doc) {
  if ('name' in doc && 'random' in doc) {
    emit(doc.random, doc.name);
  }
}
```

**2. Fetch a random artist.** Pick a random number between 0 and 1, start the view there, and take one row:

```bash
curl "http://localhost:5984/music/_design/random/_view/artist?limit=1&startkey=$(ruby -e 'puts rand')"
```

(If the random number is larger than every key you get no rows; a robust client then retries with `descending=true`.)

**3. Views for albums, tracks and tags**, in the same design document:

```javascript
// view "album"
function(doc) {
  if ('albums' in doc) {
    doc.albums.forEach(function(album){
      if ('name' in album && 'random' in album) { emit(album.random, album.name); }
    });
  }
}

// view "track"
function(doc) {
  (doc.albums || []).forEach(function(album){
    (album.tracks || []).forEach(function(track){
      if ('name' in track && 'random' in track) { emit(track.random, track.name); }
    });
  });
}

// view "tag"
function(doc) {
  (doc.albums || []).forEach(function(album){
    (album.tracks || []).forEach(function(track){
      (track.tags || []).forEach(function(tag){
        if ('idstr' in tag && 'random' in tag) { emit(tag.random, tag.idstr); }
      });
    });
  });
}
```

## Day 3 · Advanced views, the Changes API and replicating data

### Step 1: Reduce functions

A view can have a **reduce** function too, which summarizes the mapped rows. The book counts how often each **tag** is used across all tracks:

```javascript
// _design/tags, view "by_name": map
function(doc) {
  (doc.albums || []).forEach(function(album){
    (album.tracks || []).forEach(function(track){
      (track.tags || []).forEach(function(tag){
        emit(tag.idstr, 1);
      });
    });
  });
}

// reduce
function(key, values, rereduce) {
  return sum(values);
}
```

The book runs this view in Futon. With reducing off, every tag use is its own row with value 1 (`"17sonsrecords" 1` five times, `"acid" 1`, `"acousticguitar" 1` twice…). Tick Futon's **Reduce** box and the rows collapse into one count per tag:

```text
Key                 Value
"17sonsrecords"     5
"acid"              1
"acousticguitar"    2
"action"            2
"adventure"         3
```

Over HTTP, the same three views of the data look like this:

```bash
curl 'http://localhost:5984/music/_design/tags/_view/by_name'
# one row with key null: the grand total of all tag uses

curl 'http://localhost:5984/music/_design/tags/_view/by_name?group=true&limit=5'
# one row per tag, as in the table above

curl 'http://localhost:5984/music/_design/tags/_view/by_name?reduce=false&limit=5'
# the raw mapped rows, no reducing
```

Without `group=true`, CouchDB reduces **everything** into one value. With it, CouchDB reduces **per key**, which is what we want.

:::fig **Reduce and rereduce.** CouchDB stores partial reduce results inside the B-tree nodes of the view. A query combines the stored partial results (`rereduce = true`) instead of recomputing from every row, which is why reduced views stay fast as data grows.
<svg class="dg wide" viewBox="0 0 720 260">
<g class="mono s">
<rect x="10" y="190" width="110" height="34" rx="5" class="box"/><text x="65" y="212" text-anchor="middle">acid, 1</text>
<rect x="130" y="190" width="110" height="34" rx="5" class="box"/><text x="185" y="212" text-anchor="middle">acid, 1</text>
<rect x="250" y="190" width="110" height="34" rx="5" class="box"/><text x="305" y="212" text-anchor="middle">acid, 1</text>
<rect x="370" y="190" width="110" height="34" rx="5" class="box"/><text x="425" y="212" text-anchor="middle">rock, 1</text>
<rect x="490" y="190" width="110" height="34" rx="5" class="box"/><text x="545" y="212" text-anchor="middle">rock, 1</text>
<rect x="610" y="190" width="100" height="34" rx="5" class="box"/><text x="660" y="212" text-anchor="middle">rock, 1</text>
</g>
<rect x="90" y="110" width="170" height="44" rx="8" class="bv"/><text x="175" y="130" text-anchor="middle" class="s">reduce(…, false)</text><text x="175" y="146" text-anchor="middle" class="mono s">acid: 3</text>
<rect x="450" y="110" width="170" height="44" rx="8" class="bv"/><text x="535" y="130" text-anchor="middle" class="s">reduce(…, false)</text><text x="535" y="146" text-anchor="middle" class="mono s">rock: 3</text>
<line x1="65" y1="188" x2="140" y2="156" class="ln2"/><line x1="185" y1="188" x2="175" y2="156" class="ln2"/><line x1="305" y1="188" x2="210" y2="156" class="ln2"/>
<line x1="425" y1="188" x2="500" y2="156" class="ln2"/><line x1="545" y1="188" x2="535" y2="156" class="ln2"/><line x1="660" y1="188" x2="570" y2="156" class="ln2"/>
<rect x="270" y="24" width="180" height="50" rx="8" class="bg"/><text x="360" y="44" text-anchor="middle" class="s">reduce(…, rereduce=true)</text><text x="360" y="62" text-anchor="middle" class="mono s">total: 6</text>
<line x1="175" y1="108" x2="320" y2="76" class="ln" marker-end="url(#arr)"/><line x1="535" y1="108" x2="400" y2="76" class="ln" marker-end="url(#arr)"/>
<text x="10" y="250" class="s">mapped rows (leaf level)</text>
<text x="470" y="40" class="s">no group: one grand total</text>
<text x="470" y="58" class="s">group=true: one value per key</text>
</svg>
:::

The third argument, `rereduce`, tells your function which situation it is in: `false` means `values` are values emitted by map; `true` means `values` are earlier reduce results. For a sum it makes no difference. For other summaries (counting distinct items, averages) you must handle both cases.

:::tip Use the built-in reducers
CouchDB has native reducers written in Erlang: `_sum`, `_count` and `_stats` (sum, count, min, max and sum of squares). Write `"reduce": "_sum"` instead of a JavaScript function. They are much faster, because the data never has to be passed to the JavaScript engine.
:::

### Step 2: The Changes API

Every change to a database gets a **sequence number**. The **`_changes`** feed lists them in order, so applications can watch the database and react: update a search index, send notifications, sync a mobile client.

```bash
curl http://localhost:5984/music/_changes
# {"results":[ {"seq":1, ...}, ..., {"seq":100,"id":"357995","changes":[{"rev":"1-aa649aa53f…"}]} ],
#  "last_seq":100}

curl http://localhost:5984/music/_changes?since=99       # only what happened after seq 99
# {"results":[{"seq":100,"id":"357995","changes":[{"rev":"1-aa649aa53f…"}]}],
#  "last_seq":100}

curl http://localhost:5984/music/_changes?since=9000     # past the end: empty results
```

There are three ways to follow the feed:

| `feed=` | Behavior |
|---|---|
| `normal` (default) | Return what has changed since `since`, then close. You poll again later. |
| `longpoll` | If nothing has changed yet, **hold the connection open** until something does, then return and close. |
| `continuous` | Keep the connection open forever, streaming one line of JSON per change as it happens. |

:::fig **Three ways to watch for changes.** Normal polling wastes requests when nothing happens and adds delay when something does. Long polling waits on the server and answers the moment a change arrives. A continuous feed keeps one connection open and streams every change.
<svg class="dg wide" viewBox="0 0 720 250">
<text x="10" y="40" class="b">normal</text>
<line x1="110" y1="36" x2="700" y2="36" class="ln2"/>
<g class="fm"><circle cx="150" cy="36" r="5"/><circle cx="250" cy="36" r="5"/><circle cx="350" cy="36" r="5"/><circle cx="550" cy="36" r="5"/><circle cx="650" cy="36" r="5"/></g>
<circle cx="450" cy="36" r="6" class="fg"/>
<text x="400" y="62" class="s">poll every few seconds: most requests return nothing</text>
<text x="10" y="120" class="b">longpoll</text>
<line x1="110" y1="116" x2="700" y2="116" class="ln2"/>
<rect x="150" y="106" width="270" height="20" rx="10" class="bw"/>
<circle cx="420" cy="116" r="6" class="fg"/>
<rect x="430" y="106" width="200" height="20" rx="10" class="bw"/>
<text x="285" y="146" text-anchor="middle" class="s">request held open…</text><text x="420" y="146" class="s">change → reply, reconnect</text>
<text x="10" y="200" class="b">continuous</text>
<line x1="110" y1="196" x2="700" y2="196" class="ln2"/>
<rect x="150" y="186" width="550" height="20" rx="10" class="bg" fill-opacity="0.5"/>
<g class="fg"><circle cx="300" cy="196" r="6"/><circle cx="420" cy="196" r="6"/><circle cx="460" cy="196" r="6"/><circle cx="610" cy="196" r="6"/></g>
<text x="420" y="230" text-anchor="middle" class="s">one connection, one line per change, as it happens</text>
</svg>
:::

```bash
curl 'http://localhost:5984/music/_changes?feed=longpoll&since=9000'   # waits for a change…
curl 'http://localhost:5984/music/_changes?since=97&feed=continuous'   # streams changes as they come
# {"seq":98,"id":"357999","changes":[{"rev":"1-0329f5c885…"}]}
# {"seq":99,"id":"357998","changes":[{"rev":"1-79c3fd2fe6…"}]}
# {"seq":100,"id":"357995","changes":[{"rev":"1-aa649aa53f…"}]}
# … and if nothing happens for a while, CouchDB closes with {"last_seq":100}
```

#### Watching changes with Node.js

To build a real watcher, the book uses **Node.js**, whose non-blocking, event-driven style suits a client that waits on long-polling HTTP requests. The watcher is an `EventEmitter`: it makes a long-poll request, emits a `change` event for each result, remembers the last sequence number, and immediately starts the next request.

```javascript
var http = require('http'), events = require('events');

exports.createWatcher = function(options) {
  var watcher = new events.EventEmitter();
  watcher.host = options.host || 'localhost';
  watcher.port = options.port || 5984;
  watcher.last_seq = options.last_seq || 0;
  watcher.db = options.db || '_users';

  watcher.start = function() {
    var path = '/' + watcher.db + '/_changes?feed=longpoll&since=' + watcher.last_seq;
    http.get({ host: watcher.host, port: watcher.port, path: path }, function(res) {
      var buffer = '';
      res.on('data', function(chunk) { buffer += chunk; });
      res.on('end', function() {
        var output = JSON.parse(buffer);
        if (output.results) {
          watcher.last_seq = output.last_seq;
          output.results.forEach(function(change){ watcher.emit('change', change); });
          watcher.start();                   // immediately wait for the next batch
        } else {
          watcher.emit('error', output);
        }
      });
    }).on('error', function(err) { watcher.emit('error', err); });
  };
  return watcher;
};

// usage
var watcher = exports.createWatcher({ db: process.argv[2] || 'music' });
watcher.on('change', function(change) { console.log(JSON.stringify(change)); })
       .on('error', console.error)
       .start();
```

```bash
node watch_changes_longpolling.js music
```

#### Filtering the feed on the server

A **filter function**, saved in a design document, lets the server send only the changes you care about. It receives the document and the request (so you can pass parameters):

```javascript
// _design/wherabouts, filters: "by_country"
function(doc, req) {
  return doc.country === req.query.country;
}
```

```bash
curl -X PUT http://localhost:5984/music/_design/wherabouts \
  -H "Content-Type: application/json" \
  -d '{"language":"javascript","filters":{"by_country":
       "function(doc,req){return doc.country === req.query.country;}"}}'

curl "http://localhost:5984/music/_changes?filter=wherabouts/by_country&country=RUS"
```

### Step 3: Replication and conflicts

Replication copies every change from a **source** database to a **target** database; the target can be on the same server or across the world. The book starts it from Futon's **Replicator** page (Tools menu): create an empty `music-repl` database, choose `music` as the source and `music-repl` as the target, and click **Replicate**. Under the hood that is one HTTP request, which you can also send yourself:

```bash
curl -X PUT http://localhost:5984/music-repl
curl -X POST http://localhost:5984/_replicate \
  -H "Content-Type: application/json" \
  -d '{"source":"music","target":"music-repl"}'
```

Because both copies accept writes, the same document can change on both sides before they sync. The book creates exactly that conflict:

1. Create a document `theconflicts` (`{"name": "The Conflicts"}`, revision `1-e007…`) in `music` and replicate it to `music-repl`.
2. In `music-repl`, add an album "Conflicts of Interest" (it becomes revision `2-0c969f…`).
3. In `music`, add a different album, "Conflicting Opinions" (revision `2-cab47b…`). Both revision 2s come from the same revision 1.
4. Replicate from `music` to `music-repl` again. It succeeds, which surprises many people.

```bash
curl http://localhost:5984/music-repl/theconflicts?conflicts=true
# {"_id":"theconflicts","_rev":"2-cab47bf4444a20d6a2d2204330fdce2a",
#  "name":"The Conflicts","albums":["Conflicting Opinions"],
#  "_conflicts":["2-0c969fbfa76eb7fcdf6412ef219fcac5"]}

curl http://localhost:5984/music-repl/theconflicts?rev=2-0c969fbfa76eb7fcdf6412ef219fcac5
# {"_id":"theconflicts","_rev":"2-0c969f…","name":"The Conflicts",
#  "albums":["Conflicts of Interest"]}
```

:::fig **A replication conflict.** Both copies started from revision 1 and changed it independently. After replication, the target holds both revision 2s. CouchDB picks a winner with a deterministic rule, so every replica picks the same one, and lists the loser in `_conflicts` for your application to resolve.
<svg class="dg wide" viewBox="0 0 720 240">
<rect x="10" y="100" width="110" height="44" rx="8" class="bg"/><text x="65" y="127" text-anchor="middle" class="mono s">1-e007…</text>
<line x1="122" y1="114" x2="210" y2="60" class="ln" marker-end="url(#arr)"/><line x1="122" y1="130" x2="210" y2="184" class="ln" marker-end="url(#arr)"/>
<rect x="214" y="36" width="170" height="48" rx="8" class="ba"/><text x="299" y="56" text-anchor="middle" class="b">in music</text><text x="299" y="74" text-anchor="middle" class="mono s">2-cab4… Opinions</text>
<rect x="214" y="160" width="170" height="48" rx="8" class="bw"/><text x="299" y="180" text-anchor="middle" class="b">in music-repl</text><text x="299" y="198" text-anchor="middle" class="mono s">2-0c96… Interest</text>
<line x1="386" y1="60" x2="470" y2="108" class="ln" marker-end="url(#arr)"/><line x1="386" y1="184" x2="470" y2="136" class="ln" marker-end="url(#arr)"/>
<text x="420" y="210" class="s">replicate</text>
<rect x="474" y="80" width="236" height="84" rx="10" class="br"/>
<text x="592" y="102" text-anchor="middle" class="b">music-repl after sync</text>
<text x="486" y="124" class="mono s">_rev: 2-cab4… (winner)</text>
<text x="486" y="144" class="mono s">_conflicts: [2-0c96…]</text>
<text x="592" y="196" text-anchor="middle" class="s">same winner on every replica;</text>
<text x="592" y="212" text-anchor="middle" class="s">loser kept, not lost</text>
</svg>
:::

Important details:

- CouchDB **never throws away** a conflicting revision silently. It picks a **deterministic winner** (based on revision history length and then a comparison of revision IDs), so every replica shows the same "current" version, and keeps the loser available.
- You can fetch the losing version with `?rev=2-0c969fbf…`.
- **Resolving** is up to your application: merge the two versions into a new revision, then **delete** the losing revision (`DELETE …?rev=2-0c969fbf…`). Once only one leaf remains, the conflict is gone.

### Day 3 homework, solved

**Find:**
1. **Native reducers:** `_sum`, `_count`, `_stats` (and `_approx_count_distinct` in later versions). They run in Erlang, avoiding the cost of serializing data to the JavaScript process.
2. **Server-side filtering of `_changes`:** filter functions in a design document, used with `?filter=ddoc/name` (or the built-ins `filter=_doc_ids` and `filter=_view`).
3. **Replication over REST:** start with `POST /_replicate {"source": …, "target": …}`; add `"continuous": true` to keep it running; cancel by posting the same body with `"cancel": true`.
4. **Persistent replication:** write a document into the special **`_replicator`** database; CouchDB starts the replication and restarts it after reboots, until you delete the document:

```bash
curl -X POST http://localhost:5984/_replicator \
  -H "Content-Type: application/json" \
  -d '{"_id":"music-to-repl", "source":"music", "target":"music-repl", "continuous":true}'
```

**Do 1–2. A continuous-feed watcher.** With `feed=continuous` the response never ends. Each change arrives as one line of JSON, so we split the stream on newlines instead of waiting for the end:

```javascript
watcher.start = function() {
  var path = '/' + watcher.db + '/_changes?feed=continuous&since=' + watcher.last_seq;
  http.get({ host: watcher.host, port: watcher.port, path: path }, function(res) {
    var buffer = '';
    res.on('data', function(chunk) {
      buffer += chunk;
      var lines = buffer.split('\n');
      buffer = lines.pop();                     // keep any incomplete last line
      lines.forEach(function(line) {
        if (!line.trim()) return;               // CouchDB sends blank heartbeat lines
        var change = JSON.parse(line);
        if (change.seq) { watcher.last_seq = change.seq; watcher.emit('change', change); }
      });
    });
    res.on('end', function() { watcher.start(); });   // reconnect if the server closes it
  }).on('error', function(err) { watcher.emit('error', err); });
};
```

**Do 3. A view of conflicting revisions:**

```javascript
// _design/conflicts, view "by_rev"
function(doc) {
  if (doc._conflicts) {
    doc._conflicts.forEach(function(rev) {
      emit(rev, doc._id);
    });
  }
}
```

## Wrap-up · Strengths and weaknesses

### Strengths

- **Robust and stable.** Built on the assumption that networks are unreliable and hardware will fail, CouchDB takes a thoroughly **decentralized** approach to storing data.
- **Small enough for a phone, big enough for an enterprise.** It fits many deployment situations.
- **As much an API as a database.** Because everything is plain HTTP and JSON, you can put standard web tools in front of it (load balancers, caching proxies) and alternative implementations can offer the same API.

### Weaknesses

- **Views are not ad hoc queries.** Mapreduce views cannot slice data as freely as SQL, and you should not run temporary (ad hoc) views in production at all.
- **Replication is all or nothing.** Every replica holds the full database. The 2012 CouchDB had **no sharding**: more nodes increase read/write throughput, not total capacity (BigCouch, an add-on, offered sharding).

### Parting thoughts

CouchDB's attention to robustness under uncertainty makes it a great choice if your system must survive **the harsh realities of the wild Internet**: flaky networks, offline devices, crashing machines. Because it speaks HTTP and JSON, it fits wherever web technologies are used. Inside a data center it can still make sense, if you commit to handling conflicts when they arise or choose a sharding implementation like BigCouch.

:::modern CouchDB in 2026
- **Clustering is built in.** CouchDB 2.0 (2016) merged in BigCouch, so databases are now split into shards (`q`) and replicated across nodes (`n`) inside one cluster, on top of the replication between clusters you learned here.
- **Fauxton replaced Futon** as the web interface (still at `/_utils`).
- **Mango queries:** since 2.0, `POST /db/_find` accepts MongoDB-style JSON queries (`{"selector": {"year": {"$gt": 1965}}}`) backed by `_index` indexes. Temporary views were removed.
- **Security by default:** CouchDB 3.0 (2020) requires an admin account and no longer starts in "admin party" mode where anyone could do anything.
- **Offline-first lives on.** **PouchDB**, a JavaScript database that runs in the browser and syncs with CouchDB using this replication protocol, is popular for apps that must work offline. IBM Cloudant is a managed CouchDB-compatible service.
- **Not to be confused with Couchbase**, a different product that grew out of a merger between Membase and part of the early CouchDB team.
- In Node.js, `http.createClient` (used by the book's original code) was removed; the examples above use `http.get`.
:::

:::key Chapter 6 in a nutshell
- **Model:** JSON documents with `_id` and `_rev`, stored in an append-only, crash-safe B-tree; everything is REST over HTTP on port 5984.
- **Day 1:** Futon and cURL CRUD; updates and deletes must send the current `_rev` (MVCC); a stale revision gets **409 Conflict**.
- **Day 2:** views are map functions saved in **design documents**; results are a sorted index queried by `key`, `startkey`/`endkey`, `limit`, `descending`; keys can be arrays.
- **Day 3:** reduce functions (`group=true`, `rereduce`, built-ins `_sum`/`_count`/`_stats`); the `_changes` feed (normal, longpoll, continuous) and filters; master-master replication with deterministic conflict winners and `_conflicts`.
- **Choose it when** data must sync across unreliable networks and devices, and robustness matters more than ad hoc querying.
:::

@@quiz
Q: You try to update a CouchDB document with a `_rev` that is no longer the latest. What happens?
- CouchDB merges your changes automatically
- Your update overwrites the newer version
+ CouchDB rejects the update with 409 Conflict; you must re-read the document and try again
- CouchDB stores your update as a new document
? CouchDB uses MVCC instead of locks. An update must name the revision it is based on; if that revision is stale, it is refused so no change is lost.

Q: Why can CouchDB survive being killed at any moment without corrupting its data?
- It writes every change to three disks at once
+ Its file is append-only: new versions are written at the end and the old consistent tree remains valid until a new header points past it
- It keeps all data in memory
- It runs a repair tool on every startup
? This "crash-only" design never overwrites data in place, so an interrupted write cannot damage what was already there.

Q: Which HTTP request deletes a CouchDB document?
- `DELETE /music/docid` with no other information
+ `DELETE /music/docid` with the current revision, as `?rev=…` or an `If-Match` header
- `POST /music/_delete {"id": "docid"}`
- `PUT /music/docid {"deleted": true}` with no revision
? Deleting is a change like any other, so it must name the current revision. CouchDB then stores a deletion marker (tombstone) that can replicate.

Q: Why is a map function in a design document better than a temporary view for production?
- Temporary views cannot use JavaScript
+ A saved view is built once into a stored, sorted index and updated incrementally, while a temporary view re-runs the map over every document on every query
- Design documents are encrypted
- Temporary views only return one row
? Saved views are persistent B-tree indexes. Temporary views are fine for experiments but scan the whole database each time.

Q: What does this query return?
C: /music/_design/artists/_view/by_name?startkey="C"&endkey="D"
- Only the artist named "C"
+ Rows whose keys sort between "C" and "D", that is, artist names starting with C
- The first two artists
- Nothing, because the parameters must be numbers
? View rows are sorted by key, so startkey and endkey select a slice of the index.

Q: You query a view with descending=true. What must you do with startkey and endkey?
- Nothing changes
+ Swap them: startkey must be the larger key (for example "D") and endkey the smaller ("C")
- Remove them; descending does not support ranges
- Add `inclusive_end=false`
? With descending=true CouchDB walks the index backwards from startkey, so the start of the range is the higher value.

Q: A tag-count view has a reduce of `sum(values)`. What does `?group=true` change?
- It removes the reduce step
+ It returns one reduced value per key (a count per tag) instead of one grand total
- It groups documents by revision
- It sorts the results descending
? Without grouping, CouchDB reduces all rows to a single value. `group=true` reduces each distinct key separately.

Q: What is the `rereduce` argument of a reduce function for?
- It tells the function to run twice
+ It says whether `values` are values emitted by map (false) or results of earlier reduce calls (true)
- It forces CouchDB to rebuild the index
- It enables built-in reducers
? CouchDB stores partial reductions in the B-tree and combines them later. Functions that are not simple sums must handle both cases.

Q: Which `_changes` feed keeps one connection open and streams every change as it happens?
- `feed=normal`
- `feed=longpoll`
+ `feed=continuous`
- `feed=stream&since=now`
? `longpoll` waits for the next change and then closes; `continuous` never closes and sends one JSON line per change.

Q: After replicating two databases that each changed the same document, what does CouchDB do?
- Keeps the version with the latest timestamp and discards the other
- Refuses to replicate until an administrator decides
+ Picks the same deterministic winner on every replica and lists the other revision in `_conflicts`
- Creates two documents with different IDs
? No data is lost: the losing revision stays available, and your application resolves the conflict by merging and deleting the loser.

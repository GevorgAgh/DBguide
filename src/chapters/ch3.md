title: Riak
lead: A distributed key-value store that speaks HTTP and keeps working while servers fail. CRUD, links and MIME types on Day 1; mapreduce and clusters on Day 2; conflicts, hooks and search on Day 3.

## Overview: Riak loves the web

Riak is the first NoSQL database in the book, and it feels very different from PostgreSQL. There are **no tables, no SQL, no schema and no transactions**. There are only **buckets**, **keys** and **values**.

What Riak offers instead is a rare combination:

- **Distributed by design.** Data is spread and copied across many servers automatically.
- **No single point of failure.** Every server (node) is equal. There is no "master" whose death stops the cluster.
- **Scale out.** Need more capacity? Add servers; Riak moves data onto them by itself.
- **Speaks the language of the web.** You read and write with plain HTTP requests (`GET`, `PUT`, `POST`, `DELETE`). Any tool or language that can talk HTTP can use Riak, even a web browser.
- **Values can be anything**: plain text, JSON, XML, images, video. The HTTP `Content-Type` header tells Riak (and the browser) what it is.

Riak was built by a company called Basho, written in **Erlang** (a language designed by Ericsson for telephone switches that must never go down), and is a faithful implementation of Amazon's **Dynamo** paper (2007), which described how Amazon kept its shopping cart available through any failure.

:::fig **A Riak cluster has no master.** Every node is a peer that can accept reads and writes for any key. Each key is stored on several nodes, so losing one machine loses no data and stops no requests.
<svg class="dg" viewBox="0 0 720 250">
<rect x="20" y="20" width="110" height="44" rx="8" class="box"/><text x="75" y="47" text-anchor="middle">web app</text>
<rect x="20" y="186" width="110" height="44" rx="8" class="box"/><text x="75" y="213" text-anchor="middle">curl / browser</text>
<circle cx="360" cy="70" r="40" class="bw"/><text x="360" y="66" text-anchor="middle" class="b">node 1</text><text x="360" y="84" text-anchor="middle" class="s">:8091</text>
<circle cx="280" cy="190" r="40" class="bw"/><text x="280" y="186" text-anchor="middle" class="b">node 2</text><text x="280" y="204" text-anchor="middle" class="s">:8092</text>
<circle cx="440" cy="190" r="40" class="bw"/><text x="440" y="186" text-anchor="middle" class="b">node 3</text><text x="440" y="204" text-anchor="middle" class="s">:8093</text>
<line x1="340" y1="105" x2="300" y2="155" class="lw"/><line x1="380" y1="105" x2="420" y2="155" class="lw"/><line x1="320" y1="190" x2="400" y2="190" class="lw"/>
<line x1="132" y1="45" x2="316" y2="65" class="ln" marker-end="url(#arr)"/>
<line x1="132" y1="205" x2="236" y2="195" class="ln" marker-end="url(#arr)"/>
<text x="220" y="44" text-anchor="middle" class="s">HTTP to any node</text>
<text x="540" y="70" class="b">Every node is equal</text>
<text x="540" y="92" class="s">no master, no special node</text>
<text x="540" y="128" class="b">Every key is copied</text>
<text x="540" y="150" class="s">to N nodes (default 3)</text>
<text x="540" y="186" class="b">Lose a node?</text>
<text x="540" y="208" class="s">the others keep serving</text>
</svg>
:::

:::analogy A giant, unbreakable filing cabinet on the web
Think of buckets as drawers, keys as folder labels and values as whatever is inside the folder: a letter, a photo, a spreadsheet. You fetch a folder by its label. You cannot ask the cabinet "find every folder that mentions Paris" (at least, not cheaply). In exchange, the cabinet is copied across many rooms, so a fire in one room never loses your papers.
:::

## Day 1 · CRUD, links and MIMEs

### Step 1: Starting a three-node cluster

The book builds Riak from source and creates three development nodes on one machine, so you can play with a real cluster on a laptop:

```bash
make devrel                        # builds dev/dev1, dev/dev2, dev/dev3
dev/dev1/bin/riak start
dev/dev2/bin/riak start
dev/dev3/bin/riak start

# join the nodes into one cluster
dev/dev2/bin/riak-admin join dev1@127.0.0.1
dev/dev3/bin/riak-admin join dev2@127.0.0.1
```

Each node answers HTTP on its own port: 8091, 8092 and 8093. Any of them can serve any request.

### Step 2: REST in a nutshell

**REST** (REpresentational State Transfer) sounds complicated but is simple: everything is a **resource** with a **URL**, and you act on it with the standard **HTTP verbs**. The book uses `curl`, a command-line HTTP client.

```bash
curl http://localhost:8091/ping                     # OK
curl -I http://localhost:8091/riak/no_bucket/no_key # HTTP/1.1 404 Object Not Found
```

:::fig **Anatomy of a Riak URL, and how HTTP verbs map to CRUD.** The bucket and key are simply parts of the path, so every value in the database has its own web address.
<svg class="dg wide" viewBox="0 0 720 230">
<g class="mono">
<rect x="10" y="20" width="160" height="40" rx="6" class="box"/><text x="90" y="45" text-anchor="middle">http://localhost</text>
<rect x="174" y="20" width="70" height="40" rx="6" class="box"/><text x="209" y="45" text-anchor="middle">:8091</text>
<rect x="248" y="20" width="80" height="40" rx="6" class="box"/><text x="288" y="45" text-anchor="middle">/riak</text>
<rect x="332" y="20" width="110" height="40" rx="6" class="bw"/><text x="387" y="45" text-anchor="middle">/animals</text>
<rect x="446" y="20" width="80" height="40" rx="6" class="ba"/><text x="486" y="45" text-anchor="middle">/ace</text>
</g>
<text x="90" y="80" text-anchor="middle" class="s">server</text><text x="209" y="80" text-anchor="middle" class="s">node port</text>
<text x="288" y="80" text-anchor="middle" class="s">Riak API</text><text x="387" y="80" text-anchor="middle" class="s tw b">bucket</text><text x="486" y="80" text-anchor="middle" class="s ta b">key</text>
<g>
<rect x="10" y="110" width="170" height="100" rx="8" class="bg"/><text x="95" y="138" text-anchor="middle" class="b mono">PUT</text><text x="95" y="160" text-anchor="middle" class="s">create or replace</text><text x="95" y="178" text-anchor="middle" class="s">a value at a key</text>
<rect x="190" y="110" width="170" height="100" rx="8" class="ba"/><text x="275" y="138" text-anchor="middle" class="b mono">GET</text><text x="275" y="160" text-anchor="middle" class="s">read a value</text>
<rect x="370" y="110" width="170" height="100" rx="8" class="bw"/><text x="455" y="138" text-anchor="middle" class="b mono">POST</text><text x="455" y="160" text-anchor="middle" class="s">create in a bucket;</text><text x="455" y="178" text-anchor="middle" class="s">Riak invents the key</text>
<rect x="550" y="110" width="160" height="100" rx="8" class="br"/><text x="630" y="138" text-anchor="middle" class="b mono">DELETE</text><text x="630" y="160" text-anchor="middle" class="s">remove the value</text><text x="630" y="178" text-anchor="middle" class="s">(204 No Content)</text>
</g>
</svg>
:::

Some `curl` flags you will see constantly:

| Flag | Meaning |
|---|---|
| `-X PUT` | Use this HTTP method. |
| `-H "Content-Type: application/json"` | Send this header. |
| `-d '...'` | Send this request body. |
| `-v` | Verbose: show the request and response headers. |
| `-i` / `-I` | Include response headers / fetch headers only. |

### Step 3: PUT a value in a bucket

Riak groups keys into **buckets**, so the key `ace` in bucket `animals` does not clash with `ace` in bucket `playing_cards`. Buckets do not need to be created: the first `PUT` creates one.

The book starts by storing an HTML page, then opens it in a browser:

```bash
curl -v -X PUT http://localhost:8091/riak/favs/db \
  -H "Content-Type: text/html" \
  -d "<html><body><h1>My new favorite DB is RIAK</h1></body></html>"
```

Visit `http://localhost:8091/riak/favs/db` and the browser renders the page, because Riak returns the same content type it was given. Riak is a little web server for your data.

Now some JSON:

```bash
curl -v -X PUT http://localhost:8091/riak/animals/ace \
  -H "Content-Type: application/json" \
  -d '{"nickname" : "The Wonder Dog", "breed" : "German Shepherd"}'

curl -X GET http://localhost:8091/riak?buckets=true
# {"buckets":["favs","animals"]}
```

The response to a `PUT` has no body by default. Add `?returnbody=true` to get the stored value back:

```bash
curl -v -X PUT http://localhost:8091/riak/animals/polly?returnbody=true \
  -H "Content-Type: application/json" \
  -d '{"nickname" : "Sweet Polly Purebred", "breed" : "Purebred"}'
```

### Step 4: POST, DELETE and listing keys

If you do not care what the key is, `POST` to the bucket and Riak generates one, returned in the `Location` header:

```bash
curl -i -X POST http://localhost:8091/riak/animals \
  -H "Content-Type: application/json" \
  -d '{"nickname" : "Sergeant Stubby", "breed" : "Terrier"}'
# Location: /riak/animals/6VZc2o7zKxq2B34kJrm1S0ma3PO

curl -i -X DELETE http://localhost:8091/riak/animals/6VZc2o7zKxq2B34kJrm1S0ma3PO
# HTTP/1.1 204 No Content

curl http://localhost:8091/riak/animals?keys=true
# {"keys":["polly","ace"], ...}
```

:::warn Listing keys is expensive
`?keys=true` (and `?buckets=true`) must ask every node to walk through all of its keys. On a production cluster with billions of keys that is very slow and can hurt every other request. Use it for learning, not in real applications. Riak is designed for "fetch this key", not for "show me everything".
:::

### Step 5: Links between values

Riak cannot join, but it can attach **links** to a value: pointers to other bucket/key pairs, each with an optional **tag** describing the relationship. Links travel in an HTTP `Link` header.

The book models animal cages. Cage 1 contains Polly; cage 2 contains Ace and sits next to cage 1:

```bash
curl -X PUT http://localhost:8091/riak/cages/1 \
  -H "Content-Type: application/json" \
  -H "Link: </riak/animals/polly>; riaktag=\"contains\"" \
  -d '{"room" : 101}'

curl -X PUT http://localhost:8091/riak/cages/2 \
  -H "Content-Type: application/json" \
  -H "Link: </riak/animals/ace>; riaktag=\"contains\", </riak/cages/1>; riaktag=\"next_to\"" \
  -d '{"room" : 101}'
```

:::fig **Links connect values across buckets.** Each link is a one-way arrow with a tag. Link walking follows these arrows from a starting key, for example "from cage 2, follow next_to, then follow contains" to reach Polly.
<svg class="dg" viewBox="0 0 720 240">
<rect x="20" y="20" width="200" height="200" rx="10" class="soft"/><text x="120" y="44" text-anchor="middle" class="b">bucket: cages</text>
<rect x="420" y="20" width="280" height="200" rx="10" class="soft"/><text x="560" y="44" text-anchor="middle" class="b">bucket: animals</text>
<rect x="60" y="64" width="120" height="50" rx="8" class="bw"/><text x="120" y="86" text-anchor="middle" class="b mono">1</text><text x="120" y="104" text-anchor="middle" class="s">{"room":101}</text>
<rect x="60" y="150" width="120" height="50" rx="8" class="bw"/><text x="120" y="172" text-anchor="middle" class="b mono">2</text><text x="120" y="190" text-anchor="middle" class="s">{"room":101}</text>
<rect x="480" y="64" width="160" height="50" rx="8" class="ba"/><text x="560" y="86" text-anchor="middle" class="b mono">polly</text><text x="560" y="104" text-anchor="middle" class="s">Sweet Polly Purebred</text>
<rect x="480" y="150" width="160" height="50" rx="8" class="ba"/><text x="560" y="172" text-anchor="middle" class="b mono">ace</text><text x="560" y="190" text-anchor="middle" class="s">The Wonder Dog</text>
<line x1="182" y1="89" x2="476" y2="89" class="lw" marker-end="url(#arrw)"/><text x="330" y="82" text-anchor="middle" class="s b tw">contains</text>
<line x1="182" y1="175" x2="476" y2="175" class="lw" marker-end="url(#arrw)"/><text x="330" y="168" text-anchor="middle" class="s b tw">contains</text>
<line x1="120" y1="148" x2="120" y2="118" class="ln" marker-end="url(#arr)"/><text x="132" y="138" class="s b">next_to</text>
</svg>
:::

Fetch cage 1 with `-i` and you can see the stored link in the response headers:

```text
Link: </riak/animals/polly>; riaktag="contains", </riak/cages>; rel="up"
```

#### Link walking

To follow links, append one or more **steps** to the URL. Each step has three parts separated by commas: **`bucket,tag,keep`**. An underscore (`_`) means "anything".

| Part | Meaning |
|---|---|
| `bucket` | Only follow links into this bucket (`_` = any bucket). |
| `tag` | Only follow links with this tag (`_` = any tag). |
| `keep` | `1` to include this step's results in the response, `0` to skip them. By default only the last step is kept. |

```bash
curl http://localhost:8091/riak/cages/1/_,_,_
# everything cage 1 links to: Polly

curl http://localhost:8091/riak/cages/2/animals,_,_
# links from cage 2 into the animals bucket: Ace

curl http://localhost:8091/riak/cages/2/_,next_to,_
# cage 1 (the cage next to cage 2)

curl http://localhost:8091/riak/cages/2/_,next_to,0/animals,_,_
# two hops: cage 2 → (next_to) cage 1 → (any) animals → Polly

curl http://localhost:8091/riak/cages/2/_,next_to,1/_,_,_
# same walk, but keep=1 also returns cage 1 itself
```

Results come back as a **multipart** response (one part per step kept), the same format email uses for attachments.

:::fig **Reading a link-walk URL.** Each `/bucket,tag,keep` segment is one hop. Here we start at cage 2, hop along `next_to` without keeping the result, then hop into the animals bucket and return what we find.
<svg class="dg wide" viewBox="0 0 720 150">
<g class="mono">
<rect x="10" y="20" width="200" height="40" rx="6" class="bw"/><text x="110" y="45" text-anchor="middle">/riak/cages/2</text>
<rect x="216" y="20" width="160" height="40" rx="6" class="box"/><text x="296" y="45" text-anchor="middle">/_,next_to,0</text>
<rect x="382" y="20" width="160" height="40" rx="6" class="ba"/><text x="462" y="45" text-anchor="middle">/animals,_,_</text>
</g>
<text x="110" y="84" text-anchor="middle" class="s">start here</text>
<text x="296" y="84" text-anchor="middle" class="s">hop 1: any bucket,</text><text x="296" y="100" text-anchor="middle" class="s">tag next_to, don't keep</text>
<text x="462" y="84" text-anchor="middle" class="s">hop 2: into animals,</text><text x="462" y="100" text-anchor="middle" class="s">any tag, keep (last step)</text>
<line x1="550" y1="40" x2="600" y2="40" class="ln" marker-end="url(#arr)"/>
<rect x="606" y="20" width="104" height="40" rx="6" class="bg"/><text x="658" y="45" text-anchor="middle" class="b">polly</text>
<text x="360" y="136" text-anchor="middle" class="s">cage 2 → cage 1 → polly</text>
</svg>
:::

:::deep Links are not joins
A SQL join is computed by the database over whole tables, and works in any direction. A Riak link is a one-way pointer stored inside one value's metadata. Polly does not know that cage 1 contains her unless you also store a link from Polly to cage 1. Links are great for a few known relationships ("this photo belongs to this animal"), not for ad hoc queries across many values.
:::

### Step 6: MIME types

Riak stores every value as raw bytes, exactly like HTTP. The **MIME type** in `Content-Type` gives those bytes meaning: `text/plain`, `application/json`, `image/jpeg`, `application/pdf` and so on. So you can store a photo and link it to its animal:

```bash
curl -X PUT http://localhost:8091/riak/photos/polly.jpg \
  -H "Content-type: image/jpeg" \
  -H "Link: </riak/animals/polly>; riaktag=\"photo\"" \
  --data-binary @polly_image.jpg
```

Open `http://localhost:8091/riak/photos/polly.jpg` in a browser and you see the picture. (`--data-binary` sends the file's bytes unchanged; `-d` would strip newlines.)

### Day 1 wrap-up

When you design data for Riak, the authors suggest thinking of something **between a cache and PostgreSQL**. You split data into logical groups (buckets), and values can refer to each other with links, but you do not normalize into tiny pieces as in a relational database, because Riak cannot join them back together.

### Day 1 homework, solved

**1. Update `animals/polly` with a link to `photos/polly.jpg`.** A PUT replaces the whole value, so send the JSON again along with the new link:

```bash
curl -X PUT http://localhost:8091/riak/animals/polly \
  -H "Content-Type: application/json" \
  -H "Link: </riak/photos/polly.jpg>; riaktag=\"photo\"" \
  -d '{"nickname" : "Sweet Polly Purebred", "breed" : "Purebred"}'
```

**2. POST a file with a new MIME type, then open it in a browser:**

```bash
curl -i -X POST http://localhost:8091/riak/documents \
  -H "Content-Type: application/pdf" \
  --data-binary @manual.pdf
# Location: /riak/documents/<generated-key>  -> open that URL in a browser
```

**3. Store an image in a new `medicines` bucket, keyed `antibiotics`, linked to Ace:**

```bash
curl -X PUT http://localhost:8091/riak/medicines/antibiotics \
  -H "Content-Type: image/jpeg" \
  -H "Link: </riak/animals/ace>; riaktag=\"medicine\"" \
  --data-binary @antibiotics.jpg
```

## Day 2 · Mapreduce and server clusters

Day 2 covers the two biggest ideas in the chapter: **mapreduce**, Riak's way of computing over many values, and **how a Riak cluster spreads and copies data**.

### Step 1: Some data to query

The book loads a hotel into a `rooms` bucket with a small Ruby script: 100 floors with 100 rooms each, every room stored as JSON with a random `style` (single, double, queen, king, suite) and a `capacity`. The key is the room number:

```ruby
STYLES = %w{single double queen king suite}
for floor in 1..100
  for room in 1...100
    ro = Riak::RObject.new(bucket, (100 * floor + room).to_s)
    style = STYLES[rand(STYLES.length)]
    ro.data = {'style' => style, 'capacity' => rand(8) + 1}
    ro.store
  end
end
```

So key `"4201"` is room 1 on floor 42, with a value like `{"style":"queen","capacity":4}`.

### Step 2: What mapreduce is

In SQL we would write `SELECT style, sum(capacity) FROM rooms GROUP BY style`. Riak has no SQL, so we use **mapreduce**, a pattern made famous by a 2004 Google paper. It has two kinds of functions:

- **Map**: runs once for **each value**, and turns it into something smaller and more useful. It runs **where the data lives**, on every node in parallel.
- **Reduce**: takes **many map outputs** and combines them into a summary.

:::fig **Mapreduce on the hotel.** Each node maps its own rooms into small `{style: capacity}` objects in parallel, close to the data. Reduce merges them into totals per style. Only small results travel over the network, never the raw data.
<svg class="dg wide" viewBox="0 0 720 300">
<text x="80" y="20" text-anchor="middle" class="b">values on nodes</text>
<text x="300" y="20" text-anchor="middle" class="b">map (in parallel)</text>
<text x="560" y="20" text-anchor="middle" class="b">reduce</text>
<rect x="10" y="34" width="140" height="80" rx="8" class="bw"/><text x="80" y="54" text-anchor="middle" class="s b">node 1</text>
<text x="20" y="74" class="mono s">101 queen, 2</text><text x="20" y="92" class="mono s">102 king, 4</text>
<rect x="10" y="124" width="140" height="80" rx="8" class="bw"/><text x="80" y="144" text-anchor="middle" class="s b">node 2</text>
<text x="20" y="164" class="mono s">103 queen, 3</text><text x="20" y="182" class="mono s">104 suite, 6</text>
<rect x="10" y="214" width="140" height="70" rx="8" class="bw"/><text x="80" y="234" text-anchor="middle" class="s b">node 3</text>
<text x="20" y="254" class="mono s">105 king, 1</text>
<line x1="152" y1="74" x2="204" y2="74" class="ln" marker-end="url(#arr)"/>
<line x1="152" y1="164" x2="204" y2="164" class="ln" marker-end="url(#arr)"/>
<line x1="152" y1="250" x2="204" y2="250" class="ln" marker-end="url(#arr)"/>
<rect x="210" y="50" width="180" height="50" rx="8" class="box"/><text x="300" y="70" text-anchor="middle" class="mono s">{queen:2}</text><text x="300" y="88" text-anchor="middle" class="mono s">{king:4}</text>
<rect x="210" y="140" width="180" height="50" rx="8" class="box"/><text x="300" y="160" text-anchor="middle" class="mono s">{queen:3}</text><text x="300" y="178" text-anchor="middle" class="mono s">{suite:6}</text>
<rect x="210" y="230" width="180" height="40" rx="8" class="box"/><text x="300" y="255" text-anchor="middle" class="mono s">{king:1}</text>
<line x1="392" y1="75" x2="470" y2="140" class="ln" marker-end="url(#arr)"/>
<line x1="392" y1="165" x2="470" y2="160" class="ln" marker-end="url(#arr)"/>
<line x1="392" y1="250" x2="470" y2="180" class="ln" marker-end="url(#arr)"/>
<rect x="476" y="110" width="170" height="100" rx="10" class="bg"/>
<text x="561" y="134" text-anchor="middle" class="b">totals</text>
<text x="561" y="156" text-anchor="middle" class="mono s">queen: 5</text><text x="561" y="174" text-anchor="middle" class="mono s">king: 5</text><text x="561" y="192" text-anchor="middle" class="mono s">suite: 6</text>
<line x1="648" y1="160" x2="700" y2="160" class="ln" marker-end="url(#arr)"/>
</svg>
:::

:::analogy Counting votes
On election night, every polling station counts its own ballots (map, done locally and in parallel). Each station phones in a small summary, not the boxes of paper. Head office adds up the summaries (reduce). Moving the code to the data instead of the data to the code is the whole point.
:::

### Step 3: A mapreduce request

You send a mapreduce job to Riak's `/mapred` endpoint as JSON. It has **inputs** (which bucket/keys to start from) and a **query** (a list of phases):

```bash
curl -X POST -H "content-type:application/json" \
  http://localhost:8091/mapred --data @- <<EOF
{
  "inputs":[
    ["rooms","101"],["rooms","102"],["rooms","103"]
  ],
  "query":[
    {"map":{
      "language":"javascript",
      "source":
        "function(v) {
          /* v is a Riak object; its JSON lives in v.values[0].data */
          var parsed_data = JSON.parse(v.values[0].data);
          var data = {};
          /* key: the room style; value: its capacity */
          data[parsed_data.style] = parsed_data.capacity;
          return [data];
        }"
    }},
    {"reduce":{
      "language":"javascript",
      "source":
        "function(v) {
          var totals = {};
          for (var i in v) {
            for (var style in v[i]) {
              if (totals[style]) totals[style] += v[i][style];
              else               totals[style]  = v[i][style];
            }
          }
          return [totals];
        }"
    }}
  ]
}
EOF
# [{"suite":6,"king":4,"double":5}] (your random numbers will differ)
```

Notice that both functions return **arrays**. A map can return zero, one or many results per value. To run over the whole bucket, set `"inputs":"rooms"` instead of a list of keys (expensive, for the same reason as listing keys).

:::deep Why reduce must be "re-reducible"
Riak may call your reduce function **several times**: first on partial batches of map results, then again on the outputs of those earlier reduces. So the reduce output must have the **same shape as its input**, and combining in any order must give the same answer. Summing per style works, because a total of totals is still a total. Computing an average directly would not (an average of averages is wrong); instead, carry `sum` and `count` and divide at the very end.
:::

### Step 4: Stored functions and built-ins

Writing JavaScript inside JSON is clumsy, so you can **store** a function as a value in Riak and reference it by bucket and key:

```bash
curl -X PUT -H "content-type:application/json" \
  http://localhost:8091/riak/my_functions/map_capacity --data @- <<EOF
function(v) {
  var parsed_data = JSON.parse(v.values[0].data);
  var data = {};
  data[parsed_data.style] = parsed_data.capacity;
  return [data];
}
EOF
```

```json
{"map":{ "language":"javascript", "bucket":"my_functions", "key":"map_capacity" }}
```

Riak also ships with **built-in functions** in `mapred_builtins.js`, such as `Riak.mapValuesJson` (parse each value as JSON) and `Riak.reduceSum` (add numbers):

```json
"query":[
  {"map":{"language":"javascript", "source":"function(v){ var d = JSON.parse(v.values[0].data); return [d.capacity]; }"}},
  {"reduce":{"language":"javascript", "name":"Riak.reduceSum"}}
]
```

### Step 5: Key filters

Mapreduce over a whole bucket reads every value. **Key filters** narrow the inputs by looking only at the **keys**, before any value is loaded:

```json
"inputs":{
  "bucket":"rooms",
  "key_filters":[["string_to_int"], ["less_than", 1000]]
}
```

This converts each key to an integer and keeps only rooms below 1000 (floors 1 to 9). Filters can be chained: tokenizing, `between`, `starts_with`, `ends_with`, `matches` (regex), `and`, `or`, `not` and more.

You can also put a **link phase** in a mapreduce query, to walk links and then map over whatever you reach:

```json
"query":[
  {"link":{"bucket":"animals", "keep":false}},
  {"map":{"language":"javascript", "source":"function(v) { return [v]; }"}}
]
```

### Step 6: How a Riak cluster spreads data, the ring

Now the second big idea. How does Riak decide which node stores which key? With **consistent hashing**:

1. Riak treats all possible hash values, a **160-bit number**, as a **ring**: the largest number wraps around back to zero.
2. The ring is cut into equal **partitions** (64 by default). Each partition is run by a **virtual node** (vnode).
3. Physical nodes **claim partitions in turn** around the ring, so each server owns an equal share, spread out.
4. To store a key, Riak **hashes** `bucket/key` with SHA-1. The result is a point on the ring, which falls inside one partition.
5. The value is stored in that partition **and the next N−1 partitions** clockwise. With N = 3 that means three different physical nodes.

:::fig **The consistent hashing ring**, shown with 8 partitions instead of 64. Three physical nodes take turns owning partitions. The key `rooms/101` hashes to a point in a partition owned by node C, so its three copies live on C and on the next two partitions clockwise, owned by A and B.
<svg class="dg" viewBox="0 0 720 330">
<path d="M200,50 A110,110 0 0,1 277.8,82.2" class="la" style="stroke-width:22px"/>
<path d="M277.8,82.2 A110,110 0 0,1 310,160" class="lw" style="stroke-width:22px"/>
<path d="M310,160 A110,110 0 0,1 277.8,237.8" class="lgr" style="stroke-width:22px"/>
<path d="M277.8,237.8 A110,110 0 0,1 200,270" class="la" style="stroke-width:22px"/>
<path d="M200,270 A110,110 0 0,1 122.2,237.8" class="lw" style="stroke-width:22px"/>
<path d="M122.2,237.8 A110,110 0 0,1 90,160" class="lgr" style="stroke-width:22px"/>
<path d="M90,160 A110,110 0 0,1 122.2,82.2" class="la" style="stroke-width:22px"/>
<path d="M122.2,82.2 A110,110 0 0,1 200,50" class="lw" style="stroke-width:22px"/>
<g class="s mono">
<text x="254" y="26" text-anchor="middle">p1</text><text x="336" y="106" text-anchor="middle">p2</text><text x="336" y="222" text-anchor="middle">p3</text><text x="254" y="304" text-anchor="middle">p4</text>
<text x="146" y="304" text-anchor="middle">p5</text><text x="64" y="222" text-anchor="middle">p6</text><text x="64" y="106" text-anchor="middle">p7</text><text x="146" y="26" text-anchor="middle">p8</text>
</g>
<circle cx="308" cy="179" r="7" class="fi"/>
<text x="200" y="150" text-anchor="middle" class="b">hash(rooms/101)</text>
<text x="200" y="170" text-anchor="middle" class="s">lands in p3</text>
<line x1="260" y1="172" x2="298" y2="177" class="ln" marker-end="url(#arr)"/>
<path d="M332,200 A135,135 0 0,1 168,291" class="ln dash" marker-end="url(#arr)"/>
<text x="200" y="196" text-anchor="middle" class="s">copies go clockwise</text>
<rect x="440" y="40" width="16" height="16" rx="3" class="fa"/><text x="464" y="53">node A</text>
<rect x="530" y="40" width="16" height="16" rx="3" class="fw"/><text x="554" y="53">node B</text>
<rect x="620" y="40" width="16" height="16" rx="3" class="fg"/><text x="644" y="53">node C</text>
<text x="440" y="100" class="b">N = 3 copies of rooms/101</text>
<text x="440" y="124" class="s">p3 (node C) primary</text>
<text x="440" y="144" class="s">p4 (node A) replica</text>
<text x="440" y="164" class="s">p5 (node B) replica</text>
<text x="440" y="206" class="b">Add a 4th node?</text>
<text x="440" y="228" class="s">It claims a share of partitions;</text>
<text x="440" y="246" class="s">only those partitions move.</text>
<text x="440" y="264" class="s">Most keys stay where they are.</text>
</svg>
:::

:::deep Why "consistent" hashing?
The naive approach is `node = hash(key) mod number_of_nodes`. Add one server and almost **every** key maps to a different node, so nearly all data must move. With a ring of fixed partitions, adding a node only transfers the partitions it claims; every other key stays put. That is what lets Riak grow or shrink a live cluster smoothly.
:::

### Step 7: N, R and W

Riak lets you tune how many copies to keep and how many nodes must answer, **per bucket and even per request**:

| Value | Meaning | Default |
|---|---|---|
| **N** | How many nodes store a copy of each value (`n_val`). Set per bucket. | 3 |
| **R** | How many nodes must answer a **read** before it succeeds. | the bucket's setting |
| **W** | How many nodes must acknowledge a **write** before it succeeds. | the bucket's setting |
| **DW** | How many nodes must have written to **durable storage** (disk) before it succeeds. | the bucket's setting |

R and W can be any number from 1 to N, or one of the words `one` (1), `quorum` (a majority: N/2 + 1), `all` (the same as N) or `default` (whatever the bucket is set to). You can set them on the bucket (`{"props":{"w":2}}`) or on a single request (`?r=3`).

```bash
# store 4 copies of everything in the animals bucket
curl -X PUT http://localhost:8091/riak/animals \
  -H "Content-Type: application/json" \
  -d '{"props":{"n_val":4}}'

# a read that needs 3 nodes to agree, then one that needs all of them
curl http://localhost:8091/riak/animals/ace?r=3
curl http://localhost:8091/riak/animals/ace?r=all

# a write that needs no acknowledgement at all ("fire and forget")
curl -X PUT http://localhost:8091/riak/animals/jean?w=0 \
  -H "Content-Type: application/json" \
  -d '{"nickname":"Jean", "breed":"Border Collie"}'
```

:::fig **Why R + W > N gives you the latest value.** With N = 3, a write waits for 2 acknowledgements (W = 2) and a read asks 2 nodes (R = 2). Any 2 nodes out of 3 must share at least one node with any other 2, so every read reaches at least one node that has the newest write.
<svg class="dg wide" viewBox="0 0 720 240">
<circle cx="250" cy="120" r="44" class="bg"/><text x="250" y="116" text-anchor="middle" class="b">node 1</text><text x="250" y="134" text-anchor="middle" class="s">v2 (new)</text>
<circle cx="360" cy="120" r="44" class="bg"/><text x="360" y="116" text-anchor="middle" class="b">node 2</text><text x="360" y="134" text-anchor="middle" class="s">v2 (new)</text>
<circle cx="470" cy="120" r="44" class="box"/><text x="470" y="116" text-anchor="middle" class="b">node 3</text><text x="470" y="134" text-anchor="middle" class="s">v1 (old)</text>
<rect x="190" y="60" width="230" height="120" rx="60" class="la dash" fill="none"/>
<text x="305" y="44" text-anchor="middle" class="ta b">write acknowledged by W = 2</text>
<rect x="305" y="64" width="230" height="112" rx="56" class="lw dash" fill="none"/>
<text x="420" y="206" text-anchor="middle" class="tw b">read asks R = 2</text>
<text x="590" y="100" class="s">overlap on node 2:</text>
<text x="590" y="118" class="s">the read sees v2 and</text>
<text x="590" y="136" class="s">returns the newest</text>
<text x="20" y="100" class="b">N = 3</text>
<text x="20" y="124" class="s">R + W = 4 &gt; 3</text>
<text x="20" y="148" class="s">→ always overlaps</text>
</svg>
:::

The book then shuts down one node (`dev/dev3/bin/riak stop`) and reads with `?r=all`. There is a good chance the request fails with **404 Object Not Found**: not enough copies could answer. The failure also triggers a **read repair**, where Riak copies the value to the nodes still available, so trying the same URL again returns the value. The book's conclusion is that the safer choice is `r=quorum`, which needs most nodes but not all. This is the trade-off in action: **more nodes required = stronger consistency, but less availability**.

:::tip Choosing N, R and W
- **Fast, highly available, may read stale data:** R = 1, W = 1.
- **Balanced (Riak's default):** R = quorum, W = quorum.
- **Read-heavy data that must be fresh:** W = all, R = 1 (every write reaches all copies, so any copy is current).
- **Fire and forget (logs, metrics):** W = 0.
:::

:::deep Hinted handoff
What happens when a node is down and a write arrives for one of its partitions? Another node accepts the write **on its behalf** and keeps a "hint". When the missing node comes back, the stand-in hands the data over. That is how a Riak cluster keeps accepting writes while a node is down. It is called **hinted handoff** and comes straight from the Dynamo paper. Its partner is **read repair**: when a read notices that some replicas are missing or out of date, Riak writes the current value back to them.
:::

### Day 2 homework, solved

**1. Total guest capacity per floor.** The map function gets the floor from the key (`4201` → floor 42) and emits `{floor: capacity}`; the reduce adds them up, exactly like the style example:

```json
{
  "inputs":"rooms",
  "query":[
    {"map":{"language":"javascript","source":
      "function(v) {
         var parsed = JSON.parse(v.values[0].data);
         var floor = Math.floor(parseInt(v.key, 10) / 100);
         var out = {};
         out[floor] = parsed.capacity;
         return [out];
       }"}},
    {"reduce":{"language":"javascript","source":
      "function(v) {
         var totals = {};
         for (var i in v) {
           for (var floor in v[i]) {
             totals[floor] = (totals[floor] || 0) + v[i][floor];
           }
         }
         return [totals];
       }"}}
  ]
}
```

**2. Only floors 42 and 43.** Keep the same query but restrict the inputs with a key filter (rooms 4200 to 4399):

```json
"inputs":{
  "bucket":"rooms",
  "key_filters":[["string_to_int"], ["between", 4200, 4399]]
}
```

## Day 3 · Resolving conflicts and extending Riak

### Step 1: The conflict problem

Riak values availability above everything, so it lets **any node accept a write at any time**, even when nodes cannot talk to each other. The consequence: two clients can update the same key **at the same time** on different nodes. Which version is correct?

Many systems use **timestamps** ("last write wins"). Riak avoids that, because keeping clocks synchronized across many machines is unreliable: a server whose clock is a few seconds fast would silently win every conflict. Instead Riak uses **vector clocks**.

### Step 2: Vector clocks

A **vector clock** is a small piece of metadata attached to each value. It records, for each client (or node) that changed the value, a counter of how many times it did so. Riak returns it in the `X-Riak-Vclock` header, and you send it back with your update to say "this is the version I started from".

By comparing two vector clocks, Riak can tell whether one version **descends** from the other (a normal update, keep the newer one) or whether they were made **concurrently** (a real conflict).

:::fig **A vector clock conflict.** Jane and Rakshith both read Bob's version of Bruiser (score 3, vector clock `{bob:1}`). Jane writes 2, Rakshith (`rak`) writes 4. Each updates it without seeing the other's change. Neither vector clock descends from the other, so Riak keeps both versions as **siblings** and lets the next reader resolve them.
<svg class="dg wide" viewBox="0 0 720 290">
<text x="10" y="54" class="b">Jane</text>
<text x="10" y="150" class="b tw">Riak</text>
<text x="10" y="246" class="b">Rakshith</text>
<line x1="90" y1="50" x2="700" y2="50" class="ln2"/>
<line x1="90" y1="146" x2="700" y2="146" class="lw"/>
<line x1="90" y1="242" x2="700" y2="242" class="ln2"/>
<rect x="96" y="124" width="110" height="44" rx="8" class="bw"/><text x="151" y="142" text-anchor="middle" class="mono s">score: 3</text><text x="151" y="160" text-anchor="middle" class="mono s">vc {bob:1}</text>
<line x1="170" y1="122" x2="200" y2="62" class="ln dash" marker-end="url(#arr)"/>
<line x1="170" y1="170" x2="200" y2="230" class="ln dash" marker-end="url(#arr)"/>
<text x="214" y="80" class="s">GET (vc bob:1)</text>
<text x="214" y="222" class="s">GET (vc bob:1)</text>
<rect x="290" y="30" width="120" height="40" rx="8" class="box"/><text x="350" y="55" text-anchor="middle" class="mono s">PUT score 2</text>
<rect x="290" y="222" width="120" height="40" rx="8" class="box"/><text x="350" y="247" text-anchor="middle" class="mono s">PUT score 4</text>
<line x1="380" y1="72" x2="430" y2="124" class="ln" marker-end="url(#arr)"/>
<line x1="380" y1="220" x2="430" y2="170" class="ln" marker-end="url(#arr)"/>
<rect x="436" y="110" width="130" height="72" rx="8" class="br"/>
<text x="501" y="130" text-anchor="middle" class="b tr">2 siblings</text>
<text x="501" y="150" text-anchor="middle" class="mono s">2 {bob:1,jane:1}</text>
<text x="501" y="168" text-anchor="middle" class="mono s">4 {bob:1,rak:1}</text>
<line x1="568" y1="146" x2="598" y2="146" class="ln" marker-end="url(#arr)"/>
<rect x="602" y="114" width="108" height="64" rx="8" class="bg"/>
<text x="656" y="134" text-anchor="middle" class="s b">resolved PUT</text>
<text x="656" y="152" text-anchor="middle" class="mono s">score 3</text>
<text x="656" y="170" text-anchor="middle" class="mono s">new vclock</text>
<text x="501" y="206" text-anchor="middle" class="s">GET returns 300</text>
<text x="501" y="222" text-anchor="middle" class="s">Multiple Choices</text>
</svg>
:::

In the book's example, the `animals` bucket is set to keep siblings (`"allow_mult":true`). **Bob** stores Bruiser with a score of 3. **Jane** and **Rakshith** both read Bob's version, then each updates the score without knowing about the other: Jane to 2, Rakshith to 4. Both send Bob's vector clock to say "my value replaces Bob's":

```bash
# make the bucket keep conflicting versions instead of picking one
curl -X PUT http://localhost:8091/riak/animals \
  -H "Content-Type: application/json" -d '{"props":{"allow_mult":true}}'

# Bob creates Bruiser
curl -i -X PUT http://localhost:8091/riak/animals/bruiser \
  -H "X-Riak-ClientId: bob" \
  -H "Content-Type: application/json" \
  -d '{"score" : 3}'

# Jane and Rakshith read it and receive Bob's vector clock
curl -i http://localhost:8091/riak/animals/bruiser?return_body=true
# X-Riak-Vclock: a85hYGBgzGDKBVIs7NtEXmUwJTLmsTI8FMs5zpcFAA==
# {"score" : 3}
# (your vclock string will differ; always copy the one you received)

# Jane's update
curl -i -X PUT http://localhost:8091/riak/animals/bruiser \
  -H "X-Riak-ClientId: jane" \
  -H "X-Riak-Vclock: a85hYGBgzGDKBVIs7NtEXmUwJTLmsTI8FMs5zpcFAA==" \
  -H "Content-Type: application/json" \
  -d '{"score" : 2}'

# Rakshith's update, from the same (now old) vclock
curl -i -X PUT http://localhost:8091/riak/animals/bruiser \
  -H "X-Riak-ClientId: rakshith" \
  -H "X-Riak-Vclock: a85hYGBgzGDKBVIs7NtEXmUwJTLmsTI8FMs5zpcFAA==" \
  -H "Content-Type: application/json" \
  -d '{"score" : 4}'

curl http://localhost:8091/riak/animals/bruiser?return_body=true
# Siblings:
#   637aZSiky628lx1YrstzH5
#   7F85FBAIW8eiD9ubsBAeVk

curl -i http://localhost:8091/riak/animals/bruiser?return_body=true \
  -H "Accept: multipart/mixed"
# HTTP/1.1 300 Multiple Choices
# X-Riak-Vclock: a85hYGBgyWDKBVHs20Re...OYn9XY4sskQUA
# ... one part with {"score" : 4} and one with {"score" : 2}
```

`300 Multiple Choices` is the HTTP way of saying "there is more than one answer". Each sibling ID is an ETag (Riak calls it a **vtag**), so you can fetch one version with `?vtag=7F85FBAIW8eiD9ubsBAeVk`, or all of them at once with `Accept: multipart/mixed`. To **resolve** the conflict, Jane decides the correct value (she averages 2 and 4 into 3) and PUTs it with the **vector clock from the multipart response**, which tells Riak this new value supersedes both siblings:

```bash
curl -i -X PUT http://localhost:8091/riak/animals/bruiser?return_body=true \
  -H "X-Riak-ClientId: jane" \
  -H "X-Riak-Vclock: a85hYGBgyWDKBVHs20Re...OYn9XY4sskQUA" \
  -H "Content-Type: application/json" \
  -d '{"score" : 3}'
```

(The vclock is shortened here, as in the book; use the full string you received.)

:::deep How a vector clock decides "newer" versus "conflict"
Write vector clocks as counters per actor. Version X **descends from** version Y if every counter in X is greater than or equal to the matching counter in Y.
- Jane's `{bob:1, jane:1}` vs Bob's `{bob:1}`: every counter is ≥, so Jane's version simply replaces Bob's.
- Jane's `{bob:1, jane:1}` vs Rakshith's `{bob:1, rakshith:1}`: Jane's has more `jane`, Rakshith's has more `rakshith`. Neither descends from the other, so they are **concurrent** and both are kept as siblings.
- After Jane resolves it, `{bob:1, rakshith:1, jane:2}` descends from both siblings, so they disappear.
Note that Riak never decides **which value is right**. It only detects that a human (or your code) needs to decide.
:::

Vector clocks grow with every new client that touches a value. Riak **prunes** them using bucket settings (`small_vclock`, `big_vclock`, `young_vclock`, `old_vclock`) that control how many entries and how old an entry may be before it is dropped. Pruning trades a tiny risk of a false conflict for bounded metadata size.

### Step 3: Pre-commit and post-commit hooks

Riak can run functions **before** or **after** a write is stored. A **pre-commit hook** can modify the value, or **reject** the write by returning `{"fail": "message"}`. The book writes a validator that refuses any animal without a score, or with a score outside 1 to 4:

```javascript
// my_validators.js, placed in the directory named by js_source_dir in app.config
function good_score(object) {
  try {
    /* from the Riak object, pull data and parse it as JSON */
    var data = JSON.parse( object.values[0].data );
    /* if score is not found, fail here */
    if( !data.score || data.score === '' ) {
      throw( 'Score is required' );
    }
    /* if score is not within range, fail here */
    if( data.score < 1 || data.score > 4 ) {
      throw( 'Score must be from 1 to 4' );
    }
  } catch( message ) {
    /* Riak expects the following JSON if a failure occurs */
    return { "fail" : message };
  }
  /* No problems found, so continue */
  return object;
}
```

```bash
# restart each node so it loads the new .js file, then attach the hook to the bucket
curl -X PUT http://localhost:8091/riak/animals \
  -H "content-type:application/json" \
  -d '{"props":{"precommit":[{"name" : "good_score"}]}}'

curl -i -X PUT http://localhost:8091/riak/animals/bruiser \
  -H "Content-Type: application/json" -d '{"score" : 5}'
# HTTP/1.1 403 Forbidden
# Score must be from 1 to 4
```

The message after 403 is the text from the `fail` field. Bruiser keeps its previous score (3); a write with a score of 2 succeeds.

:::fig **A pre-commit hook guards the bucket.** Every write to `animals` passes through `good_score` before it is stored. A value with a missing score, or a score outside 1 to 4, is turned away with 403 Forbidden. Post-commit hooks run after storage and cannot reject anything; in Riak they had to be written in Erlang.
<svg class="dg" viewBox="0 0 720 180">
<rect x="10" y="60" width="160" height="60" rx="8" class="box"/><text x="90" y="86" text-anchor="middle" class="b mono">PUT /animals/x</text><text x="90" y="106" text-anchor="middle" class="s">from any client</text>
<line x1="172" y1="90" x2="236" y2="90" class="ln" marker-end="url(#arr)"/>
<rect x="240" y="50" width="170" height="80" rx="10" class="bv"/><text x="325" y="80" text-anchor="middle" class="b">precommit</text><text x="325" y="102" text-anchor="middle" class="mono s">good_score(obj)</text>
<line x1="412" y1="75" x2="490" y2="40" class="lgr" marker-end="url(#arrg)"/>
<line x1="412" y1="105" x2="490" y2="140" class="lr" marker-end="url(#arrr)"/>
<rect x="494" y="14" width="210" height="52" rx="8" class="bg"/><text x="599" y="36" text-anchor="middle" class="b">score 1 to 4</text><text x="599" y="54" text-anchor="middle" class="s">stored, then postcommit runs</text>
<rect x="494" y="114" width="210" height="52" rx="8" class="br"/><text x="599" y="136" text-anchor="middle" class="b tr">bad or missing score</text><text x="599" y="154" text-anchor="middle" class="s">403 Forbidden, nothing stored</text>
</svg>
:::

### Step 4: Riak Search

Riak's weak spot is querying by anything other than the key. **Riak Search** fixes part of that. When enabled (`{riak_search, [{enabled, true}]}` in `app.config`) and attached to a bucket, it reads every value as it is written and builds an **inverted index** of its fields, the same idea as PostgreSQL's GIN index from Chapter 2. It answers queries through an interface compatible with **Apache Solr**, the popular search server:

```bash
bin/search-cmd install animals     # install the indexing hook on the bucket

curl -X PUT http://localhost:8091/riak/animals/dragon \
  -H "Content-Type: application/json" \
  -d '{"nickname" : "Dragon", "breed" : "Briard", "score" : 1 }'
curl -X PUT http://localhost:8091/riak/animals/ace \
  -H "Content-Type: application/json" \
  -d '{"nickname" : "The Wonder Dog", "breed" : "German Shepherd", "score" : 3 }'

curl http://localhost:8091/solr/animals/select?q=breed:Shepherd
# returns XML describing Ace
```

The query language supports wildcards (`breed:Shep*`), ranges (`score:[2 TO 5]`), boolean logic (`breed:Shepherd AND score:3`), and paging and sorting with `start`, `rows` and `sort` parameters. You can also define a **schema** for a bucket so that, for example, `score` is indexed as an integer (which makes numeric ranges work properly).

### Step 5: Secondary indexes (2i)

A lighter option is **secondary indexing**: you tag a value with extra index entries when you write it, using `x-riak-index-*` headers, then look values up by those entries. Index names end in `_bin` (binary/string) or `_int` (integer). This requires the `eleveldb` storage backend.

```bash
curl -X PUT http://localhost:8098/riak/animals/blue \
  -H "Content-Type: application/json" \
  -H "x-riak-index-mascot_bin: butler" \
  -H "x-riak-index-version_int: 4" \
  -d '{"nickname" : "Blue", "breed" : "English Bulldog"}'

curl http://localhost:8098/riak/animals/index/mascot_bin/butler
# {"keys":["blue"]}
```

| | Riak Search | Secondary indexes (2i) |
|---|---|---|
| What gets indexed | Every field, automatically | Only the index entries you add in headers |
| Queries | Full-text, wildcards, ranges, boolean | Exact match or range on one index |
| Cost | Heavier: maintains a full-text index | Light |

### Day 3 homework, solved

**1. An index schema where `score` is an integer, then a range query.** In the Riak Search of the book, a bucket's schema is an Erlang-term file installed with `search-cmd set-schema`:

```erlang
{
  schema,
  [
    {version, "1.1"},
    {default_field, "nickname"},
    {default_op, "or"},
    {n_val, 3},
    {analyzer_factory, {erlang, text_analyzers, whitespace_analyzer_factory}}
  ],
  [
    {field, [{name, "nickname"}, {type, string}, {analyzer_factory, {erlang, text_analyzers, standard_analyzer_factory}}]},
    {field, [{name, "breed"},    {type, string}, {analyzer_factory, {erlang, text_analyzers, standard_analyzer_factory}}]},
    {field, [{name, "score"},    {type, integer}]},
    {dynamic_field, [{name, "*"}, {skip, true}]}
  ]
}
```

```bash
bin/search-cmd set-schema animals animals.def
# re-store the animals so they are re-indexed, then:
curl "http://localhost:8091/solr/animals/select?q=score:[2%20TO%205]"
```

**2. A three-server cluster.** Install Riak on three machines, set each node's name and listen address in its config (for example `riak@10.0.0.1`), start them, then from the second and third run `riak-admin join riak@10.0.0.1`. `riak-admin member_status` shows all three sharing the ring. (On Riak 1.2 and later the join is staged: `riak-admin cluster join ...`, then `cluster plan` and `cluster commit`.)

## Wrap-up · Strengths and weaknesses

Riak is a **distributed, data-replicating, enhanced key-value store with no single point of failure**. If you only know relational databases it may feel alien: no transactions, no SQL, no schema, links that are nothing like joins, and mapreduce instead of queries. For a certain class of problems, the trade is worth it. Riak scales out by adding servers, and builds on HTTP instead of reinventing a protocol, so any web-capable system can use it.

### Strengths

- **High availability above all.** Designing a huge ordering system like Amazon's, or anything where uptime is the top priority? Consider Riak. It removes single points of failure and grows or shrinks to meet demand.
- **Simple when your data is simple**, with mapreduce for deeper digging when needed.
- **Many client languages**, plus a faster binary protocol (Protocol Buffers) if HTTP is too slow, and full extensibility in Erlang.

### Weaknesses

- If you need **simple ad hoc queries**, **complex data structures**, a **rigid schema**, or you do not need to scale horizontally, Riak is probably the wrong choice.
- The authors' main complaint: no easy, robust **ad hoc query** framework. Mapreduce is powerful but heavy for everyday questions. Indexing was a step in the right direction.
- JavaScript (instead of Erlang) brings limits: no post-commit hooks, slower mapreduce.

### Riak and CAP

Most databases pick one corner of the CAP trade-off (see the CAP appendix). Riak's trick, straight from the Dynamo paper, is to let you choose **per bucket or even per request** with N, R and W. The same cluster can serve shopping carts with `w=1` (always accept writes) and account balances with `r=all` (always consistent). The authors find this flexibility impressive compared with systems like PostgreSQL that offer essentially one behavior.

### Parting thoughts

For a huge catalog of data, Riak is a strong choice. Not every problem needs ACID or a schema. But if you need to embed a database in a device, or handle financial transactions, avoid Riak. If you need to scale out and serve lots of data on the web, take a look.

:::modern Riak in 2026
Riak's story changed after the book:
- **Basho, the company behind Riak, collapsed in 2017.** The betting company **bet365**, a heavy Riak user, bought its assets and released everything (including the formerly paid multi-datacenter replication) as open source under the Apache 2.0 licence. Riak KV is now maintained by a small community (the 3.x series, with releases continuing at least into late 2024), but it is a niche product rather than a growing one.
- **Riak 2.0 (2014) changed many Day 1 to Day 3 details.** It introduced **bucket types**, made **JavaScript mapreduce, link walking and the old Riak Search deprecated**, and replaced search with **Yokozuna**, a real embedded Apache Solr (itself later deprecated).
- **CRDTs** (Conflict-free Replicated Data Types) arrived in Riak 2.0: counters, sets, maps and flags that merge concurrent updates automatically, so many sibling conflicts never reach your code.
- **Dynamo's ideas are everywhere.** Consistent hashing rings, N/R/W quorums, hinted handoff and sloppy quorums live on in **Apache Cassandra**, **ScyllaDB** and Amazon's managed **DynamoDB** (which, despite the name, has a different internal design from the 2007 paper). What you learned in this chapter transfers directly to them.
:::

:::key Chapter 3 in a nutshell
- **Data model:** buckets of keys; values are any bytes, described by a MIME type. Talk to it with HTTP: `PUT`, `GET`, `POST`, `DELETE`.
- **Links** are one-way tagged pointers between values; **link walking** follows them with `/bucket,tag,keep` steps.
- **Mapreduce** runs `map` on every value where it lives and `reduce` to combine results; reduce must be re-reducible. **Key filters** narrow inputs by key.
- **The ring:** consistent hashing spreads keys over partitions owned by nodes in turn; each value goes to the next **N** partitions.
- **N/R/W** tune copies, read quorum and write quorum per bucket or request; **R + W > N** means reads see the latest write.
- **Vector clocks** detect concurrent updates and keep **siblings** for the client to resolve; **hooks** validate writes; **Riak Search** and **2i** add querying.
:::

@@quiz
Q: What is the address of the value stored under key `ace` in bucket `animals` on the first dev node?
- `http://localhost:8091/animals?key=ace`
+ `http://localhost:8091/riak/animals/ace`
- `http://localhost:8091/riak/ace/animals`
- `riak://animals/ace`
? Riak exposes every value as a REST resource: `/riak/<bucket>/<key>`. The node's port comes first, then the bucket, then the key.

Q: What happens when you POST a JSON value to `http://localhost:8091/riak/animals` without a key?
- Riak rejects the request because every value needs a key
- Riak overwrites a random existing key
+ Riak generates a key and returns it in the `Location` header
- Riak stores it under the key `null`
? POST to a bucket means "create a new resource here". Riak invents the key and tells you where it put the value.

Q: What does this link-walking URL return?
C: /riak/cages/2/_,next_to,0/animals,_,_
- Every animal in the animals bucket
- Cage 2 and cage 1
+ The animals contained in the cage next to cage 2 (Polly), without returning the intermediate cage
- Only the cages that have a next_to link
? Start at cage 2, follow `next_to` links to cage 1 (keep=0, so not returned), then follow any link into the animals bucket. The last step is kept, so Polly is returned.

Q: Why must a Riak reduce function return data in the same shape it receives?
+ Riak may call reduce several times, including on the output of earlier reduce calls
- Because JSON requires it
- Because map functions run after reduce functions
- So that the result can be stored back in the bucket
? Reduce can be run on partial batches and then re-run on those partial results (re-reduce). If the output shape differs from the input shape, the second pass breaks.

Q: With consistent hashing, what is the main benefit when a new node joins the cluster?
- Every key is rehashed, so data is perfectly balanced
+ Only the partitions the new node claims are moved; most keys stay where they are
- The new node becomes the master
- Nothing moves until the cluster is restarted
? With `hash mod nodes`, adding a node remaps almost every key. With a ring of fixed partitions, the new node simply takes over some partitions, so only that data moves.

Q: N = 3. Which setting guarantees that a successful read sees the latest successful write?
- R = 1, W = 1
- R = 1, W = 2
+ R = 2, W = 2
- R = 0, W = 3
? Reads are guaranteed to overlap with the latest write when R + W > N. 2 + 2 = 4 > 3, so at least one node consulted by the read has the newest value.

Q: A node holding a replica is down and a write arrives for it. What does Riak do by default?
- Rejects the write until the node returns
+ Another node accepts the write on its behalf and hands it over when the node returns (hinted handoff)
- Writes it to a log that an administrator must replay
- Drops the write silently
? Hinted handoff, from the Dynamo paper, keeps writes available during failures. The stand-in node stores a hint and transfers the data later.

Q: Why does Riak use vector clocks rather than timestamps to order updates?
- Timestamps take more storage
+ Clocks on different machines drift, so timestamps cannot reliably tell which update came first; vector clocks track causal history instead
- HTTP does not allow timestamps
- Vector clocks are required by Erlang
? Synchronizing clocks across a cluster is unreliable. Vector clocks record which version each update started from, so Riak can tell a normal update from two concurrent ones.

Q: Two clients update the same key concurrently in a bucket with `allow_mult: true`. What does the next GET return?
- The value with the larger score
- The value written last
+ `300 Multiple Choices`, listing the sibling versions for the client to resolve
- `409 Conflict`, and both writes are discarded
? Riak keeps both versions as siblings and returns 300 Multiple Choices. A client resolves the conflict by writing a new value with the vector clock it received.

Q: How can a pre-commit hook reject a write?
- By throwing an Erlang exception that crashes the node
+ By returning a JSON object like `{"fail": "Score must be from 1 to 4"}`, which Riak turns into a 403 Forbidden
- By deleting the bucket
- By returning `false`
? A JavaScript pre-commit function either returns the (possibly modified) object to accept it, or `{"fail": message}` to reject it.

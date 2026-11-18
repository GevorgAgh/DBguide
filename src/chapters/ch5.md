title: MongoDB
lead: A document database built for huge data that still feels familiar to SQL users. Documents, rich queries and updates on Day 1; indexes, aggregation and mapreduce on Day 2; replica sets, sharding, geospatial queries and GridFS on Day 3.

## Overview: hu(mongo)us

MongoDB takes its name from "hu**mongo**us". It was designed to handle **huge amounts of data and requests**, through replication and horizontal scaling, while staying easy to use. The authors describe it as a database that fills the gap between the flexibility of key-value stores and the query power of relational databases.

What makes it attractive:

- **Documents instead of rows.** A document is a JSON object with an ID. It can contain lists and nested objects, so data that would need several SQL tables and joins can live in one document.
- **No schema.** Two documents in the same collection may have different fields. Adding a field needs no migration.
- **Rich, ad hoc queries** on any field, at any depth of nesting, with indexes to make them fast.
- **Consistency:** after you write a value, the next read returns it (unlike eventually consistent stores such as Riak).
- **JavaScript everywhere:** the shell is JavaScript, queries are JavaScript objects, mapreduce functions are JavaScript.

:::fig **Relational rows versus a MongoDB document.** In SQL, a town with several famous things and a mayor needs three tables joined back together. In MongoDB it is one document with an array and a nested object, read in a single operation.
<svg class="dg wide" viewBox="0 0 720 290">
<text x="170" y="22" text-anchor="middle" class="b ta">Relational: 3 tables</text>
<rect x="10" y="36" width="178" height="78" rx="6" class="ba"/>
<text x="20" y="56" class="s b">towns</text>
<text x="20" y="76" class="mono s">1 | Portland | 582000</text>
<text x="20" y="96" class="mono s">2 | New York | 22200000</text>
<rect x="204" y="36" width="150" height="98" rx="6" class="ba"/>
<text x="214" y="56" class="s b">famous_for</text>
<text x="214" y="76" class="mono s">1 | beer</text><text x="214" y="96" class="mono s">1 | food</text><text x="214" y="116" class="mono s">2 | statue …</text>
<rect x="10" y="134" width="178" height="78" rx="6" class="ba"/>
<text x="20" y="154" class="s b">mayors</text>
<text x="20" y="174" class="mono s">1 | Sam Adams | D</text><text x="20" y="194" class="mono s">2 | M. Bloomberg | I</text>
<line x1="188" y1="76" x2="204" y2="76" class="ln2"/><line x1="90" y1="114" x2="90" y2="132" class="ln2"/>
<text x="175" y="246" text-anchor="middle" class="s">joined at read time</text>
<line x1="365" y1="20" x2="365" y2="270" class="ln2 dash"/>
<text x="545" y="22" text-anchor="middle" class="b tg">MongoDB: 1 document</text>
<rect x="390" y="36" width="320" height="196" rx="8" class="bg"/>
<g class="mono s">
<text x="404" y="60">{</text>
<text x="416" y="80">_id: ObjectId("4d0b6da3…"),</text>
<text x="416" y="100">name: "Portland",</text>
<text x="416" y="120">population: 582000,</text>
<text x="416" y="140">famous_for: [ "beer", "food" ],</text>
<text x="416" y="160">mayor: {</text>
<text x="432" y="180">name: "Sam Adams",</text>
<text x="432" y="200">party: "D" }</text>
<text x="404" y="220">}</text>
</g>
<text x="545" y="258" text-anchor="middle" class="s">array and nested object live inside the document</text>
</svg>
:::

| SQL term | MongoDB term |
|---|---|
| Database | Database |
| Table | **Collection** |
| Row | **Document** |
| Column | **Field** |
| Primary key | `_id` field |
| Join | Embedding or manual references (no server-side joins in 2012) |

## Day 1 · CRUD and nesting

### Step 1: The shell and your first document

```bash
mongo book         # open the shell, using a database named "book"
```

Databases and collections are created automatically the first time you write to them. Insert a town:

```javascript
db.towns.insert({
  name: "New York",
  population: 22200000,
  last_census: ISODate("2009-07-31"),
  famous_for: [ "statue of liberty", "food" ],
  mayor : {
    name : "Michael Bloomberg",
    party : "I"
  }
})
```

```javascript
> show collections
system.indexes
towns

> db.towns.find()
{ "_id" : ObjectId("4d0ad975bb30773266f39fe3"),
  "name" : "New York", "population": 22200000, ... }
```

Notice what you get without asking: the `towns` collection, and an `_id` field holding an **ObjectId**.

### Step 2: The ObjectId

Every document needs a unique `_id`. If you do not supply one, MongoDB generates an **ObjectId**: a 12-byte value that is unique across machines **without any coordination**, which matters when many servers create documents at the same time.

:::fig **Anatomy of an ObjectId** (as described in the book). Because it starts with a timestamp, ObjectIds sort roughly by creation time, and you can read the creation time back out of one. The other parts make collisions between machines and processes practically impossible.
<svg class="dg" viewBox="0 0 720 150">
<g class="mono">
<rect x="40" y="30" width="200" height="50" rx="6" class="bg"/><text x="140" y="61" text-anchor="middle">4d0ad975</text>
<rect x="240" y="30" width="150" height="50" rx="6" class="ba"/><text x="315" y="61" text-anchor="middle">bb3077</text>
<rect x="390" y="30" width="100" height="50" rx="6" class="bw"/><text x="440" y="61" text-anchor="middle">3266</text>
<rect x="490" y="30" width="150" height="50" rx="6" class="bv"/><text x="565" y="61" text-anchor="middle">f39fe3</text>
</g>
<text x="140" y="104" text-anchor="middle" class="b">4 bytes</text><text x="140" y="122" text-anchor="middle" class="s">timestamp (seconds)</text>
<text x="315" y="104" text-anchor="middle" class="b">3 bytes</text><text x="315" y="122" text-anchor="middle" class="s">machine id</text>
<text x="440" y="104" text-anchor="middle" class="b">2 bytes</text><text x="440" y="122" text-anchor="middle" class="s">process id</text>
<text x="565" y="104" text-anchor="middle" class="b">3 bytes</text><text x="565" y="122" text-anchor="middle" class="s">counter</text>
</svg>
:::

### Step 3: It is all JavaScript

The shell is a JavaScript interpreter, and `db` is an ordinary JavaScript object:

```javascript
> typeof db                 // object
> typeof db.towns           // object
> typeof db.towns.insert    // function
> db.towns.insert           // without (): prints the function's source code!
> db.help()                 // list database methods
> db.towns.help()           // list collection methods
```

Since it is JavaScript, you can write helper functions. The book adds a function to insert towns, then uses it:

```javascript
function insertCity(name, population, last_census, famous_for, mayor_info) {
  db.towns.insert({
    name: name,
    population: population,
    last_census: ISODate(last_census),
    famous_for: famous_for,
    mayor : mayor_info
  });
}

insertCity("Punxsutawney", 6200, '2008-01-31',
           ["phil the groundhog"], { name : "Jim Wehrle" })
insertCity("Portland", 582000, '2007-09-20',
           ["beer", "food"], { name : "Sam Adams", party : "D" })
```

Notice that Punxsutawney's mayor has no `party` field. No schema, no problem.

### Step 4: Reading with find()

```javascript
// by _id
db.towns.find({ "_id" : ObjectId("4d0ada1fbb30773266f39fe4") })

// choose fields to return (a "projection"): 1 = include, 0 = exclude
db.towns.find({ _id : ObjectId("4d0ada1fbb30773266f39fe4") }, { name : 1 })
db.towns.find({ _id : ObjectId("4d0ada1fbb30773266f39fe4") }, { name : 0 })

// criteria: names starting with P and population under 10,000
db.towns.find(
  { name : /^P/, population : { $lt : 10000 } },
  { name : 1, population : 1 }
)
// { "name" : "Punxsutawney", "population" : 6200 }
```

A query is itself a document. Fields you list must all match (an implicit **AND**). **Operators** start with `$`:

| Operator | Meaning | Example |
|---|---|---|
| `$lt`, `$lte`, `$gt`, `$gte` | less than / greater than (or equal) | `{ population: { $gt: 10000 } }` |
| `$ne` | not equal | `{ name: { $ne: "Portland" } }` |
| `$in`, `$nin` | value is / is not in a list | `{ famous_for: { $in: ["beer","food"] } }` |
| `$all` | array contains all of these | `{ famous_for: { $all: ["food","beer"] } }` |
| `$exists` | field is present or absent | `{ "mayor.party": { $exists: false } }` |
| `$size` | array has exactly n elements | `{ famous_for: { $size: 2 } }` |
| `$regex` or `/.../` | regular expression | `{ name: /^New/ }` |
| `$elemMatch` | one array element matches all conditions | see Step 6 |
| `$or`, `$and`, `$not`, `$nor` | boolean logic | `{ $or: [ {_id:"mx"}, {name:"United States"} ] }` |

Because queries are plain objects, you can build them with code:

```javascript
var population_range = {};
population_range['$lt'] = 1000000;
population_range['$gt'] = 10000;
db.towns.find({ name : /^P/, population : population_range }, { name : 1 })
// { "name" : "Portland" }
```

### Step 5: Querying arrays and nested documents

**Arrays** are matched element by element: if any element matches, the document matches.

```javascript
db.towns.find({ famous_for : 'food' }, { _id : 0, name : 1, famous_for : 1 })
// New York and Portland

db.towns.find({ famous_for : /statue/ }, { _id : 0, name : 1 })               // New York
db.towns.find({ famous_for : { $all : ['food', 'beer'] } }, { name : 1 })     // Portland
db.towns.find({ famous_for : { $nin : ['food', 'beer'] } }, { name : 1 })     // Punxsutawney
```

**Nested documents** are reached with **dot notation**, in quotes:

```javascript
db.towns.find({ 'mayor.party' : 'I' }, { _id : 0, name : 1, mayor : 1 })          // New York
db.towns.find({ 'mayor.party' : { $exists : false } }, { _id : 0, name : 1 })    // Punxsutawney
```

### Step 6: $elemMatch, matching inside one array element

The book's clearest lesson about arrays uses a `countries` collection, where each country lists the foods it exports:

```javascript
db.countries.insert({ _id : "us", name : "United States",
  exports : { foods : [ { name : "bacon", tasty : true },
                        { name : "burgers" } ] } })
db.countries.insert({ _id : "ca", name : "Canada",
  exports : { foods : [ { name : "bacon", tasty : false },
                        { name : "syrup", tasty : true } ] } })
db.countries.insert({ _id : "mx", name : "Mexico",
  exports : { foods : [ { name : "salsa", tasty : true, condiment : true } ] } })
```

Question: **which countries export tasty bacon?**

```javascript
db.countries.find(
  { 'exports.foods.name' : 'bacon', 'exports.foods.tasty' : true },
  { _id : 0, name : 1 }
)
// United States AND Canada  ← surprising!
```

Canada matches because **one** element is named bacon and **another** element (syrup) is tasty. Each condition was satisfied by a different element. `$elemMatch` requires **one element** to satisfy all conditions:

```javascript
db.countries.find(
  { 'exports.foods' : { $elemMatch : { name : 'bacon', tasty : true } } },
  { _id : 0, name : 1 }
)
// United States only
```

:::fig **Why Canada matched without $elemMatch.** Without it, each condition may be satisfied by a different element of the array. With `$elemMatch`, a single element must satisfy every condition at once.
<svg class="dg wide" viewBox="0 0 720 230">
<text x="180" y="22" text-anchor="middle" class="b">Canada's exports.foods</text>
<rect x="20" y="36" width="160" height="70" rx="8" class="box"/><text x="100" y="62" text-anchor="middle" class="mono">name: "bacon"</text><text x="100" y="84" text-anchor="middle" class="mono">tasty: false</text>
<rect x="190" y="36" width="160" height="70" rx="8" class="box"/><text x="270" y="62" text-anchor="middle" class="mono">name: "syrup"</text><text x="270" y="84" text-anchor="middle" class="mono">tasty: true</text>
<text x="20" y="140" class="b">plain query</text>
<text x="20" y="160" class="s">name = bacon? element 1 ✓</text>
<text x="20" y="178" class="s">tasty = true? element 2 ✓</text>
<text x="20" y="200" class="tr b">→ Canada matches (wrong)</text>
<line x1="100" y1="108" x2="100" y2="146" class="lr dash"/><line x1="270" y1="108" x2="200" y2="166" class="lr dash"/>
<line x1="380" y1="20" x2="380" y2="215" class="ln2 dash"/>
<text x="550" y="22" text-anchor="middle" class="b">with $elemMatch</text>
<rect x="420" y="36" width="260" height="70" rx="8" class="bg"/>
<text x="550" y="62" text-anchor="middle" class="s">one element must have</text>
<text x="550" y="84" text-anchor="middle" class="mono">name: "bacon" AND tasty: true</text>
<text x="420" y="140" class="s">Canada: bacon is not tasty; syrup is not bacon</text>
<text x="420" y="160" class="s">United States: { bacon, tasty: true } ✓</text>
<text x="420" y="200" class="tg b">→ United States only (right)</text>
</svg>
:::

Boolean operators combine conditions. Plain fields are AND-ed; `$or` takes a list:

```javascript
db.countries.find({ $or : [ { _id : "mx" }, { name : "United States" } ] }, { _id : 1 })
// mx, us
```

### Step 7: Updating documents

`update(criteria, operation)` changes the **first** matching document (add a fourth argument `true`, or `{multi: true}`, to change all matches).

```javascript
db.towns.update(
  { _id : ObjectId("4d0ada87bb30773266f39fe5") },
  { $set : { "state" : "OR" } }
);
db.towns.update(
  { _id : ObjectId("4d0ada87bb30773266f39fe5") },
  { $inc : { population : 1000 } }
);
```

:::warn Forgetting $set replaces the whole document
`db.towns.update({_id: ...}, { state: "OR" })` (without `$set`) does not add a field. It **replaces the entire document** with `{ state: "OR" }`, and Portland's name, population, mayor and everything else are gone. This is one of the most common MongoDB mistakes.
:::

:::fig **The two kinds of update.** With an operator such as `$set`, only the named field changes. With a plain document as the second argument, MongoDB replaces everything except `_id`.
<svg class="dg wide" viewBox="0 0 720 210">
<rect x="10" y="60" width="180" height="100" rx="8" class="box"/>
<g class="mono s"><text x="22" y="84">name: "Portland"</text><text x="22" y="104">population: 582000</text><text x="22" y="124">mayor: {…}</text><text x="22" y="144">famous_for: […]</text></g>
<line x1="192" y1="90" x2="356" y2="62" class="lgr" marker-end="url(#arrg)"/>
<line x1="192" y1="130" x2="356" y2="166" class="lr" marker-end="url(#arrr)"/>
<text x="272" y="58" text-anchor="middle" class="s mono">{$set:{state:"OR"}}</text>
<text x="272" y="184" text-anchor="middle" class="s mono">{state:"OR"}</text>
<rect x="360" y="10" width="220" height="110" rx="8" class="bg"/>
<g class="mono s"><text x="372" y="32">name: "Portland"</text><text x="372" y="50">population: 582000</text><text x="372" y="68">mayor: {…}</text><text x="372" y="86">famous_for: […]</text><text x="372" y="104" class="tg b">state: "OR"</text></g>
<rect x="360" y="140" width="220" height="56" rx="8" class="br"/>
<g class="mono s"><text x="372" y="162">_id: …</text><text x="372" y="182" class="tr b">state: "OR"</text></g>
<text x="596" y="60" class="s">field added,</text><text x="596" y="76" class="s">rest kept</text>
<text x="596" y="164" class="s">everything else</text><text x="596" y="180" class="s">is gone</text>
</svg>
:::

| Update operator | Effect |
|---|---|
| `$set` / `$unset` | Set a field / remove a field. |
| `$inc` | Add a number to a field (atomic). |
| `$push` / `$pushAll` | Append a value / several values to an array. |
| `$addToSet` | Append only if not already present (set semantics). |
| `$pop` | Remove the first or last array element. |
| `$pull` / `$pullAll` | Remove matching values from an array. |

:::deep Why atomic operators matter
Imagine two web servers both incrementing a page's view count. If each one reads the document, adds 1 in application code and writes it back, one increment can be lost (both read 10, both write 11). `$inc` happens **inside the database**, atomically on that one document, so both increments land (10 → 12). The book points out this kind of atomic read-modify-write is part of what makes MongoDB feel safe to RDBMS users.
:::

### Step 8: References between documents

MongoDB has no server-side joins (in 2012), so you either **embed** related data inside a document or **reference** another document by its `_id`. The book uses a **DBRef**, a convention `{ $ref: collection, $id: id }`:

```javascript
db.towns.update(
  { _id : ObjectId("4d0ada87bb30773266f39fe5") },
  { $set : { country: { $ref: "countries", $id: "us" } } }
)

var portland = db.towns.findOne({ _id : ObjectId("4d0ada87bb30773266f39fe5") })
db.countries.findOne({ _id : portland.country.$id })
// or, without hard-coding the collection name:
db[ portland.country.$ref ].findOne({ _id : portland.country.$id })
```

The "join" happens in your code: two queries instead of one.

:::fig **Embed or reference?** Embed data that belongs to one parent and is read with it (a town's mayor). Reference data that is shared by many documents or large on its own (the country many towns belong to). Referencing costs an extra query; embedding duplicates shared data.
<svg class="dg wide" viewBox="0 0 720 220">
<text x="170" y="22" text-anchor="middle" class="b">embed</text>
<rect x="30" y="36" width="280" height="150" rx="8" class="bg"/>
<text x="46" y="60" class="mono s">town "Portland"</text>
<rect x="56" y="74" width="230" height="90" rx="6" class="box"/>
<text x="70" y="98" class="mono s">mayor: {</text><text x="86" y="118" class="mono s">name: "Sam Adams",</text><text x="86" y="138" class="mono s">party: "D" }</text>
<text x="170" y="206" text-anchor="middle" class="s">one read, data travels together</text>
<line x1="360" y1="20" x2="360" y2="210" class="ln2 dash"/>
<text x="540" y="22" text-anchor="middle" class="b">reference</text>
<rect x="390" y="36" width="140" height="60" rx="8" class="bg"/><text x="460" y="60" text-anchor="middle" class="mono s">"Portland"</text><text x="460" y="80" text-anchor="middle" class="mono s">country: us</text>
<rect x="390" y="120" width="140" height="60" rx="8" class="bg"/><text x="460" y="144" text-anchor="middle" class="mono s">"New York"</text><text x="460" y="164" text-anchor="middle" class="mono s">country: us</text>
<rect x="580" y="78" width="120" height="60" rx="8" class="ba"/><text x="640" y="102" text-anchor="middle" class="mono s">countries</text><text x="640" y="122" text-anchor="middle" class="mono s">_id: "us"</text>
<line x1="532" y1="72" x2="576" y2="100" class="la" marker-end="url(#arra)"/>
<line x1="532" y1="146" x2="576" y2="118" class="la" marker-end="url(#arra)"/>
<text x="540" y="206" text-anchor="middle" class="s">shared data stored once, extra query</text>
</svg>
:::

### Step 9: Deleting documents

`remove(criteria)` deletes **every** matching document. The book's advice: run `find()` with the same criteria first, and only then `remove()`:

```javascript
var bad_bacon = {
  'exports.foods' : { $elemMatch : { name : 'bacon', tasty : false } }
}
db.countries.find( bad_bacon )      // check: Canada
db.countries.remove( bad_bacon )
db.countries.count()                // 2
```

### Step 10: Queries written as code ($where)

When operators are not enough, you can pass a JavaScript function (or a string) that returns true for documents you want:

```javascript
db.towns.find( function() {
  return this.population > 6000 && this.population < 600000;
})
db.towns.find("this.population > 6000 && this.population < 600000")

// mix with normal criteria so an index can narrow the set first
db.towns.find({
  $where : "this.population > 6000 && this.population < 600000",
  famous_for : /groundhog/
})
```

:::warn Code queries are slow
A `$where` function must be run on **every document**: it cannot use indexes, and each call runs JavaScript. If one document lacks the field (for example `population` is missing), the function can throw an error and the whole query fails. Use it as a last resort, combined with normal criteria that narrow the set first.
:::

### Day 1 homework, solved

```javascript
// 1. print a JSON document
printjson({ "hello" : "world" })

// 2. towns containing "new", case-insensitive
db.towns.find({ name : /new/i })

// 3. cities whose names contain an "e" and are famous for food or beer
db.towns.find({ name : /e/, famous_for : { $in : ['food', 'beer'] } })

// 4. a blogger database with an article
use blogger
db.articles.insert({
  author_name : "Ann Writer",
  email : "ann@example.com",
  created_at : new Date(),
  text : "My first post about MongoDB."
})

// 5. add an array of comments
db.articles.update(
  { author_name : "Ann Writer" },
  { $push : { comments : { author : "Bob", text : "Great post!" } } }
)

// 6. run a query from an external file
//    $ mongo blogger my_query.js
```

The "Find" answers: the online docs at mongodb.org; regular expressions use JavaScript syntax `/pattern/flags` or `{ $regex: "pattern", $options: "i" }`; `db.help()` and `db.collection.help()` list methods; drivers exist for almost every language.

## Day 2 · Indexing, grouping and mapreduce

### Step 1: A big collection to work with

To see indexes matter, the book generates **100,000 fake phone numbers** with a stored helper:

```javascript
populatePhones = function(area, start, stop) {
  for(var i = start; i < stop; i++) {
    var country = 1 + ((Math.random() * 8) << 0);
    var num = (country * 1e10) + (area * 1e7) + i;
    db.phones.insert({
      _id: num,
      components: { country: country, area: area, prefix: (i * 1e-4) << 0, number: i },
      display: "+" + country + " " + area + "-" + i
    });
  }
}
populatePhones( 800, 5550000, 5650000 )
db.phones.find().limit(2)
// { "_id" : 18005550000, "components" : { "country" : 1, "area" : 800,
//   "prefix" : 555, "number" : 5550000 }, "display" : "+1 800-5550000" }
```

### Step 2: Indexes and explain()

Every collection has an index on `_id` automatically. Indexes are listed in `db.system.indexes`. To see how a query runs, add `.explain()`:

```javascript
db.phones.find({ display: "+1 800-5650001" }).explain()
// { "cursor" : "BasicCursor", "nscanned" : 109999, "nscannedObjects" : 109999,
//   "n" : 1, "millis" : 52, ... }
```

`BasicCursor` means a full collection scan: it looked at all 109,999 documents to find 1. Add an index:

```javascript
db.phones.ensureIndex(
  { display : 1 },
  { unique : true, dropDups : true }
)
db.phones.find({ display: "+1 800-5650001" }).explain()
// { "cursor" : "BtreeCursor display_1", "nscanned" : 1, "n" : 1, "millis" : 0, ... }
```

- `{ display: 1 }` means ascending order (`-1` is descending, which matters for multi-field indexes and sorting).
- `unique: true` rejects duplicates; `dropDups: true` deletes existing duplicates while building.
- MongoDB indexes are **B-trees**, just like PostgreSQL's default.

:::fig **One index, a huge difference.** Without an index, MongoDB scanned 109,999 documents to find one phone number. With a B-tree index on `display`, it read exactly one.
<svg class="dg" viewBox="0 0 720 160">
<text x="10" y="40" class="b">no index</text><text x="10" y="58" class="s mono">BasicCursor</text>
<rect x="200" y="26" width="500" height="34" rx="4" class="br"/>
<text x="680" y="48" text-anchor="end" class="mono b">nscanned 109,999 · 52 ms</text>
<text x="10" y="112" class="b">with index</text><text x="10" y="130" class="s mono">BtreeCursor display_1</text>
<rect x="200" y="98" width="6" height="34" rx="2" class="fg"/>
<text x="218" y="120" class="mono b tg">nscanned 1 · 0 ms</text>
</svg>
:::

Indexes on **nested fields** use dot notation. Building an index on a big collection blocks writes, so the book builds it **in the background**:

```javascript
db.phones.ensureIndex({ "components.area": 1 }, { background : 1 })
```

The **profiler** records slow operations so you can find missing indexes:

```javascript
db.setProfilingLevel(2)          // 0 = off, 1 = slow operations only, 2 = everything
db.phones.find({ display : "+1 800-5650001" })
db.system.profile.find()         // shows each operation, how long it took, what it scanned
```

:::tip When to add an index
Index the fields you **filter**, **sort** and **look up** by often. Every index speeds up reads but slows down writes (each insert must update every index) and uses memory. `explain()` and the profiler tell you which queries need help.
:::

### Step 3: Aggregate queries

| Method | Example | Result |
|---|---|---|
| `count()` | `db.phones.count({'components.number': { $gt : 5599999 } })` | `50000` |
| `distinct()` | `db.phones.distinct('components.number', {'components.number': { $lt : 5550005 } })` | `[5550000, 5550001, 5550002, 5550003, 5550004]` |
| `group()` | see below | counts per group |

`group()` is MongoDB's (2012) answer to SQL's `GROUP BY`. Count phone numbers above 5,599,999 per area code:

```javascript
db.phones.group({
  initial: { count:0 },
  reduce: function(phone, output) { output.count++; },
  cond: { 'components.number': { $gt: 5599999 } },
  key: { 'components.area': true }
})
// [ { "components.area" : 800, "count" : 50000 }, ... ]
```

`group()` was limited: at most 10,000 groups, and it did not work on sharded collections. For bigger jobs, use mapreduce (Step 6).

### Step 4: Running code on the server

Normally your loop runs in the shell, and every document travels from the server to the shell and back. This function reformats every phone number, one round trip per document:

```javascript
update_area = function() {
  db.phones.find().forEach(
    function(phone) {
      phone.components.area++;
      phone.display = "+"+
        phone.components.country+" "+
        phone.components.area+"-"+
        phone.components.number;
      db.phones.update({ _id : phone._id }, phone, false);   // the book prints db.phone here, a typo
    }
  )
}
```

`db.eval(update_area)` sends the function to the **server** and runs it there, avoiding all that traffic (but in 2012 it also locked the database while it ran).

Every shell helper is a thin wrapper around a **command**: `db.phones.count()` actually calls `db.runCommand({ "count" : "phones" })`. Type a function name without parentheses to read its source and see this for yourself.

```javascript
use admin
db.runCommand("top")        // per-collection usage statistics
use book
db.listCommands()           // every command the server understands
db.runCommand({ "count" : "phones" })
```

You can also **store** JavaScript functions on the server, in the special `system.js` collection:

```javascript
db.system.js.save({
  _id: 'getLast',
  value: function(collection) {
    return collection.find({}).sort({'_id':1}).limit(1)[0]
  }
})
db.eval('getLast(db.phones)')
```

### Step 5: Mapreduce

The book's mapreduce job answers an odd but instructive question: **for each country, how many phone numbers use each set of distinct digits?** (`555-1213` uses the digits 1, 2, 3 and 5.)

First, a helper that returns the sorted distinct digits of a number, stored on the server so map can use it:

```javascript
distinctDigits = function(phone){
  var number = phone.components.number + '',
      seen = [], result = [], i = number.length;
  while(i--) { seen[+number[i]] = 1; }
  for (i=0; i<10; i++) { if (seen[i]) { result[result.length] = i; } }
  return result;
}
db.system.js.save({ _id: 'distinctDigits', value: distinctDigits })
```

**Map** emits one key per phone, a compound key of digits and country, with a count of 1:

```javascript
map = function() {
  var digits = distinctDigits(this);
  emit({ digits : digits, country : this.components.country }, { count : 1 });
}
```

**Reduce** adds up the counts for each key:

```javascript
reduce = function(key, values) {
  var total = 0;
  for(var i=0; i<values.length; i++) {
    total += values[i].count;
  }
  return { count : total };
}
```

```javascript
results = db.runCommand({
  mapReduce: 'phones',
  map: map,
  reduce: reduce,
  out: 'phones.report'           // write results into a new collection
})
db.phones.report.find({ '_id.country' : 8 })
// { "_id" : { "digits" : [ 0, 1, 2, 3, 4, 5, 6 ], "country" : 8 }, "value" : { "count" : 19 } }
// { "_id" : { "digits" : [ 0, 1, 2, 3, 5 ], "country" : 8 }, "value" : { "count" : 3 } }
// ...
```

:::fig **The phone-number mapreduce.** Map turns every phone into a (key, {count: 1}) pair, where the key combines its distinct digits and its country. MongoDB groups pairs by key and reduce sums them, writing one document per key into `phones.report`.
<svg class="dg wide" viewBox="0 0 720 250">
<text x="80" y="20" text-anchor="middle" class="b">phones</text>
<g class="mono s">
<rect x="10" y="32" width="140" height="34" rx="5" class="box"/><text x="20" y="54">+8 800-5551213</text>
<rect x="10" y="74" width="140" height="34" rx="5" class="box"/><text x="20" y="96">+8 800-5552131</text>
<rect x="10" y="116" width="140" height="34" rx="5" class="box"/><text x="20" y="138">+8 800-5550123</text>
<rect x="10" y="158" width="140" height="34" rx="5" class="box"/><text x="20" y="180">+1 800-5551213</text>
</g>
<text x="290" y="20" text-anchor="middle" class="b">map: emit(key, {count:1})</text>
<g class="mono s">
<text x="190" y="54">{[1,2,3,5], c:8} → 1</text>
<text x="190" y="96">{[1,2,3,5], c:8} → 1</text>
<text x="190" y="138">{[0,1,2,3,5], c:8} → 1</text>
<text x="190" y="180">{[1,2,3,5], c:1} → 1</text>
</g>
<line x1="152" y1="49" x2="184" y2="49" class="ln" marker-end="url(#arr)"/><line x1="152" y1="91" x2="184" y2="91" class="ln" marker-end="url(#arr)"/>
<line x1="152" y1="133" x2="184" y2="133" class="ln" marker-end="url(#arr)"/><line x1="152" y1="175" x2="184" y2="175" class="ln" marker-end="url(#arr)"/>
<text x="575" y="20" text-anchor="middle" class="b">reduce: sum per key</text>
<rect x="450" y="40" width="260" height="34" rx="5" class="bg"/><text x="460" y="62" class="mono s">{[1,2,3,5], c:8} → count 2</text>
<rect x="450" y="116" width="260" height="34" rx="5" class="bg"/><text x="460" y="138" class="mono s">{[0,1,2,3,5], c:8} → count 1</text>
<rect x="450" y="158" width="260" height="34" rx="5" class="bg"/><text x="460" y="180" class="mono s">{[1,2,3,5], c:1} → count 1</text>
<line x1="400" y1="50" x2="446" y2="56" class="ln" marker-end="url(#arr)"/><line x1="400" y1="92" x2="446" y2="62" class="ln" marker-end="url(#arr)"/>
<line x1="420" y1="134" x2="446" y2="134" class="ln" marker-end="url(#arr)"/><line x1="410" y1="176" x2="446" y2="176" class="ln" marker-end="url(#arr)"/>
<text x="360" y="232" text-anchor="middle" class="s">results stored in the phones.report collection, one document per key</text>
</svg>
:::

:::warn Reduce may receive its own output
As in Riak, MongoDB can call reduce **several times** for the same key, feeding the result of one reduce into the next. That is why the map emits `{count: 1}` (not just `1`) and reduce returns `{count: total}`: the value has the same shape at every stage. A reduce that returned a bare number would break on the second pass.
:::

On a sharded cluster, the `mongos` router sends the mapreduce job to every shard; each shard maps and reduces its own data, then the partial results are reduced again into the final answer.

### Day 2 homework, solved

**Find:** `db._adminCommand(...)` is the shortcut for admin commands; type `db.phones.help`, `db.phones.findOne` or `db.phones.stats` without parentheses to read each function's source.

**Do 1. Add a finalize step** that outputs the count as `total`. `finalize` runs once per key after all reducing, so it is the right place to reshape the final value:

```javascript
finalize = function(key, value) {
  return { total : value.count };
}
db.runCommand({
  mapReduce: 'phones', map: map, reduce: reduce, finalize: finalize,
  out: 'phones.report'
})
db.phones.report.findOne()
// { "_id" : { "digits" : [ 0, 1, 2, 3, 4, 5, 6 ], "country" : 1 }, "value" : { "total" : 26 } }
```

**Do 2. Use a driver from your own language: connect, insert, index a field.** In Ruby with today's driver:

```ruby
require 'mongo'
client = Mongo::Client.new([ '127.0.0.1:27017' ], database: 'book')
client[:towns].insert_one(name: 'Yerevan', population: 1_090_000, famous_for: ['brandy'])
client[:towns].indexes.create_one(famous_for: 1)          # the homework also asks for an index
client[:towns].find(famous_for: 'brandy').each { |doc| puts doc['name'] }
```

## Day 3 · Replica sets, sharding, geospatial and GridFS

### Step 1: Replica sets

MongoDB keeps data safe by **replication**, not by writing every change to disk immediately (the default in 2012). A **replica set** is a group of `mongod` servers holding the same data: one **primary** accepts writes, the **secondaries** copy them.

```bash
mkdir ./mongo1 ./mongo2 ./mongo3
mongod --replSet book --dbpath ./mongo1 --port 27011 --rest
mongod --replSet book --dbpath ./mongo2 --port 27012 --rest
mongod --replSet book --dbpath ./mongo3 --port 27013 --rest
```

```javascript
// connect to one of them: mongo localhost:27011
rs.initiate({
  _id: 'book',
  members: [
    { _id: 1, host: 'localhost:27011' },
    { _id: 2, host: 'localhost:27012' },
    { _id: 3, host: 'localhost:27013' }
  ]
})
rs.status()      // shows one PRIMARY and two SECONDARY members
```

Write a document on the primary and it appears on the secondaries. Try to write on a secondary and you get an error (`not master`). Now **kill the primary**: within seconds the two survivors hold an **election** and one becomes the new primary.

:::fig **A replica set elects a new primary.** All writes go to the primary and are copied to secondaries. If the primary disappears, the remaining members vote; a member that gets a majority of the votes becomes the new primary and writes continue.
<svg class="dg wide" viewBox="0 0 720 240">
<text x="170" y="22" text-anchor="middle" class="b">normal operation</text>
<circle cx="170" cy="80" r="40" class="bg"/><text x="170" y="76" text-anchor="middle" class="b">primary</text><text x="170" y="94" text-anchor="middle" class="s">:27011</text>
<circle cx="90" cy="190" r="36" class="box"/><text x="90" y="186" text-anchor="middle" class="b">second.</text><text x="90" y="204" text-anchor="middle" class="s">:27012</text>
<circle cx="250" cy="190" r="36" class="box"/><text x="250" y="186" text-anchor="middle" class="b">second.</text><text x="250" y="204" text-anchor="middle" class="s">:27013</text>
<line x1="150" y1="115" x2="110" y2="156" class="ln" marker-end="url(#arr)"/><line x1="190" y1="115" x2="230" y2="156" class="ln" marker-end="url(#arr)"/>
<text x="56" y="128" class="s">replicate</text>
<line x1="60" y1="40" x2="128" y2="68" class="lgr" marker-end="url(#arrg)"/><text x="20" y="36" class="s tg b">writes</text>
<line x1="360" y1="20" x2="360" y2="225" class="ln2 dash"/>
<text x="545" y="22" text-anchor="middle" class="b">primary fails → election</text>
<circle cx="545" cy="80" r="40" class="br"/><text x="545" y="84" text-anchor="middle" class="b tr">down</text>
<circle cx="465" cy="190" r="36" class="bg"/><text x="465" y="186" text-anchor="middle" class="b">primary</text><text x="465" y="204" text-anchor="middle" class="s">2 votes</text>
<circle cx="625" cy="190" r="36" class="box"/><text x="625" y="186" text-anchor="middle" class="b">second.</text><text x="625" y="204" text-anchor="middle" class="s">votes</text>
<line x1="587" y1="190" x2="505" y2="190" class="la" marker-end="url(#arra)"/><text x="545" y="180" text-anchor="middle" class="s ta">vote</text>
<text x="545" y="140" text-anchor="middle" class="s">2 of 3 = majority</text>
</svg>
:::

:::deep What happens to writes the old primary never copied?
If the old primary accepted a write but crashed before any secondary copied it, the new primary never saw that write. When the old primary comes back, it rejoins as a secondary and **rolls back** those writes (saving them to a rollback file) to match the new primary. The book uses this to explain why acknowledgement settings matter: asking for a write to be confirmed by a majority of members (`getLastError` with `w`, today's **write concern** `w: "majority"`) prevents this kind of loss.
:::

#### Why an odd number of members?

An election needs a **majority of all members**, not just of the ones still reachable. This protects against two halves of a split network each electing their own primary ("split brain").

:::fig **The problem with even numbers.** With 4 members split 2 and 2 by a network failure, neither side has a majority (3), so nobody can be primary and writes stop. With 3 members (or 4 plus a lightweight **arbiter** that only votes), one side always has a majority.
<svg class="dg wide" viewBox="0 0 720 200">
<text x="170" y="22" text-anchor="middle" class="b tr">4 members, split 2 | 2</text>
<circle cx="70" cy="90" r="26" class="box"/><circle cx="130" cy="90" r="26" class="box"/>
<circle cx="210" cy="90" r="26" class="box"/><circle cx="270" cy="90" r="26" class="box"/>
<line x1="170" y1="50" x2="170" y2="130" class="lr" style="stroke-width:3px"/>
<text x="100" y="150" text-anchor="middle" class="s">2 of 4: no majority</text><text x="240" y="150" text-anchor="middle" class="s">2 of 4: no majority</text>
<text x="170" y="180" text-anchor="middle" class="tr b">no primary anywhere</text>
<line x1="360" y1="20" x2="360" y2="190" class="ln2 dash"/>
<text x="545" y="22" text-anchor="middle" class="b tg">3 members, split 2 | 1</text>
<circle cx="450" cy="90" r="26" class="bg"/><circle cx="510" cy="90" r="26" class="bg"/>
<circle cx="620" cy="90" r="26" class="box"/>
<line x1="565" y1="50" x2="565" y2="130" class="lr" style="stroke-width:3px"/>
<text x="480" y="150" text-anchor="middle" class="s">2 of 3: majority</text><text x="620" y="150" text-anchor="middle" class="s">1 of 3</text>
<text x="480" y="180" text-anchor="middle" class="tg b">elects a primary</text><text x="620" y="180" text-anchor="middle" class="s">read-only</text>
</svg>
:::

### Step 2: Sharding

Replication copies data for safety; **sharding** splits it so a collection can be bigger, and busier, than one server can handle. MongoDB shards a collection by a **shard key**, cutting it into **chunks** of key ranges that are spread over the shards and moved around automatically to keep them balanced.

The book builds a small sharded cluster on one machine: two shard servers, one config server, and the **`mongos`** router that clients talk to:

```bash
mkdir ./mongo4 ./mongo5 ./mongoconfig
mongod --shardsvr --dbpath ./mongo4 --port 27014
mongod --shardsvr --dbpath ./mongo5 --port 27015
mongod --configsvr --dbpath ./mongoconfig --port 27016
mongos --configdb localhost:27016 --chunkSize 1 --port 27020
```

```javascript
// mongo localhost:27020/admin
db.runCommand({ addshard : "localhost:27014" })
db.runCommand({ addshard : "localhost:27015" })
db.runCommand({ enablesharding : "test" })
db.runCommand({ shardcollection : "test.cities", key : { name : 1 } })
```

```bash
mongoimport -h localhost:27020 -db test --collection cities \
  --type json mongo_cities1000.json
```

:::fig **A sharded MongoDB cluster.** The application only talks to `mongos`. The config server knows which key ranges (chunks) live on which shard. `mongos` routes each query to the shard(s) that hold the relevant chunks, and the balancer moves chunks to keep shards even.
<svg class="dg wide" viewBox="0 0 720 270">
<rect x="270" y="10" width="180" height="44" rx="8" class="box"/><text x="360" y="37" text-anchor="middle" class="b">application</text>
<line x1="360" y1="54" x2="360" y2="82" class="ln" marker-end="url(#arr)"/>
<rect x="270" y="86" width="180" height="54" rx="8" class="bg"/><text x="360" y="110" text-anchor="middle" class="b mono">mongos :27020</text><text x="360" y="128" text-anchor="middle" class="s">router</text>
<rect x="540" y="86" width="170" height="54" rx="8" class="bw"/><text x="625" y="110" text-anchor="middle" class="b">config server</text><text x="625" y="128" text-anchor="middle" class="s">chunk → shard map</text>
<line x1="452" y1="113" x2="536" y2="113" class="ln dash"/>
<line x1="320" y1="140" x2="190" y2="176" class="ln" marker-end="url(#arr)"/><line x1="400" y1="140" x2="530" y2="176" class="ln" marker-end="url(#arr)"/>
<rect x="60" y="180" width="260" height="76" rx="10" class="ba"/><text x="190" y="202" text-anchor="middle" class="b">shard :27014</text>
<rect x="76" y="214" width="110" height="28" rx="4" class="box"/><text x="131" y="233" text-anchor="middle" class="mono s">A … Ki</text>
<rect x="196" y="214" width="110" height="28" rx="4" class="box"/><text x="251" y="233" text-anchor="middle" class="mono s">Kj … Mo</text>
<rect x="400" y="180" width="260" height="76" rx="10" class="ba"/><text x="530" y="202" text-anchor="middle" class="b">shard :27015</text>
<rect x="416" y="214" width="110" height="28" rx="4" class="box"/><text x="471" y="233" text-anchor="middle" class="mono s">Mp … Sa</text>
<rect x="536" y="214" width="110" height="28" rx="4" class="box"/><text x="591" y="233" text-anchor="middle" class="mono s">Sb … Z</text>
<text x="360" y="230" text-anchor="middle" class="s">chunks</text><text x="360" y="246" text-anchor="middle" class="s">by name</text>
</svg>
:::

:::tip Choosing a shard key
A good shard key has **many distinct values**, spreads **writes evenly**, and appears in most **queries** (so `mongos` can send a query to one shard instead of all of them). City `name` is fine for a demo. A monotonically increasing key like a timestamp is a classic mistake: every new document lands in the last chunk, on one busy shard.
:::

In production every shard is itself a **replica set**, and there are three config servers, so there is no single point of failure.

### Step 3: Geospatial queries

MongoDB can index **locations** and answer "what is near this point?" The book uses a dataset of world cities, each with a `location` field such as `{ longitude: 1.48453, latitude: 42.57205 }`:

```javascript
db.cities.ensureIndex({ location : "2d" })

// cities near a point, nearest first
db.cities.find({ location : { $near : [45.52, -122.67] } }).limit(5)

// the same with geoNear, which also returns each distance
db.runCommand({
  geoNear : 'cities',
  near : [45.52, -122.67],
  num : 5,
  maxDistance : 1
})
// results sorted by distance, each with "dis" (distance) and "obj" (the city)
```

:::warn Coordinate order
A `2d` index reads the **first** value of each point as x and the second as y. The book's data stores longitude first, but its query point `[45.52, -122.67]` is Portland written latitude first. To really search around Portland with this data, write `[-122.67, 45.52]`. Mixing up the order is one of the most common geospatial bugs; GeoJSON (used by today's `2dsphere` indexes) is always `[longitude, latitude]`.
:::

A `2d` index treats coordinates as points on a flat plane. You can also search inside a shape with `$within` and `$box`, `$center` or `$polygon`:

```javascript
db.cities.find({ location : { $within : { $center : [ [45.52, -122.67], 1 ] } } })
```

:::fig **A geospatial query.** A 2d index lets MongoDB find the points nearest a location, or all points inside a box, circle or polygon, without checking every city.
<svg class="dg" viewBox="0 0 720 220">
<rect x="20" y="10" width="420" height="200" rx="10" class="soft"/>
<circle cx="220" cy="110" r="70" class="bg" fill-opacity="0.4" stroke-dasharray="6 4"/>
<circle cx="220" cy="110" r="7" class="fg"/><text x="232" y="106" class="b">Portland</text>
<circle cx="250" cy="70" r="5" class="fa"/><text x="258" y="66" class="s">Vancouver WA</text>
<circle cx="180" cy="150" r="5" class="fa"/><text x="130" y="168" class="s">Beaverton</text>
<circle cx="270" cy="140" r="5" class="fa"/><text x="278" y="144" class="s">Gresham</text>
<circle cx="190" cy="80" r="5" class="fa"/><text x="128" y="74" class="s">Hillsboro</text>
<circle cx="80" cy="40" r="5" class="fm"/><circle cx="380" cy="190" r="5" class="fm"/><circle cx="400" cy="40" r="5" class="fm"/><circle cx="60" cy="180" r="5" class="fm"/>
<text x="470" y="60" class="b">geoNear / $center</text>
<text x="470" y="84" class="s">blue: inside the radius,</text>
<text x="470" y="102" class="s">returned nearest first</text>
<text x="470" y="134" class="s">grey: outside, skipped</text>
<text x="470" y="166" class="s">index type: "2d"</text>
<text x="470" y="184" class="s">(flat plane, as in the book)</text>
</svg>
:::

### Step 4: GridFS

A single MongoDB document was limited to a few megabytes (16 MB today). To store big files (videos, images, backups), MongoDB uses **GridFS**, a convention built on two ordinary collections:

- **`fs.files`**: one document per file, with its name, size, upload date, MD5 checksum and chunk size.
- **`fs.chunks`**: the file's bytes, cut into chunks (256 KB in 2012, 255 KB today), each a document pointing back to the file.

```bash
echo "here's some file data" > just-some-data.txt
mongofiles -h localhost:27020 put just-some-data.txt
mongofiles -h localhost:27020 list
```

```javascript
// mongo localhost:27020
show collections        // fs.chunks, fs.files, ...
db.fs.files.find()
// { "_id" : ObjectId("4e2..."), "filename" : "just-some-data.txt",
//   "chunkSize" : 262144, "uploadDate" : ISODate(...), "md5" : "...", "length" : 22 }
```

:::fig **How GridFS stores a big file.** The file is split into fixed-size chunks stored as documents in `fs.chunks`, each numbered and pointing to a metadata document in `fs.files`. Because these are normal collections, files are replicated and sharded like any other data.
<svg class="dg wide" viewBox="0 0 720 200">
<rect x="10" y="60" width="120" height="80" rx="8" class="box"/><text x="70" y="96" text-anchor="middle" class="b">video.mp4</text><text x="70" y="116" text-anchor="middle" class="s">700 KB</text>
<line x1="132" y1="100" x2="186" y2="100" class="ln" marker-end="url(#arr)"/>
<text x="159" y="90" text-anchor="middle" class="s">split</text>
<rect x="190" y="20" width="250" height="160" rx="10" class="soft"/>
<text x="315" y="40" text-anchor="middle" class="b mono">fs.chunks</text>
<rect x="206" y="52" width="218" height="34" rx="5" class="bg"/><text x="216" y="74" class="mono s">n: 0 · 256 KB · files_id: f1</text>
<rect x="206" y="92" width="218" height="34" rx="5" class="bg"/><text x="216" y="114" class="mono s">n: 1 · 256 KB · files_id: f1</text>
<rect x="206" y="132" width="218" height="34" rx="5" class="bg"/><text x="216" y="154" class="mono s">n: 2 · 188 KB · files_id: f1</text>
<rect x="500" y="50" width="210" height="110" rx="10" class="ba"/>
<text x="605" y="72" text-anchor="middle" class="b mono">fs.files</text>
<g class="mono s"><text x="514" y="94">_id: f1</text><text x="514" y="112">filename: "video.mp4"</text><text x="514" y="130">length: 716800</text><text x="514" y="148">chunkSize · md5 · date</text></g>
<line x1="426" y1="109" x2="496" y2="105" class="la" marker-end="url(#arra)"/>
</svg>
:::

### Day 3 homework, solved

**1. All cities within a 50-mile box around the centre of London** (longitude −0.13, latitude 51.50). With a flat `2d` index, coordinates are degrees. 50 miles is about 0.72° of latitude, and at London's latitude about 1.16° of longitude. A box is given by its lower-left and upper-right corners, in the data's order (longitude, latitude). A box 50 miles across means 25 miles each way:

```javascript
db.cities.find({
  location : { $within : { $box : [ [-0.13 - 0.58, 51.50 - 0.36],
                                    [-0.13 + 0.58, 51.50 + 0.36] ] } }
})
```

(For a box reaching 50 miles in every direction from the centre, double the offsets: ±1.16 and ±0.72.)

(The book's "Find" item, a spherical index, gives true distances on the globe; today you would use a `2dsphere` index with GeoJSON points and `$geoWithin` / `$near` with distances in metres.)

**2. The final exam.** Six servers: two shards, each a three-member replica set, plus a config server and `mongos`; then store files with GridFS through `mongos`:

```bash
# shard A: replica set "a"
mongod --shardsvr --replSet a --dbpath ./a1 --port 27101
mongod --shardsvr --replSet a --dbpath ./a2 --port 27102
mongod --shardsvr --replSet a --dbpath ./a3 --port 27103
# shard B: replica set "b"
mongod --shardsvr --replSet b --dbpath ./b1 --port 27201
mongod --shardsvr --replSet b --dbpath ./b2 --port 27202
mongod --shardsvr --replSet b --dbpath ./b3 --port 27203
# config server and router
mongod --configsvr --dbpath ./cfg --port 27300
mongos --configdb localhost:27300 --port 27400
```

```javascript
// mongo localhost:27101  → rs.initiate({_id:'a', members:[{_id:0,host:'localhost:27101'},
//                           {_id:1,host:'localhost:27102'},{_id:2,host:'localhost:27103'}]})
// mongo localhost:27201  → the same for 'b'
// mongo localhost:27400/admin
db.runCommand({ addshard : "a/localhost:27101,localhost:27102,localhost:27103" })
db.runCommand({ addshard : "b/localhost:27201,localhost:27202,localhost:27203" })
db.runCommand({ enablesharding : "files" })
db.runCommand({ shardcollection : "files.fs.chunks", key : { files_id : 1, n : 1 } })
```

```bash
mongofiles -h localhost:27400 -d files put big_video.mp4
```

## Wrap-up · Strengths and weaknesses

### Strengths

- **Huge data and huge traffic**, through replication and horizontal scaling (sharding).
- **A very flexible data model**: no schema to conform to, and values you would join in SQL can simply be nested.
- **Easy to use and familiar.** Many Mongo commands mirror SQL ideas (minus server-side joins). That is no accident, and it is why former users of object-relational mappers (ORMs) adopted it so quickly.

### Weaknesses

- **Denormalization by default.** Without a schema, nothing stops you inserting any value of any type into any collection. A typo in a field or collection name silently creates a new one, and can cost hours to find. Some developers find relational constraints reassuring for good reason.
- **Flexibility matters less** if your data model is already mature and stable.
- **Clusters need planning.** Mongo works best in large clusters, which take effort to design and manage. Unlike Riak, adding nodes is not transparent.

### Parting thoughts

The authors recommend MongoDB especially to developers who use a relational database **out of habit, through an ORM**: Rails, Django and other Model-View-Controller developers. Validation and field management can live in the application's models, and schema migrations largely disappear: add a field to the model and Mongo accepts it. For many application-driven datasets, they find Mongo a more natural fit than a relational database.

:::modern MongoDB in 2026
MongoDB became one of the most widely used databases in the world, and changed a lot along the way:
- **New shell and API.** The old `mongo` shell was replaced by **`mongosh`**. `insert` became `insertOne`/`insertMany`; `update` became `updateOne`/`updateMany` (which require operators like `$set`) and `replaceOne` (for whole-document replacement, the mistake from Day 1 is now explicit); `remove` became `deleteOne`/`deleteMany`; `ensureIndex` became `createIndex` and `dropDups` was removed.
- **Aggregation pipeline replaced group and mapreduce.** Introduced in 2.2 (August 2012), it chains stages such as `$match`, `$group`, `$sort`, `$project`, `$unwind` and `$lookup` (a server-side **join**, since 3.2). `group()` and `db.eval()` were removed in 4.2, and **mapReduce is deprecated** since 5.0.
- **Transactions.** Multi-document ACID transactions arrived in 4.0 (2018), and across shards in 4.2.
- **Storage engine.** WiredTiger became the default in 3.2, bringing document-level concurrency (no more database-wide write lock) and compression. Journaling is on by default, and the default write concern is `majority` since 5.0.
- **Geo:** `geoNear` the command is gone; use `2dsphere` indexes with GeoJSON and `$near` / `$geoWithin` / the `$geoNear` aggregation stage.
- **Clusters:** config servers must now be a replica set; resharding and zone sharding exist.
- **Licence and cloud:** since 2018 the server is under the SSPL licence (not approved as open source by the OSI). Most new users run it as **MongoDB Atlas**, the managed cloud service, which also adds full-text and vector search.
:::

:::key Chapter 5 in a nutshell
- **Model:** databases → collections → JSON-like documents with an `_id` (ObjectId by default). No schema; nest arrays and objects freely.
- **Day 1:** `insert`, `find` with criteria and projections, operators (`$lt`, `$in`, `$all`, `$exists`, `$regex`, `$or`), dot notation, `$elemMatch`, updates with `$set`/`$inc`/`$push` (never forget `$set`), DBRef references, `remove`, `$where`.
- **Day 2:** `ensureIndex` and `explain()`, the profiler, `count`/`distinct`/`group`, server-side commands and `system.js`, mapreduce with re-reducible reduce and `finalize`.
- **Day 3:** replica sets (primary, secondaries, elections, odd numbers), sharding (`mongos`, config servers, shard keys, chunks), `2d` geospatial queries, GridFS for big files.
- **Choose it when** your data is varied or nested and your app wants flexible queries at scale. **Be careful** when you need strong schemas or complex relational queries.
:::

@@quiz
Q: What happens when you insert a document without an `_id` field?
- The insert fails
+ MongoDB generates an ObjectId and stores it in `_id`
- MongoDB uses the first field as the key
- The document is stored without any identifier
? Every document must have a unique `_id`. If you do not provide one, MongoDB creates a 12-byte ObjectId that is unique across machines without coordination.

Q: Which query finds towns whose mayor belongs to party "I"?
- `db.towns.find({ mayor: "I" })`
+ `db.towns.find({ 'mayor.party': 'I' })`
- `db.towns.find({ mayor: { party: { $eq: 'I' } }, $nested: true })`
- `db.towns.find('mayor->party = I')`
? Dot notation, in quotes, reaches into nested documents: `'mayor.party'`.

Q: Canada exports `[{name: "bacon", tasty: false}, {name: "syrup", tasty: true}]`. Which query does NOT return Canada when looking for tasty bacon?
- `find({'exports.foods.name': 'bacon', 'exports.foods.tasty': true})`
+ `find({'exports.foods': {$elemMatch: {name: 'bacon', tasty: true}}})`
- `find({'exports.foods.name': 'bacon'})`
- `find({'exports.foods.tasty': true})`
? Without `$elemMatch`, each condition can be satisfied by a different array element, so Canada matches. `$elemMatch` requires a single element to satisfy both conditions.

Q: What does this update do to Portland's document?
C: db.towns.update({ name: "Portland" }, { state: "OR" })
- Adds a `state` field and keeps everything else
+ Replaces the whole document with `{ state: "OR" }` (plus its `_id`)
- Fails because `$set` is missing
- Updates every town
? Without an update operator, the second argument is treated as a replacement document. To add a field, use `{ $set: { state: "OR" } }`.

Q: Two servers increment a page's view counter at the same moment. Which approach guarantees both increments are counted?
- Each server reads the document, adds 1 in code and saves it back
+ Each server sends `update(..., { $inc: { views: 1 } })`
- Each server deletes and reinserts the document
- Use `$set` with the new number
? `$inc` is applied atomically inside the database, so concurrent increments cannot overwrite each other. Read-modify-write in application code can lose an update.

Q: `explain()` shows `"cursor": "BasicCursor", "nscanned": 109999, "n": 1`. What does that tell you?
- The query used an index efficiently
+ The query scanned the whole collection to find one document; an index on the queried field would help
- The query returned 109,999 documents
- The collection is sharded
? BasicCursor means a full scan. After `ensureIndex({display: 1})`, the same query shows a BtreeCursor with nscanned 1.

Q: Why does the mapreduce map function emit `{count: 1}` instead of just `1`?
- JavaScript cannot emit numbers
+ Reduce may be called again on its own output, so values must keep the same shape at every stage
- Because `_id` must be an object
- To make the output collection smaller
? MongoDB may re-reduce partial results. If reduce returns `{count: total}`, its output looks exactly like a map value, so it can be reduced again safely.

Q: In a three-member replica set, the primary crashes. What happens?
- All writes are lost until an administrator intervenes
+ The two remaining members hold an election and one becomes primary, since 2 of 3 is a majority
- Both secondaries become primaries
- The set switches to read-only forever
? Elections need a majority of all members. Two of three is a majority, so a new primary is elected automatically within seconds.

Q: Why does the book warn against an even number of replica set members?
- Even numbers use more disk space
+ A network split into two equal halves leaves neither side with a majority, so no primary can be elected
- MongoDB only accepts odd port numbers
- Even numbers make elections too fast
? With 4 members split 2 and 2, neither half reaches 3 votes. Use an odd number, or add an arbiter (a voting member with no data).

Q: In a sharded cluster, which component do applications connect to?
- The config server
- Any shard directly
+ `mongos`, the router that sends each operation to the right shard(s)
- The primary of the first replica set
? `mongos` uses the config server's chunk map to route queries. Applications never need to know which shard holds which data.

Q: How does GridFS store a 700 KB file?
- As one document in the `files` collection
+ As a metadata document in `fs.files` plus several numbered chunk documents in `fs.chunks`
- As a link to a file on the server's disk
- It cannot; MongoDB documents are limited to 4 KB
? GridFS splits big files into fixed-size chunks stored as ordinary documents, so files are replicated and sharded like any other data.

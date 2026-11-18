title: PostgreSQL
lead: The hammer of the database world. Tables, SQL and joins on Day 1; grouping, transactions, code and rules on Day 2; fuzzy search, full-text search and multidimensional queries on Day 3.

## Overview: why start with PostgreSQL?

The authors call PostgreSQL **the hammer of the database world**: common, sturdy, and able to solve a surprising number of problems if you swing it hard enough. It comes first because every other database in the book is easier to understand when you can compare it with a good relational one.

PostgreSQL is a **relational database management system (RDBMS)**. That means it is built on set theory and stores data as two-dimensional tables made of rows, with strictly enforced column types. The book gives four reasons why relational databases remain so popular:

| Reason | What it means |
|---|---|
| A huge toolkit | Triggers, stored procedures, advanced indexes, custom types. |
| Data safety (ACID) | Changes are all-or-nothing, rules are never broken, saved data survives crashes. |
| Mind share | Most programmers already think in tables and SQL. |
| **Query flexibility** | You do not need to know in advance how you will use the data. If the schema is well designed (normalized), you can ask almost any question later. |

The last one is the big one. Many NoSQL databases ask you to design your data around the questions you plan to ask. A relational database lets you ask new questions years later.

:::deep Where the name comes from
The project started at the University of California, Berkeley, in the early 1970s as **Ingres** (Interactive Graphics and Retrieval System). In the 1980s an improved successor was built "post-Ingres", shortened to **Postgres**. Berkeley stopped working on it in 1993, the open-source community picked it up as **Postgres95**, and in 1996 it was renamed **PostgreSQL** to show it now spoke SQL. People say "post-gres-Q-L" or simply "Postgres".
:::

PostgreSQL also brings things many relational databases do not: plug-ins for natural-language parsing, multidimensional indexing, geographic queries and custom data types; stored procedures in a dozen languages; Unicode, sequences, table inheritance and subselects. It handles terabytes of data, and in 2012 it already ran at Skype, the US Federal Aviation Administration and France's family benefits agency (CNAF).

### Setting up

Beyond the basic install, the chapter needs five **contrib packages** (optional extensions that ship with PostgreSQL): `tablefunc`, `dict_xsyn`, `fuzzystrmatch`, `pg_trgm` and `cube`. Then create a database for the exercises:

```bash
createdb book                       # create a database called "book"
psql book -c "SELECT '1'::cube;"    # check that the cube extension works
```

:::modern Installing extensions today
Since PostgreSQL 9.1 you switch an extension on inside each database with one SQL command instead of running install scripts:
```sql
CREATE EXTENSION tablefunc;
CREATE EXTENSION fuzzystrmatch;
CREATE EXTENSION pg_trgm;
CREATE EXTENSION cube;
CREATE EXTENSION dict_xsyn;
```
The book uses PostgreSQL 9.0/9.1. Current versions (PostgreSQL 18, with 19 scheduled for release on 19 November 2026) are much faster and add `jsonb`, parallel queries, logical replication and better partitioning, but everything in this chapter still works.
:::

## Day 1 · Relations, CRUD and joins

Day 1 covers the core of every relational database: creating tables, the four basic operations (CRUD), joining tables, and indexes.

### Step 1: Client and server

Like most databases in the book, PostgreSQL has two parts: a **server** that does the work, and a **client** that sends it commands. The server listens on port **5432** by default. The client shell is called `psql`:

```bash
psql book
```

The prompt shows the database name followed by `=#` if you are an administrator, or `=>` if you are a regular user. `psql` has excellent built-in help:

| Command | What it does |
|---|---|
| `\h` | Help on SQL commands, for example `\h CREATE INDEX` prints its full syntax. |
| `\?` | Help on `psql`'s own backslash commands. |
| `\dt` | List tables. |
| `\d events` | Describe the `events` table. |
| `\di` | List indexes. |
| `\i file.sql` | Run the SQL in a file. |
| `\q` | Quit. |

### Step 2: What "relational" really means

A common misunderstanding is that "relational" means "tables relate to each other through foreign keys". It does not. The word comes from mathematics:

| Mathematical term | SQL term | Example |
|---|---|---|
| Relation | Table | `countries` |
| Tuple | Row | `('us', 'United States')` |
| Attribute | Column | `country_name` |

A relation is a **set of tuples**. Because relations are sets, the database can apply **relational algebra** to them:

- **Selection** picks rows. In SQL: `WHERE died_at_age IS NULL`.
- **Projection** picks columns. In SQL: `SELECT name`.
- **Cartesian product** combines tables. In SQL: `JOIN`.

So the query `SELECT x.name FROM People x WHERE x.died_at_age IS NULL` is really "project the name attribute from the selection of People where died_at_age is null".

:::deep Why the math matters to you
SQL is **declarative**: you describe *what* you want, not *how* to get it. Because the math underneath is precise, PostgreSQL can turn your query into algebra, simplify it, and pick the fastest way to run it (which index to use, which table to read first).
The authors warn against picturing a table as "an array of arrays that I loop through". If you think that way you end up writing code that fetches all rows and filters them in your program, which throws away everything the database is good at.
:::

### Step 3: Design first, then data

PostgreSQL is a **design-first** datastore. You define the schema (tables, columns, types, rules), and then every row you insert must fit it. Over Day 1 the book builds four connected tables for an event calendar:

:::fig **The Day 1 schema.** Each arrow points from a foreign key to the primary key it must match. A city belongs to a country, a venue sits in a city, and an event happens at a venue (or at no venue, for holidays). Keys marked PK identify rows; keys marked FK point to another table.
<svg class="dg wide" viewBox="0 0 720 270">
<rect x="10" y="40" width="150" height="110" rx="8" class="ba"/>
<text x="85" y="62" text-anchor="middle" class="b">countries</text>
<line x1="10" y1="72" x2="160" y2="72" class="la"/>
<text x="16" y="94" class="mono">country_code</text><text x="154" y="94" text-anchor="end" class="s b ta">PK</text>
<text x="16" y="116" class="mono">country_name</text><text x="154" y="116" text-anchor="end" class="s">UNIQUE</text>
<rect x="195" y="40" width="160" height="130" rx="8" class="ba"/>
<text x="275" y="62" text-anchor="middle" class="b">cities</text>
<line x1="195" y1="72" x2="355" y2="72" class="la"/>
<text x="205" y="94" class="mono">name</text><text x="345" y="94" text-anchor="end" class="s">NOT NULL</text>
<text x="205" y="116" class="mono">postal_code</text><text x="345" y="116" text-anchor="end" class="s b ta">PK</text>
<text x="205" y="138" class="mono">country_code</text><text x="345" y="138" text-anchor="end" class="s b ta">PK, FK</text>
<rect x="390" y="40" width="160" height="200" rx="8" class="ba"/>
<text x="470" y="62" text-anchor="middle" class="b">venues</text>
<line x1="390" y1="72" x2="550" y2="72" class="la"/>
<text x="400" y="94" class="mono">venue_id</text><text x="540" y="94" text-anchor="end" class="s b ta">PK</text>
<text x="400" y="116" class="mono">name</text>
<text x="400" y="138" class="mono">street_address</text>
<text x="400" y="160" class="mono">type</text><text x="540" y="160" text-anchor="end" class="s">CHECK</text>
<text x="400" y="182" class="mono">postal_code</text><text x="540" y="182" text-anchor="end" class="s b ta">FK</text>
<text x="400" y="204" class="mono">country_code</text><text x="540" y="204" text-anchor="end" class="s b ta">FK</text>
<rect x="585" y="40" width="125" height="150" rx="8" class="ba"/>
<text x="647" y="62" text-anchor="middle" class="b">events</text>
<line x1="585" y1="72" x2="710" y2="72" class="la"/>
<text x="595" y="94" class="mono">event_id</text><text x="700" y="94" text-anchor="end" class="s b ta">PK</text>
<text x="595" y="116" class="mono">title</text>
<text x="595" y="138" class="mono">starts</text>
<text x="595" y="160" class="mono">ends</text>
<text x="595" y="182" class="mono">venue_id</text><text x="700" y="182" text-anchor="end" class="s b ta">FK</text>
<path d="M195,138 L178,138 L178,94 L163,94" class="ln" marker-end="url(#arr)"/>
<path d="M390,193 L372,193 L372,127 L358,127" class="ln" marker-end="url(#arr)"/>
<path d="M585,182 L568,182 L568,94 L553,94" class="ln" marker-end="url(#arr)"/>
<text x="178" y="190" text-anchor="middle" class="s">has</text>
<text x="372" y="220" text-anchor="middle" class="s">contains</text>
<text x="568" y="210" text-anchor="middle" class="s">hosts</text>
</svg>
:::

#### Table 1: countries

```sql
CREATE TABLE countries (
  country_code char(2) PRIMARY KEY,
  country_name text UNIQUE
);
```

Every table should have a **primary key**: a column (or set of columns) whose value pinpoints exactly one row. Here, only one row may have `country_code = 'us'`. The `UNIQUE` constraint also blocks duplicates, but on a column that is not the key.

```sql
INSERT INTO countries (country_code, country_name)
VALUES ('us','United States'), ('mx','Mexico'), ('au','Australia'),
       ('gb','United Kingdom'), ('de','Germany'), ('ll','Loompaland');
```

The book then tests the constraint on purpose, by inserting the United Kingdom again under a different code:

```sql
INSERT INTO countries VALUES ('uk','United Kingdom');
-- ERROR: duplicate key value violates unique constraint "countries_country_name_key"
```

That error is the database doing its job. **Constraints are how a relational database keeps your data clean**, no matter which program (or which tired developer) writes to it.

#### Table 2: cities

```sql
CREATE TABLE cities (
  name text NOT NULL,
  postal_code varchar(9) CHECK (postal_code <> ''),
  country_code char(2) REFERENCES countries,
  PRIMARY KEY (country_code, postal_code)
);
```

This table introduces four new ideas at once:

| Constraint | Meaning here |
|---|---|
| `NOT NULL` | Every city must have a name. |
| `CHECK (postal_code <> '')` | A custom rule: the postal code cannot be an empty string (`<>` means "not equal"). |
| `REFERENCES countries` | A **foreign key**: `country_code` must already exist in `countries`. |
| `PRIMARY KEY (country_code, postal_code)` | A **compound key**: the two columns *together* identify a city. |

It also shows three string types: `text` (any length), `varchar(9)` (up to 9 characters) and `char(2)` (exactly 2 characters).

Now try inserting Toronto, Canada:

```sql
INSERT INTO cities VALUES ('Toronto','M4C1B5','ca');
-- ERROR: insert or update on table "cities" violates foreign key constraint
-- DETAIL: Key (country_code)=(ca) is not present in table "countries".
```

:::fig **Referential integrity in action.** Before accepting the new city, PostgreSQL looks up its country code in the referenced table. There is no 'ca' row, so the insert is rejected and the database never contains a city in a country that does not exist.
<svg class="dg" viewBox="0 0 720 200">
<rect x="10" y="60" width="200" height="70" rx="8" class="box"/>
<text x="110" y="86" text-anchor="middle" class="b">INSERT INTO cities</text>
<text x="110" y="108" text-anchor="middle" class="mono">('Toronto','M4C1B5','ca')</text>
<line x1="214" y1="95" x2="300" y2="95" class="ln" marker-end="url(#arr)"/>
<text x="257" y="85" text-anchor="middle" class="s">check FK</text>
<rect x="305" y="20" width="170" height="160" rx="8" class="ba"/>
<text x="390" y="42" text-anchor="middle" class="b">countries</text>
<text x="325" y="68" class="mono">us</text><text x="355" y="68" class="mono s">United States</text>
<text x="325" y="90" class="mono">mx</text><text x="355" y="90" class="mono s">Mexico</text>
<text x="325" y="112" class="mono">au</text><text x="355" y="112" class="mono s">Australia</text>
<text x="325" y="134" class="mono">gb</text><text x="355" y="134" class="mono s">United Kingdom</text>
<text x="325" y="156" class="mono">de</text><text x="355" y="156" class="mono s">Germany</text>
<text x="390" y="174" text-anchor="middle" class="s tr b">no 'ca' here</text>
<line x1="479" y1="95" x2="540" y2="95" class="lr" marker-end="url(#arrr)"/>
<rect x="545" y="60" width="165" height="70" rx="8" class="br"/>
<text x="627" y="88" text-anchor="middle" class="b tr">Rejected</text>
<text x="627" y="110" text-anchor="middle" class="s">foreign key violation</text>
</svg>
:::

This guarantee is called **referential integrity**: a reference always points to something that exists.

:::warn NULL is allowed in a foreign key
`REFERENCES` alone still accepts `NULL`, because NULL means "no value at all" rather than "a value that does not exist". If every city must have a country, write `country_code char(2) REFERENCES countries NOT NULL`.
:::

A US city works, because `'us'` exists:

```sql
INSERT INTO cities VALUES ('Portland','87200','us');   -- INSERT 0 1
```

#### Table 3: venues

```sql
CREATE TABLE venues (
  venue_id SERIAL PRIMARY KEY,
  name varchar(255),
  street_address text,
  type char(7) CHECK ( type in ('public','private') ) DEFAULT 'public',
  postal_code varchar(9),
  country_code char(2),
  FOREIGN KEY (country_code, postal_code)
    REFERENCES cities (country_code, postal_code) MATCH FULL
);
```

| Feature | Meaning |
|---|---|
| `SERIAL` | An integer that fills itself in: 1, 2, 3 and so on. MySQL calls this `AUTO_INCREMENT`. |
| `CHECK (type in (...))` | Only `'public'` or `'private'` are allowed. |
| `DEFAULT 'public'` | Used when the insert does not give a value. |
| Two-column foreign key | Cities have a compound key, so a venue must point at **both** columns. |
| `MATCH FULL` | Either both foreign key columns are filled in, or both are NULL. Half-filled is rejected. |

```sql
INSERT INTO venues (name, postal_code, country_code)
VALUES ('Crystal Ballroom', '97205', 'us');
```

We never gave a `venue_id`, but the row has one (1), created by `SERIAL`.

#### Table 4: events

The book leaves this one as an exercise. One solution:

```sql
CREATE TABLE events (
  event_id SERIAL PRIMARY KEY,
  title    text,
  starts   timestamp,
  ends     timestamp,
  venue_id integer REFERENCES venues
);

INSERT INTO events (title, starts, ends, venue_id) VALUES
  ('LARP Club',       '2012-02-15 17:30', '2012-02-15 19:30', 2),
  ('April Fools Day', '2012-04-01 00:00', '2012-04-01 23:59', NULL),
  ('Christmas Day',   '2012-12-25 00:00', '2012-12-25 23:59', NULL);
```

Venue 2 is *Voodoo Donuts*, added below. The two holidays have **no venue**, and that NULL will matter a lot when we get to joins.

### Step 4: CRUD, the four basic operations

| Letter | Operation | SQL keyword | Example from the chapter |
|---|---|---|---|
| **C** | Create | `INSERT` | `INSERT INTO countries VALUES ('us','United States');` |
| **R** | Read | `SELECT` | `SELECT * FROM countries;` |
| **U** | Update | `UPDATE` | `UPDATE cities SET postal_code = '97205' WHERE name = 'Portland';` |
| **D** | Delete | `DELETE` | `DELETE FROM countries WHERE country_code = 'll';` |

(Loompaland is not a real country, so it gets deleted. Portland was inserted with the wrong postal code on purpose so it can be updated.)

The authors' point: **every query you will ever write, however clever, is a Read.** If you can do CRUD, you can do anything.

:::warn Always use WHERE with UPDATE and DELETE
`DELETE FROM countries;` without a `WHERE` deletes every row. `UPDATE cities SET postal_code = '97205';` changes every city. Many developers run a `SELECT` with the same `WHERE` first to see which rows will be affected.
:::

A useful extra, `RETURNING`, hands back values from the row you just inserted, so you do not need a second query to learn the new ID:

```sql
INSERT INTO venues (name, postal_code, country_code)
VALUES ('Voodoo Donuts', '97205', 'us') RETURNING venue_id;
--  venue_id
-- ----------
--         2
```

### Step 5: Joins, the relational superpower

All seven databases in the book can do CRUD. What sets relational databases apart is the **join**: combining two tables into one result at read time. The book compares it to shuffling Scrabble tiles from existing words to build new ones.

#### Inner join

The basic join matches rows from two tables using one column from each, given after `ON`:

```sql
SELECT cities.*, country_name
FROM cities INNER JOIN countries
  ON cities.country_code = countries.country_code;
```

```text
 country_code |   name   | postal_code | country_name
--------------+----------+-------------+---------------
 us           | Portland | 97205       | United States
```

The result is a new table: all the city columns plus the matching country name.

When a table has a **compound key**, the join must match all key columns. Table **aliases** (`venues v`) save typing:

```sql
SELECT v.venue_id, v.name, c.name
FROM venues v INNER JOIN cities c
  ON v.postal_code = c.postal_code AND v.country_code = c.country_code;
```

#### Outer joins

An inner join returns a row **only when both sides match**. Look what happens to the holidays:

```sql
SELECT e.title, v.name
FROM events e JOIN venues v ON e.venue_id = v.venue_id;
```

```text
   title   |     name
-----------+---------------
 LARP Club | Voodoo Donuts
```

April Fools Day and Christmas have a NULL `venue_id`, which matches nothing, so they vanish. To keep **every event** whether or not it has a venue, use a **LEFT OUTER JOIN** (usually written `LEFT JOIN`):

```sql
SELECT e.title, v.name
FROM events e LEFT JOIN venues v ON e.venue_id = v.venue_id;
```

```text
      title      |     name
-----------------+---------------
 LARP Club       | Voodoo Donuts
 April Fools Day |
 Christmas Day   |
```

:::fig **The four join types.** The left circle is `events`, the right circle is `venues`, and the overlap holds rows that match. The shaded area is what each join returns. Rows that exist on only one side come back with empty (NULL) values for the other side's columns.
<svg class="dg wide" viewBox="0 0 720 210">
<g>
<circle cx="70" cy="80" r="44" class="box"/><circle cx="110" cy="80" r="44" class="box"/>
<path d="M90,40.6 A44,44 0 0,1 90,119.4 A44,44 0 0,1 90,40.6 Z" class="fa" opacity="0.55"/>
<text x="90" y="150" text-anchor="middle" class="b">INNER JOIN</text>
<text x="90" y="168" text-anchor="middle" class="s">only matching rows</text>
<text x="90" y="186" text-anchor="middle" class="s">LARP Club</text>
</g>
<g>
<circle cx="250" cy="80" r="44" class="fa" opacity="0.55"/><circle cx="290" cy="80" r="44" class="box" fill-opacity="0"/>
<circle cx="250" cy="80" r="44" class="ln2"/>
<text x="270" y="150" text-anchor="middle" class="b">LEFT JOIN</text>
<text x="270" y="168" text-anchor="middle" class="s">every event, plus matches</text>
<text x="270" y="186" text-anchor="middle" class="s">LARP, April Fools, Christmas</text>
</g>
<g>
<circle cx="470" cy="80" r="44" class="fa" opacity="0.55"/><circle cx="430" cy="80" r="44" class="box" fill-opacity="0"/>
<circle cx="470" cy="80" r="44" class="ln2"/>
<text x="450" y="150" text-anchor="middle" class="b">RIGHT JOIN</text>
<text x="450" y="168" text-anchor="middle" class="s">every venue, plus matches</text>
<text x="450" y="186" text-anchor="middle" class="s">venues with no events too</text>
</g>
<g>
<circle cx="610" cy="80" r="44" class="fa" opacity="0.55"/><circle cx="650" cy="80" r="44" class="fa" opacity="0.55"/>
<text x="630" y="150" text-anchor="middle" class="b">FULL JOIN</text>
<text x="630" y="168" text-anchor="middle" class="s">everything from both</text>
<text x="630" y="186" text-anchor="middle" class="s">joined where they match</text>
</g>
<text x="64" y="26" text-anchor="end" class="s">events</text><text x="116" y="26" class="s">venues</text>
</svg>
:::

| Join | Returns |
|---|---|
| `INNER JOIN` (or just `JOIN`) | Only rows that match on both sides. |
| `LEFT JOIN` | Every row from the left table, plus matches (NULLs where there are none). |
| `RIGHT JOIN` | Every row from the right table, plus matches. |
| `FULL JOIN` | Every row from both, joined where they match. |

:::tip Reading a join out loud
"Give me events, **and** for each one, the venue whose `venue_id` equals the event's `venue_id`." If you say "and if there is no venue, keep the event anyway", you mean `LEFT JOIN`.
:::

### Step 6: Indexes for fast lookups

PostgreSQL is fast because it manages blocks of data cleverly, avoids disk reads and optimizes queries. But some queries still have to look at every row. Without an index, this query reads the whole table:

```sql
SELECT * FROM events WHERE title = 'Christmas Day';
```

That is a **full table scan**: row 1, no; row 2, no; row 3, yes. Fine for three rows, terrible for three billion.

An **index** is a separate data structure that maps values to row locations, like the index at the back of a book that sends you straight to page 214.

:::fig **Table scan versus B-tree index.** Without an index, the database checks rows one by one. A B-tree keeps values sorted in a shallow, balanced tree, so the database walks down a few levels and lands on the right rows. Because the leaves are sorted and linked, ranges such as `starts >= '2012-04-01'` are just as easy.
<svg class="dg wide" viewBox="0 0 720 270">
<text x="150" y="22" text-anchor="middle" class="lg">Full table scan</text>
<rect x="30" y="40" width="240" height="200" rx="8" class="box"/>
<g class="mono">
<text x="46" y="66">LARP Club</text><text x="256" y="66" text-anchor="end" class="tr">✕</text>
<text x="46" y="92">April Fools Day</text><text x="256" y="92" text-anchor="end" class="tr">✕</text>
<text x="46" y="118">Valentine's Day</text><text x="256" y="118" text-anchor="end" class="tr">✕</text>
<text x="46" y="144">Wedding</text><text x="256" y="144" text-anchor="end" class="tr">✕</text>
<text x="46" y="170">Christmas Day</text><text x="256" y="170" text-anchor="end" class="tg">✓</text>
<text x="46" y="196">Moby</text><text x="256" y="196" text-anchor="end" class="tm">✕</text>
<text x="46" y="222">… millions more</text><text x="256" y="222" text-anchor="end" class="tm">✕</text>
</g>
<text x="150" y="262" text-anchor="middle" class="s">reads every row: O(n)</text>
<line x1="320" y1="20" x2="320" y2="250" class="ln2 dash"/>
<text x="520" y="22" text-anchor="middle" class="lg">B-tree index lookup</text>
<rect x="470" y="40" width="100" height="34" rx="6" class="ba"/>
<text x="520" y="62" text-anchor="middle" class="mono">L … T</text>
<rect x="360" y="110" width="90" height="34" rx="6" class="box"/>
<text x="405" y="132" text-anchor="middle" class="mono">A … K</text>
<rect x="475" y="110" width="90" height="34" rx="6" class="ba"/>
<text x="520" y="132" text-anchor="middle" class="mono">L … S</text>
<rect x="590" y="110" width="90" height="34" rx="6" class="box"/>
<text x="635" y="132" text-anchor="middle" class="mono">T … Z</text>
<line x1="490" y1="74" x2="420" y2="108" class="ln2"/>
<line x1="520" y1="74" x2="520" y2="108" class="la" marker-end="url(#arra)"/>
<line x1="550" y1="74" x2="620" y2="108" class="ln2"/>
<rect x="350" y="180" width="80" height="44" rx="6" class="box"/>
<text x="390" y="200" text-anchor="middle" class="mono s">April…</text><text x="390" y="215" text-anchor="middle" class="mono s">Christmas</text>
<rect x="440" y="180" width="80" height="44" rx="6" class="ba"/>
<text x="480" y="200" text-anchor="middle" class="mono s">LARP Club</text><text x="480" y="215" text-anchor="middle" class="mono s">Moby → #4</text>
<rect x="530" y="180" width="80" height="44" rx="6" class="box"/>
<text x="570" y="200" text-anchor="middle" class="mono s">…</text>
<rect x="620" y="180" width="80" height="44" rx="6" class="box"/>
<text x="660" y="200" text-anchor="middle" class="mono s">Wedding…</text>
<line x1="510" y1="144" x2="485" y2="178" class="la" marker-end="url(#arra)"/>
<line x1="430" y1="202" x2="440" y2="202" class="ln2"/><line x1="520" y1="202" x2="530" y2="202" class="ln2"/><line x1="610" y1="202" x2="620" y2="202" class="ln2"/>
<text x="525" y="252" text-anchor="middle" class="s">finding "Moby": 3 steps instead of n</text>
</svg>
:::

PostgreSQL automatically creates an index for every **PRIMARY KEY** and **UNIQUE** constraint. You can add your own:

```sql
-- hash index: only exact matches (=)
CREATE INDEX events_title ON events USING hash (title);

-- B-tree index (the default): =, <, >, BETWEEN, ORDER BY, ranges
CREATE INDEX events_starts ON events USING btree (starts);

SELECT * FROM events WHERE starts >= '2012-04-01';   -- now uses the index
```

:::deep Why B-trees are so popular
A B-tree is a **balanced** tree: every leaf is the same distance from the root. Each node holds many keys (hundreds), so even a billion rows need only about four or five levels. Finding one value means reading four or five disk pages instead of millions. Because the leaves are kept **in sorted order**, the same index also answers range queries and helps `ORDER BY`. A hash index can only answer "is it exactly equal to X?"
:::

:::warn Two corrections to the book
1. The book says that setting a `FOREIGN KEY` makes PostgreSQL create an index automatically. Only the **referenced** side is indexed (because it must be a primary key or unique). The **referencing column**, such as `events.venue_id`, is **not** indexed for you. Create those indexes yourself if you join or delete on them often, which is exactly the book's advice anyway.
2. The book says values in a hash index must be unique. They do not have to be. Also, before PostgreSQL 10 hash indexes were not crash-safe, so in practice people almost always use B-tree.
:::

### Day 1 homework, solved

**Find:** the PostgreSQL FAQ and documentation; the `\?` and `\h` help; what `MATCH FULL` means (answered above: all foreign key columns must be NULL together or filled in together).

**1. List only the tables we created, using the `pg_class` system catalog:**

```sql
SELECT relname FROM pg_class
WHERE relname IN ('countries','cities','venues','events')
  AND relkind = 'r';      -- 'r' = ordinary table (not an index or sequence)
```

**2. Find the country name of the LARP Club event** (a three-table join):

```sql
SELECT co.country_name
FROM events e
JOIN venues v     ON e.venue_id = v.venue_id
JOIN countries co ON v.country_code = co.country_code
WHERE e.title = 'LARP Club';
-- United States
```

**3. Add a boolean `active` column to venues, defaulting to TRUE:**

```sql
ALTER TABLE venues ADD COLUMN active boolean DEFAULT TRUE;
```

## Day 2 · Advanced queries, code and rules

Day 2 shows that PostgreSQL is more than a box that stores rows. It can summarize data, run code, react to changes automatically, and even rewrite the queries you send it.

First the book adds more data. The handy trick here is a **subquery** inside `INSERT`, so you can name a venue instead of remembering its ID:

```sql
INSERT INTO events (title, starts, ends, venue_id)
VALUES ('Moby', '2012-02-06 21:00', '2012-02-06 23:00', (
  SELECT venue_id FROM venues WHERE name = 'Crystal Ballroom'
));
```

To put an apostrophe inside a string, double it: `'Valentine''s Day'`. After adding a *Wedding* and *Dinner with Mom* (at a venue called *My Place*) and *Valentine's Day*, the events table holds:

| title | starts | venue_id |
|---|---|---|
| Moby | 2012-02-06 21:00 | 1 (Crystal Ballroom) |
| LARP Club | 2012-02-15 17:30 | 2 (Voodoo Donuts) |
| Wedding | 2012-02-26 21:00 | 2 (Voodoo Donuts) |
| Dinner with Mom | 2012-02-26 18:00 | 3 (My Place) |
| Valentine's Day | 2012-02-14 00:00 | NULL |
| April Fools Day | 2012-04-01 00:00 | NULL |
| Christmas Day | 2012-12-25 00:00 | NULL |

### Step 1: Aggregate functions

An **aggregate function** turns many rows into one value: `count()`, `min()`, `max()`, `sum()`, `avg()`.

```sql
SELECT count(title) FROM events WHERE title LIKE '%Day%';    -- 3
```

In `LIKE`, `%` means "any characters", so `'%Day%'` means "contains Day".

```sql
SELECT min(starts), max(ends)
FROM events INNER JOIN venues ON events.venue_id = venues.venue_id
WHERE venues.name = 'Crystal Ballroom';
```

Aggregates on their own are limited. To count events *per venue* you would need one query per venue (`WHERE venue_id = 1`, `= 2`, `= 3`, `IS NULL`...), which does not scale.

### Step 2: GROUP BY and HAVING

`GROUP BY` runs all of those queries at once. It sorts rows into groups, then applies the aggregate to each group:

```sql
SELECT venue_id, count(*) FROM events GROUP BY venue_id;
```

```text
 venue_id | count
----------+-------
        1 |     1
        2 |     2
        3 |     1
          |     3      <- the NULL group: the three holidays
```

`HAVING` filters **groups** the way `WHERE` filters **rows**:

```sql
SELECT venue_id, count(*)
FROM events
WHERE venue_id IS NOT NULL      -- filter rows BEFORE grouping
GROUP BY venue_id
HAVING count(*) >= 2;           -- filter groups AFTER counting
-- venue 2, count 2
```

:::fig **The order in which SQL clauses run.** You write SELECT first, but the database runs it almost last. That is why WHERE cannot use `count(*)` (no groups exist yet) while HAVING can.
<svg class="dg wide" viewBox="0 0 720 120">
<rect x="0" y="30" width="100" height="50" rx="8" class="box"/><text x="50" y="52" text-anchor="middle" class="b mono">FROM</text><text x="50" y="70" text-anchor="middle" class="s">pick tables</text>
<rect x="124" y="30" width="100" height="50" rx="8" class="box"/><text x="174" y="52" text-anchor="middle" class="b mono">WHERE</text><text x="174" y="70" text-anchor="middle" class="s">filter rows</text>
<rect x="248" y="30" width="100" height="50" rx="8" class="ba"/><text x="298" y="52" text-anchor="middle" class="b mono">GROUP BY</text><text x="298" y="70" text-anchor="middle" class="s">make groups</text>
<rect x="372" y="30" width="100" height="50" rx="8" class="ba"/><text x="422" y="52" text-anchor="middle" class="b mono">HAVING</text><text x="422" y="70" text-anchor="middle" class="s">filter groups</text>
<rect x="496" y="30" width="100" height="50" rx="8" class="box"/><text x="546" y="52" text-anchor="middle" class="b mono">SELECT</text><text x="546" y="70" text-anchor="middle" class="s">pick columns</text>
<rect x="620" y="30" width="100" height="50" rx="8" class="box"/><text x="670" y="52" text-anchor="middle" class="b mono">ORDER BY</text><text x="670" y="70" text-anchor="middle" class="s">sort</text>
<line x1="100" y1="55" x2="122" y2="55" class="ln" marker-end="url(#arr)"/>
<line x1="224" y1="55" x2="246" y2="55" class="ln" marker-end="url(#arr)"/>
<line x1="348" y1="55" x2="370" y2="55" class="ln" marker-end="url(#arr)"/>
<line x1="472" y1="55" x2="494" y2="55" class="ln" marker-end="url(#arr)"/>
<line x1="596" y1="55" x2="618" y2="55" class="ln" marker-end="url(#arr)"/>
<text x="360" y="108" text-anchor="middle" class="s">logical order of evaluation</text>
</svg>
:::

`GROUP BY` without an aggregate returns the unique values. That is so common that SQL has a shortcut, `DISTINCT`. These two queries return the same result:

```sql
SELECT venue_id FROM events GROUP BY venue_id;
SELECT DISTINCT venue_id FROM events;
```

:::deep The book's MySQL warning
Older MySQL versions let you write `SELECT title, venue_id, count(*) ... GROUP BY venue_id` even though `title` is not grouped. MySQL quietly returned the title of a **random row** in each group. That looks like it works but gives misleading data. PostgreSQL refuses with an error. Since MySQL 5.7 (2015), MySQL also refuses by default (`ONLY_FULL_GROUP_BY`).
:::

### Step 3: Window functions

Try to show each event's title next to its venue's event count:

```sql
SELECT title, venue_id, count(*) FROM events GROUP BY venue_id;
-- ERROR: column "events.title" must appear in the GROUP BY clause
--        or be used in an aggregate function
```

Venue 2 has two titles (LARP Club and Wedding), and GROUP BY squeezes them into one row, so PostgreSQL cannot know which title to show. A **window function** computes over a group **without squeezing the rows together**:

```sql
SELECT title, venue_id, count(*) OVER (PARTITION BY venue_id) FROM events;
```

```text
      title      | venue_id | count
-----------------+----------+-------
 Moby            |        1 |     1
 LARP Club       |        2 |     2
 Wedding         |        2 |     2
 Dinner with Mom |        3 |     1
 April Fools Day |          |     3
 Christmas Day   |          |     3
 Valentine's Day |          |     3
```

:::fig **GROUP BY versus a window function.** Both compute a count per venue. GROUP BY returns one row per group. The window function keeps every row and writes the group's count beside each one.
<svg class="dg wide" viewBox="0 0 720 250">
<text x="105" y="20" text-anchor="middle" class="b">events (7 rows)</text>
<g class="mono">
<rect x="10" y="30" width="190" height="200" rx="6" class="box"/>
<text x="22" y="54">Moby</text><text x="188" y="54" text-anchor="end">1</text>
<text x="22" y="80">LARP Club</text><text x="188" y="80" text-anchor="end" class="ta b">2</text>
<text x="22" y="106">Wedding</text><text x="188" y="106" text-anchor="end" class="ta b">2</text>
<text x="22" y="132">Dinner w/ Mom</text><text x="188" y="132" text-anchor="end">3</text>
<text x="22" y="158">April Fools</text><text x="188" y="158" text-anchor="end" class="tw b">∅</text>
<text x="22" y="184">Christmas</text><text x="188" y="184" text-anchor="end" class="tw b">∅</text>
<text x="22" y="210">Valentine's</text><text x="188" y="210" text-anchor="end" class="tw b">∅</text>
</g>
<line x1="206" y1="90" x2="268" y2="70" class="ln" marker-end="url(#arr)"/>
<text x="350" y="20" text-anchor="middle" class="b">GROUP BY venue_id</text>
<rect x="275" y="30" width="150" height="110" rx="6" class="ba"/>
<g class="mono">
<text x="290" y="54">venue 1</text><text x="410" y="54" text-anchor="end">1</text>
<text x="290" y="78">venue 2</text><text x="410" y="78" text-anchor="end" class="ta b">2</text>
<text x="290" y="102">venue 3</text><text x="410" y="102" text-anchor="end">1</text>
<text x="290" y="126">NULL</text><text x="410" y="126" text-anchor="end" class="tw b">3</text>
</g>
<text x="350" y="160" text-anchor="middle" class="s">4 rows, titles are gone</text>
<text x="575" y="20" text-anchor="middle" class="b">count(*) OVER (PARTITION BY …)</text>
<rect x="450" y="30" width="260" height="200" rx="6" class="bg"/>
<g class="mono">
<text x="462" y="54">Moby</text><text x="640" y="54">1</text><text x="698" y="54" text-anchor="end">1</text>
<text x="462" y="80">LARP Club</text><text x="640" y="80">2</text><text x="698" y="80" text-anchor="end" class="ta b">2</text>
<text x="462" y="106">Wedding</text><text x="640" y="106">2</text><text x="698" y="106" text-anchor="end" class="ta b">2</text>
<text x="462" y="132">Dinner w/ Mom</text><text x="640" y="132">3</text><text x="698" y="132" text-anchor="end">1</text>
<text x="462" y="158">April Fools</text><text x="640" y="158">∅</text><text x="698" y="158" text-anchor="end" class="tw b">3</text>
<text x="462" y="184">Christmas</text><text x="640" y="184">∅</text><text x="698" y="184" text-anchor="end" class="tw b">3</text>
<text x="462" y="210">Valentine's</text><text x="640" y="210">∅</text><text x="698" y="210" text-anchor="end" class="tw b">3</text>
</g>
<text x="580" y="246" text-anchor="middle" class="s">7 rows, each with its group's count</text>
<path d="M202,216 L230,216 L230,232 L440,232" class="ln dash" marker-end="url(#arr)"/>
</svg>
:::

Read `count(*) OVER (PARTITION BY venue_id)` as "the count, computed **over** the **partition** of rows that share this row's `venue_id`". `PARTITION BY` is like `GROUP BY` without the squashing.

:::example Window functions people actually use
```sql
-- rank events by start time within each venue
SELECT title, venue_id,
       rank() OVER (PARTITION BY venue_id ORDER BY starts) AS nth_at_venue
FROM events;

-- how long since the previous event? (lag looks at the previous row)
SELECT title, starts,
       starts - lag(starts) OVER (ORDER BY starts) AS gap
FROM events;

-- running total
SELECT title, count(*) OVER (ORDER BY starts) AS events_so_far FROM events;
```
:::

In 2012 window functions were rare in open-source databases. Today MySQL 8, SQLite and MariaDB support them too.

### Step 4: Transactions

**All or nothing** is the transaction motto. Either every command in a transaction succeeds, or none of them do and everything is rolled back as if it never happened.

```sql
BEGIN TRANSACTION;
  DELETE FROM events;      -- oops
ROLLBACK;                  -- undo everything since BEGIN
SELECT * FROM events;      -- all events are still there
```

The classic example is a bank transfer, where money must leave one account and arrive in another:

```sql
BEGIN TRANSACTION;
  UPDATE account SET total = total + 5000.0 WHERE account_id = 1337;
  UPDATE account SET total = total - 5000.0 WHERE account_id = 45887;
END;      -- same as COMMIT
```

:::fig **Why the bank transfer needs a transaction.** Without one, a crash between the two updates leaves 5,000 created out of thin air. With one, PostgreSQL rolls the first update back during recovery, so the accounts are exactly as they were before.
<svg class="dg wide" viewBox="0 0 720 230">
<text x="10" y="22" class="b tr">Without a transaction</text>
<rect x="10" y="34" width="150" height="56" rx="8" class="box"/><text x="85" y="56" text-anchor="middle" class="mono">#1337 + 5000</text><text x="85" y="76" text-anchor="middle" class="s">saved</text>
<line x1="160" y1="62" x2="220" y2="62" class="ln" marker-end="url(#arr)"/>
<rect x="225" y="34" width="120" height="56" rx="8" class="br"/><text x="285" y="58" text-anchor="middle" class="b tr">CRASH</text><text x="285" y="76" text-anchor="middle" class="s">power cut</text>
<line x1="345" y1="62" x2="405" y2="62" class="ln dash" marker-end="url(#arr)"/>
<rect x="410" y="34" width="150" height="56" rx="8" class="box" stroke-dasharray="5 4"/><text x="485" y="56" text-anchor="middle" class="mono tm">#45887 − 5000</text><text x="485" y="76" text-anchor="middle" class="s">never runs</text>
<text x="580" y="56" class="tr b">+5000 appears</text><text x="580" y="74" class="s">from nowhere</text>
<text x="10" y="130" class="b tg">With BEGIN … COMMIT</text>
<rect x="10" y="142" width="700" height="72" rx="10" class="bg" fill-opacity="0.5"/>
<rect x="24" y="152" width="150" height="52" rx="8" class="box"/><text x="99" y="174" text-anchor="middle" class="mono">#1337 + 5000</text><text x="99" y="192" text-anchor="middle" class="s">not yet final</text>
<line x1="174" y1="178" x2="230" y2="178" class="ln" marker-end="url(#arr)"/>
<rect x="235" y="152" width="120" height="52" rx="8" class="br"/><text x="295" y="176" text-anchor="middle" class="b tr">CRASH</text><text x="295" y="194" text-anchor="middle" class="s">power cut</text>
<line x1="355" y1="178" x2="410" y2="178" class="lgr" marker-end="url(#arrg)"/>
<rect x="415" y="152" width="150" height="52" rx="8" class="box"/><text x="490" y="174" text-anchor="middle" class="b">on restart:</text><text x="490" y="192" text-anchor="middle" class="s">roll back #1337</text>
<text x="580" y="174" class="tg b">Balances safe.</text><text x="580" y="192" class="s">Nothing lost or invented.</text>
</svg>
:::

PostgreSQL transactions are **ACID**:

| Letter | Property | Meaning |
|---|---|---|
| A | Atomic | All operations succeed or none do. |
| C | Consistent | The data always moves from one valid state to another; constraints are never broken. |
| I | Isolated | Transactions running at the same time do not interfere with each other. |
| D | Durable | Once committed, the change survives a crash. |

:::warn Two different "consistencies"
The C in **ACID** means "the database's rules are never broken". The C in the **CAP theorem** (Appendix A in this guide) means "every server in a cluster returns the latest value". The book points out the difference because the same word is used for two unrelated ideas.
:::

:::deep You are always in a transaction
Every command you type in `psql` is automatically wrapped in its own little transaction. If a `DELETE FROM account WHERE total < 20;` crashes halfway through, you will not end up with half the rows deleted. `BEGIN` simply lets you group several commands into one transaction.
:::

### Step 5: Stored procedures

Everything so far has been **declarative**. Sometimes you need real logic: variables, `IF`, loops. You can run that logic in your application, or inside the database as a **stored procedure** (PostgreSQL calls them functions).

The book's example adds an event by **venue name**, and creates the venue first if it does not exist. It returns `true` if a new venue was created.

```sql
CREATE OR REPLACE FUNCTION add_event( title text, starts timestamp,
  ends timestamp, venue text, postal varchar(9), country char(2) )
RETURNS boolean AS $$
DECLARE
  did_insert boolean := false;
  found_count integer;
  the_venue_id integer;
BEGIN
  -- 1. look for the venue (ILIKE = case-insensitive LIKE)
  SELECT venue_id INTO the_venue_id
  FROM venues v
  WHERE v.postal_code = postal AND v.country_code = country AND v.name ILIKE venue
  LIMIT 1;

  -- 2. not found? create it and remember its new id
  IF the_venue_id IS NULL THEN
    INSERT INTO venues (name, postal_code, country_code)
    VALUES (venue, postal, country)
    RETURNING venue_id INTO the_venue_id;
    did_insert := true;
  END IF;

  -- a message for the console, not an error
  RAISE NOTICE 'Venue found %', the_venue_id;

  -- 3. insert the event
  INSERT INTO events (title, starts, ends, venue_id)
  VALUES (title, starts, ends, the_venue_id);

  RETURN did_insert;
END;
$$ LANGUAGE plpgsql;
```

```sql
SELECT add_event('House Party', '2012-05-03 23:00', '2012-05-04 02:00',
                 'Run''s House', '97205', 'us');
-- t   (true: a new venue "Run's House" was created)
```

How to read the pieces:

- `$$ ... $$` wraps the function body so you do not have to escape every quote inside it.
- `DECLARE` lists local variables; `:=` assigns a value.
- `SELECT ... INTO var` stores a query result in a variable.
- **PL/pgSQL** (Procedural Language/PostgreSQL) is the built-in language. PostgreSQL also supports Tcl, Perl and Python, with extensions for many more.

:::fig **Why stored procedures can be faster.** Done from the application, "find or create the venue, then add the event" needs up to three network round trips. As a stored procedure it needs one. With thousands of rows to process, avoiding the network can make a ten-fold difference.
<svg class="dg wide" viewBox="0 0 720 210">
<text x="175" y="20" text-anchor="middle" class="b">Logic in the application</text>
<rect x="10" y="34" width="90" height="160" rx="8" class="box"/><text x="55" y="118" text-anchor="middle" class="b">App</text>
<rect x="250" y="34" width="90" height="160" rx="8" class="ba"/><text x="295" y="118" text-anchor="middle" class="b">DB</text>
<line x1="102" y1="56" x2="246" y2="56" class="ln" marker-end="url(#arr)"/><text x="175" y="50" text-anchor="middle" class="s">SELECT venue</text>
<line x1="246" y1="76" x2="102" y2="76" class="ln dash" marker-end="url(#arr)"/><text x="175" y="90" text-anchor="middle" class="s">not found</text>
<line x1="102" y1="112" x2="246" y2="112" class="ln" marker-end="url(#arr)"/><text x="175" y="106" text-anchor="middle" class="s">INSERT venue</text>
<line x1="246" y1="130" x2="102" y2="130" class="ln dash" marker-end="url(#arr)"/>
<line x1="102" y1="160" x2="246" y2="160" class="ln" marker-end="url(#arr)"/><text x="175" y="154" text-anchor="middle" class="s">INSERT event</text>
<line x1="246" y1="178" x2="102" y2="178" class="ln dash" marker-end="url(#arr)"/>
<line x1="370" y1="20" x2="370" y2="200" class="ln2 dash"/>
<text x="545" y="20" text-anchor="middle" class="b">Logic in a stored procedure</text>
<rect x="390" y="34" width="90" height="160" rx="8" class="box"/><text x="435" y="118" text-anchor="middle" class="b">App</text>
<rect x="620" y="34" width="90" height="160" rx="8" class="ba"/><text x="665" y="72" text-anchor="middle" class="b">DB</text>
<text x="665" y="100" text-anchor="middle" class="s">find venue</text><text x="665" y="118" text-anchor="middle" class="s">create venue</text><text x="665" y="136" text-anchor="middle" class="s">add event</text>
<line x1="482" y1="100" x2="616" y2="100" class="la" marker-end="url(#arra)"/><text x="549" y="94" text-anchor="middle" class="s">add_event(…)</text>
<line x1="616" y1="124" x2="482" y2="124" class="la dash" marker-end="url(#arra)"/><text x="549" y="140" text-anchor="middle" class="s">true</text>
</svg>
:::

#### Should code live in the database?

This is the first time the book raises a question that keeps coming back: **does the code belong in your application or in the database?**

| Code in the database | Code in the application |
|---|---|
| Much faster for data-heavy work: no shipping thousands of rows over the network. | Everything in one language, one code base, one test suite. |
| Ties your application to this database's features (**vendor lock-in**). | Easier to switch databases later. |
| Logic is split across two places and two styles of programming. | Slower when the calculation needs lots of rows. |

The authors explain where the popular rule "no logic in the database" came from: in the 1990s, commercial database vendors pushed proprietary features and then charged huge licence and consulting fees once customers depended on them. Their view is balanced: learn what your database can do before you rule its tools out.

### Step 6: Triggers

A **trigger** automatically runs a function when something happens to a table: an `INSERT`, `UPDATE` or `DELETE`, either `BEFORE` or `AFTER` it. The database enforces the behavior, so no application can forget it.

The book builds an **audit log** that records the old version of an event every time someone changes it:

```sql
-- 1. a table to hold the history (no primary key needed for a log)
CREATE TABLE logs (
  event_id   integer,
  old_title  varchar(255),
  old_starts timestamp,
  old_ends   timestamp,
  logged_at  timestamp DEFAULT current_timestamp
);

-- 2. the trigger function: OLD = row before the change, NEW = row after
CREATE OR REPLACE FUNCTION log_event() RETURNS trigger AS $$
DECLARE
BEGIN
  INSERT INTO logs (event_id, old_title, old_starts, old_ends)
  VALUES (OLD.event_id, OLD.title, OLD.starts, OLD.ends);
  RAISE NOTICE 'Someone just changed event #%', OLD.event_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3. attach it to the table
CREATE TRIGGER log_events
  AFTER UPDATE ON events
  FOR EACH ROW EXECUTE PROCEDURE log_event();
```

```sql
UPDATE events SET ends = '2012-05-04 01:00:00' WHERE title = 'House Party';
-- NOTICE: Someone just changed event #9

SELECT event_id, old_title, old_ends, logged_at FROM logs;
--  9 | House Party | 2012-05-04 02:00:00 | 2011-02-26 15:50:31.939
```

:::fig **How the audit trigger fires.** The application only sends an UPDATE. PostgreSQL notices the trigger on the events table and calls `log_event()` for each changed row, which copies the old values into `logs`.
<svg class="dg" viewBox="0 0 720 170">
<rect x="10" y="50" width="150" height="60" rx="8" class="box"/><text x="85" y="76" text-anchor="middle" class="b">UPDATE events</text><text x="85" y="96" text-anchor="middle" class="s">from any app</text>
<line x1="160" y1="80" x2="218" y2="80" class="ln" marker-end="url(#arr)"/>
<rect x="222" y="50" width="140" height="60" rx="8" class="ba"/><text x="292" y="76" text-anchor="middle" class="b">events</text><text x="292" y="96" text-anchor="middle" class="s">row changes</text>
<line x1="362" y1="80" x2="420" y2="80" class="lv" marker-end="url(#arrv)"/>
<text x="391" y="36" text-anchor="middle" class="s tv b">AFTER UPDATE</text><line x1="391" y1="42" x2="391" y2="74" class="lv dash"/>
<rect x="424" y="50" width="140" height="60" rx="8" class="bv"/><text x="494" y="76" text-anchor="middle" class="b mono">log_event()</text><text x="494" y="96" text-anchor="middle" class="s">reads OLD.*</text>
<line x1="564" y1="80" x2="618" y2="80" class="ln" marker-end="url(#arr)"/>
<rect x="622" y="50" width="90" height="60" rx="8" class="box"/><text x="667" y="76" text-anchor="middle" class="b">logs</text><text x="667" y="96" text-anchor="middle" class="s">old values</text>
<text x="360" y="150" text-anchor="middle" class="s">BEFORE / AFTER · INSERT / UPDATE / DELETE · FOR EACH ROW or FOR EACH STATEMENT</text>
</svg>
:::

### Step 7: Views

A **view** is a saved query with a name. You query it like a table, but it stores no data: each time you use it, PostgreSQL runs the query underneath.

```sql
CREATE VIEW holidays AS
  SELECT event_id AS holiday_id, title AS name, starts AS date
  FROM events
  WHERE title LIKE '%Day%' AND venue_id IS NULL;

SELECT name, to_char(date, 'Month DD, YYYY') AS date
FROM holidays
WHERE date <= '2012-04-01';
```

```text
      name       |        date
-----------------+--------------------
 April Fools Day | April     01, 2012
 Valentine's Day | February  14, 2012
```

The query underneath can be as complicated as you like; the user only sees a simple table.

The book then adds an **array column**, one of PostgreSQL's less common types, and includes it in the view:

```sql
ALTER TABLE events ADD colors text ARRAY;

CREATE OR REPLACE VIEW holidays AS
  SELECT event_id AS holiday_id, title AS name, starts AS date, colors
  FROM events
  WHERE title LIKE '%Day%' AND venue_id IS NULL;
```

### Step 8: Rules

In the book, updating the view fails:

```sql
UPDATE holidays SET colors = '{"red","green"}' WHERE name = 'Christmas Day';
-- ERROR: cannot update a view
-- HINT: You need an unconditional ON UPDATE DO INSTEAD rule.
```

To understand the fix, you need to know how PostgreSQL runs a query.

:::fig **How a SQL statement travels through PostgreSQL.** The parser turns your text into a query tree. The rewriter applies rules, and views are rules, so a view is replaced by the query it stands for. The planner then chooses the fastest way to run it, and the executor produces the rows.
<svg class="dg wide" viewBox="0 0 720 170">
<rect x="0" y="50" width="100" height="56" rx="8" class="box"/><text x="50" y="74" text-anchor="middle" class="b">SQL text</text><text x="50" y="92" text-anchor="middle" class="s">from psql</text>
<rect x="125" y="50" width="110" height="56" rx="8" class="ba"/><text x="180" y="74" text-anchor="middle" class="b">Parser</text><text x="180" y="92" text-anchor="middle" class="s">text → query tree</text>
<rect x="260" y="50" width="120" height="56" rx="8" class="bv"/><text x="320" y="74" text-anchor="middle" class="b">Rewriter</text><text x="320" y="92" text-anchor="middle" class="s">applies RULES</text>
<rect x="405" y="50" width="120" height="56" rx="8" class="ba"/><text x="465" y="74" text-anchor="middle" class="b">Planner</text><text x="465" y="92" text-anchor="middle" class="s">picks fastest plan</text>
<rect x="550" y="50" width="100" height="56" rx="8" class="ba"/><text x="600" y="74" text-anchor="middle" class="b">Executor</text><text x="600" y="92" text-anchor="middle" class="s">runs it</text>
<line x1="100" y1="78" x2="123" y2="78" class="ln" marker-end="url(#arr)"/>
<line x1="235" y1="78" x2="258" y2="78" class="ln" marker-end="url(#arr)"/>
<line x1="380" y1="78" x2="403" y2="78" class="ln" marker-end="url(#arr)"/>
<line x1="525" y1="78" x2="548" y2="78" class="ln" marker-end="url(#arr)"/>
<line x1="650" y1="78" x2="676" y2="78" class="ln" marker-end="url(#arr)"/><text x="682" y="82" class="s">rows</text>
<rect x="255" y="128" width="130" height="34" rx="6" class="box"/><text x="320" y="150" text-anchor="middle" class="s">views + your rules</text>
<line x1="320" y1="126" x2="320" y2="108" class="lv" marker-end="url(#arrv)"/>
<text x="465" y="140" text-anchor="middle" class="s">see it with EXPLAIN</text>
</svg>
:::

A **rule** tells the rewriter how to change the query tree before it runs. In fact, **a view is a rule**. You can prove it with `EXPLAIN VERBOSE`: querying `holidays` and running the view's original `SELECT` on `events` produce exactly the same plan (a sequential scan of `events` with the WHERE condition as a filter).

So to make the view updatable, we write a rule that says "when someone updates `holidays`, do this **instead**":

```sql
CREATE RULE update_holidays AS ON UPDATE TO holidays DO INSTEAD
  UPDATE events
  SET title  = NEW.name,
      starts = NEW.date,
      colors = NEW.colors
  WHERE title = OLD.name;
```

`NEW` holds the values being set, and `OLD` holds the existing row's values. A similar `ON INSERT ... DO INSTEAD INSERT INTO events ...` rule makes inserts work too.

:::modern Views are updatable without rules now
I ran the failing `UPDATE` on PostgreSQL 16 **without any rule, and it worked.** Since PostgreSQL 9.3 (2013), **simple views** (one table, no grouping) are automatically updatable.
- For **complex views** (joins, aggregates), the modern tool is an **`INSTEAD OF` trigger** on the view.
- **Rules** still exist, but the official documentation now recommends triggers for almost everything, because rules rewrite whole queries and can behave in surprising ways (for example with sequences or multi-row statements).
Learn rules for the idea (views are query rewrites), but use triggers in real projects.
:::

### Step 9: Pivot tables with crosstab()

The last exercise builds a **calendar of events per month**: one row per year and one column per month. Turning row values (months) into columns is called a **pivot**.

First, count events per year and month. `extract()` pulls one part out of a date:

```sql
SELECT extract(year from starts) AS year,
       extract(month from starts) AS month, count(*)
FROM events
GROUP BY year, month;
```

`crosstab()` (from the `tablefunc` extension) needs two queries:

1. A **source query** with exactly three columns: **row ID** (year), **category** (month), **value** (count).
2. A **category query** listing every possible column (months 1 to 12). The book uses a temporary table:

```sql
CREATE TEMPORARY TABLE month_count(month INT);
INSERT INTO month_count VALUES (1),(2),(3),(4),(5),(6),(7),(8),(9),(10),(11),(12);
```

You also have to **declare the output columns**. Leave that out and you get *"a column definition list is required for functions returning record"*, because PostgreSQL cannot guess the names or types:

```sql
SELECT * FROM crosstab(
  'SELECT extract(year from starts) as year,
          extract(month from starts) as month, count(*)
   FROM events GROUP BY year, month',
  'SELECT * FROM month_count'
) AS (
  year int,
  jan int, feb int, mar int, apr int, may int, jun int,
  jul int, aug int, sep int, oct int, nov int, dec int
) ORDER BY YEAR;
```

```text
 year | jan | feb | mar | apr | may | jun | jul | aug | sep | oct | nov | dec
------+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----
 2012 |     |   5 |     |   1 |   1 |     |     |     |     |     |     |   1
```

:::fig **What crosstab() does.** It takes long, narrow rows (one per year and month) and spreads them into one wide row per year, with one column per month. Missing combinations become empty cells.
<svg class="dg wide" viewBox="0 0 720 190">
<text x="90" y="20" text-anchor="middle" class="b">source rows</text>
<rect x="10" y="30" width="160" height="140" rx="6" class="box"/>
<g class="mono"><text x="24" y="52" class="b">year mon count</text>
<text x="24" y="78">2012  2    5</text><text x="24" y="102">2012  4    1</text><text x="24" y="126">2012  5    1</text><text x="24" y="150">2012 12    1</text></g>
<line x1="176" y1="100" x2="232" y2="100" class="la" marker-end="url(#arra)"/>
<text x="204" y="90" text-anchor="middle" class="s">pivot</text>
<text x="475" y="20" text-anchor="middle" class="b">crosstab result</text>
<rect x="238" y="60" width="474" height="70" rx="6" class="ba"/>
<line x1="238" y1="90" x2="712" y2="90" class="la"/>
<g class="mono s">
<text x="248" y="80" class="b">year</text>
<text x="298" y="80">jan</text><text x="332" y="80">feb</text><text x="366" y="80">mar</text><text x="400" y="80">apr</text><text x="434" y="80">may</text><text x="468" y="80">jun</text><text x="502" y="80">jul</text><text x="536" y="80">aug</text><text x="570" y="80">sep</text><text x="604" y="80">oct</text><text x="638" y="80">nov</text><text x="672" y="80">dec</text>
<text x="248" y="114" class="b">2012</text>
<text x="340" y="114" class="ta b">5</text><text x="408" y="114" class="ta b">1</text><text x="442" y="114" class="ta b">1</text><text x="680" y="114" class="ta b">1</text>
</g>
</svg>
:::

### Day 2 homework, solved

These answers were tested on PostgreSQL 16.

**1. A rule that turns `DELETE` on venues into "set active to FALSE"** (a *soft delete*, so the row is kept for history):

```sql
CREATE RULE delete_venues AS ON DELETE TO venues DO INSTEAD
  UPDATE venues SET active = FALSE WHERE venue_id = OLD.venue_id;

DELETE FROM venues WHERE name = 'My Place';   -- row is kept, active becomes false
```

**2. Replace the temporary table with `generate_series()`**, which produces the numbers 1 to 12 on the fly:

```sql
SELECT * FROM crosstab(
  'SELECT extract(year from starts)::int AS year,
          extract(month from starts)::int AS month,
          count(*)::int
   FROM events GROUP BY year, month ORDER BY year, month',
  'SELECT generate_series(1,12)'
) AS (year int, jan int, feb int, mar int, apr int, may int, jun int,
      jul int, aug int, sep int, oct int, nov int, dec int)
ORDER BY year;
```

The `::int` casts make the source types match the declared columns.

**3. A month calendar**: weeks as rows, Sunday to Saturday as columns, event counts in the cells (here, February 2012):

```sql
SELECT * FROM crosstab(
  $$SELECT (extract(day from d)::int
            + extract(dow from date_trunc('month', d))::int - 1) / 7 + 1 AS week,
           extract(dow from d)::int AS dow,                 -- 0 = Sunday ... 6 = Saturday
           NULLIF(count(e.event_id), 0)::int AS events      -- blank instead of 0
    FROM generate_series('2012-02-01'::date, '2012-02-29'::date, '1 day') AS g(d)
    LEFT JOIN events e ON e.starts::date = g.d::date
    GROUP BY 1, 2 ORDER BY 1, 2$$,
  $$SELECT generate_series(0, 6)$$
) AS (week int, sun int, mon int, tue int, wed int, thu int, fri int, sat int);
```

```text
 week | sun | mon | tue | wed | thu | fri | sat
------+-----+-----+-----+-----+-----+-----+-----
    1 |     |     |     |     |     |     |
    2 |     |   1 |     |     |     |     |      <- Moby, Monday 6th
    3 |     |     |   1 |   1 |     |     |      <- Valentine's (Tue), LARP Club (Wed)
    4 |     |     |     |     |     |     |
    5 |   2 |     |     |     |     |     |      <- Wedding + Dinner, Sunday 26th
```

How it works: `generate_series` creates every day of the month and the `LEFT JOIN` keeps days with no events, so empty weeks still appear. The week formula shifts each day by the weekday on which the month starts (1 February 2012 was a Wednesday), so weeks begin on Sunday. Writing the queries between `$$` saves you from doubling every quote.

:::modern Other Day 2 changes
- The book's "stored procedures" are technically `FUNCTION`s. PostgreSQL 11 added real `CREATE PROCEDURE`, called with `CALL`, which can commit transactions part-way through.
- In triggers, `EXECUTE PROCEDURE` is now written `EXECUTE FUNCTION` (the old spelling still works).
- The `createlang` command was removed in PostgreSQL 10. Use `CREATE EXTENSION plpython3u;` and friends instead.
- `SERIAL` still works, but the SQL-standard `GENERATED ALWAYS AS IDENTITY` is now recommended.
:::

## Day 3 · Full-text and multidimensions

Day 3 builds a small **movie recommendation system** and uses it to explore PostgreSQL's text-search and multidimensional features. Most of these come from contrib extensions, which is the authors' point: extensions are what make PostgreSQL shine.

### Step 1: The movie schema

:::fig **The Day 3 schema.** Movies and actors have a many-to-many relationship, stored in the `movies_actors` join table. Each movie's `genre` is a cube: an 18-number vector that scores the movie in every genre. The `genres` table says which position in the vector belongs to which genre.
<svg class="dg wide" viewBox="0 0 720 262">
<rect x="10" y="40" width="160" height="100" rx="8" class="ba"/>
<text x="90" y="62" text-anchor="middle" class="b">genres</text><line x1="10" y1="72" x2="170" y2="72" class="la"/>
<text x="22" y="94" class="mono">name</text><text x="160" y="94" text-anchor="end" class="s">UNIQUE</text>
<text x="22" y="116" class="mono">position</text><text x="160" y="116" text-anchor="end" class="s">UNIQUE</text>
<rect x="210" y="40" width="160" height="110" rx="8" class="ba"/>
<text x="290" y="62" text-anchor="middle" class="b">movies</text><line x1="210" y1="72" x2="370" y2="72" class="la"/>
<text x="222" y="94" class="mono">movie_id</text><text x="360" y="94" text-anchor="end" class="s b ta">PK</text>
<text x="222" y="116" class="mono">title</text>
<text x="222" y="138" class="mono">genre</text><text x="360" y="138" text-anchor="end" class="s b tv">cube</text>
<rect x="410" y="40" width="150" height="90" rx="8" class="ba"/>
<text x="485" y="62" text-anchor="middle" class="b">movies_actors</text><line x1="410" y1="72" x2="560" y2="72" class="la"/>
<text x="422" y="94" class="mono">movie_id</text><text x="550" y="94" text-anchor="end" class="s b ta">FK</text>
<text x="422" y="116" class="mono">actor_id</text><text x="550" y="116" text-anchor="end" class="s b ta">FK</text>
<rect x="595" y="40" width="115" height="90" rx="8" class="ba"/>
<text x="652" y="62" text-anchor="middle" class="b">actors</text><line x1="595" y1="72" x2="710" y2="72" class="la"/>
<text x="607" y="94" class="mono">actor_id</text><text x="700" y="94" text-anchor="end" class="s b ta">PK</text>
<text x="607" y="116" class="mono">name</text>
<line x1="408" y1="90" x2="373" y2="90" class="ln" marker-end="url(#arr)"/>
<line x1="562" y1="112" x2="592" y2="90" class="ln" marker-end="url(#arr)"/>
<path d="M172,116 L190,116 L190,134 L207,134" class="ln dash"/>
<text x="190" y="160" text-anchor="middle" class="s">position → index</text>
<text x="10" y="196" class="b">Star Wars genre cube</text>
<g class="mono s">
<rect x="10" y="206" width="700" height="30" rx="4" class="box"/>
<text x="20" y="226">0</text><text x="58" y="226" class="tv b">7</text><text x="96" y="226">0</text><text x="134" y="226">0</text><text x="172" y="226">0</text><text x="210" y="226">0</text><text x="248" y="226">0</text><text x="286" y="226">0</text><text x="324" y="226">0</text><text x="362" y="226" class="tv b">7</text><text x="400" y="226">0</text><text x="438" y="226">0</text><text x="476" y="226">0</text><text x="514" y="226">0</text><text x="552" y="226" class="tv b">10</text><text x="596" y="226">0</text><text x="634" y="226">0</text><text x="672" y="226">0</text>
</g>
<text x="58" y="250" class="s tv" text-anchor="middle">Adventure</text><text x="362" y="250" class="s tv" text-anchor="middle">Fantasy</text><text x="556" y="250" class="s tv" text-anchor="middle">SciFi</text>
</svg>
:::

```sql
CREATE TABLE genres (
  name text UNIQUE,
  position integer
);
CREATE TABLE movies (
  movie_id SERIAL PRIMARY KEY,
  title text,
  genre cube
);
CREATE TABLE actors (
  actor_id SERIAL PRIMARY KEY,
  name text
);
CREATE TABLE movies_actors (
  movie_id integer REFERENCES movies NOT NULL,
  actor_id integer REFERENCES actors NOT NULL,
  UNIQUE (movie_id, actor_id)
);
CREATE INDEX movies_actors_movie_id ON movies_actors (movie_id);
CREATE INDEX movies_actors_actor_id ON movies_actors (actor_id);
CREATE INDEX movies_genres_cube ON movies USING gist (genre);
```

There are 18 genres (Action, Adventure, Animation, Comedy, Crime, Disaster, Documentary, Drama, Eastern, Fantasy, History, Horror, Musical, Romance, SciFi, Sport, Thriller, Western), each scored from 0 to 10. The book's download includes a `movies_data.sql` file that fills all of this in.

:::deep What is a many-to-many join table?
One movie has many actors, and one actor appears in many movies. You cannot store that in a single column of either table, so a third table, `movies_actors`, holds one row per (movie, actor) pair. The `UNIQUE (movie_id, actor_id)` constraint stops the same pair being stored twice. This pattern is everywhere in relational design: students and courses, tags and posts, orders and products.
:::

### Step 2: SQL-standard string matching

`LIKE` and `ILIKE` (case-insensitive `LIKE`) are the simplest text search. `%` matches any number of characters and `_` matches exactly one:

```sql
SELECT title FROM movies WHERE title ILIKE 'stardust%';
-- Stardust, Stardust Memories

SELECT title FROM movies WHERE title ILIKE 'stardust_%';
-- Stardust Memories   (at least one more character required)
```

### Step 3: Regular expressions

For more power, PostgreSQL supports POSIX **regular expressions** with the `~` operator family:

| Operator | Meaning |
|---|---|
| `~` | Matches, case-sensitive. |
| `~*` | Matches, case-insensitive. |
| `!~` | Does not match, case-sensitive. |
| `!~*` | Does not match, case-insensitive. |

```sql
-- how many titles do NOT start with "the"?
SELECT COUNT(*) FROM movies WHERE title !~* '^the.*';
```

To make such searches fast, index the lower-cased title with a pattern-matching operator class:

```sql
CREATE INDEX movies_title_pattern ON movies (lower(title) text_pattern_ops);
```

### Step 4: Levenshtein distance

What if the user misspells the title? The **Levenshtein distance** counts the minimum number of single-character edits (insert, delete, substitute) needed to turn one string into another. It comes from the `fuzzystrmatch` extension.

:::fig **Levenshtein distance from "bat" to "fads" is 3.** Two letters are substituted and one is added. The smaller the number, the more similar the strings.
<svg class="dg" viewBox="0 0 720 150">
<g class="mono lg">
<rect x="20" y="40" width="40" height="44" rx="6" class="box"/><text x="40" y="69" text-anchor="middle" class="lg mono">b</text>
<rect x="66" y="40" width="40" height="44" rx="6" class="box"/><text x="86" y="69" text-anchor="middle" class="lg mono">a</text>
<rect x="112" y="40" width="40" height="44" rx="6" class="box"/><text x="132" y="69" text-anchor="middle" class="lg mono">t</text>
</g>
<line x1="170" y1="62" x2="220" y2="62" class="ln" marker-end="url(#arr)"/>
<rect x="230" y="40" width="40" height="44" rx="6" class="bw"/><text x="250" y="69" text-anchor="middle" class="lg mono">f</text>
<rect x="276" y="40" width="40" height="44" rx="6" class="box"/><text x="296" y="69" text-anchor="middle" class="lg mono">a</text>
<rect x="322" y="40" width="40" height="44" rx="6" class="box"/><text x="342" y="69" text-anchor="middle" class="lg mono">t</text>
<text x="296" y="110" text-anchor="middle" class="s">substitute b→f (1)</text>
<line x1="380" y1="62" x2="420" y2="62" class="ln" marker-end="url(#arr)"/>
<rect x="430" y="40" width="40" height="44" rx="6" class="box"/><text x="450" y="69" text-anchor="middle" class="lg mono">f</text>
<rect x="476" y="40" width="40" height="44" rx="6" class="box"/><text x="496" y="69" text-anchor="middle" class="lg mono">a</text>
<rect x="522" y="40" width="40" height="44" rx="6" class="bw"/><text x="542" y="69" text-anchor="middle" class="lg mono">d</text>
<rect x="568" y="40" width="40" height="44" rx="6" class="bg"/><text x="588" y="69" text-anchor="middle" class="lg mono">s</text>
<text x="519" y="110" text-anchor="middle" class="s">substitute t→d (2), insert s (3)</text>
<text x="660" y="69" class="lg ta">= 3</text>
<text x="360" y="140" text-anchor="middle" class="s">levenshtein('bat','fad') = 2 · levenshtein('bat','fat') = 1 · levenshtein('bat','bat') = 0</text>
</svg>
:::

```sql
SELECT levenshtein('bat', 'fads');                         -- 3
SELECT levenshtein('bat', 'fad') fad,
       levenshtein('bat', 'fat') fat,
       levenshtein('bat', 'bad') bad;                     -- 2 | 1 | 1

-- find a title despite a typo
SELECT movie_id, title FROM movies
WHERE levenshtein(lower(title), lower('a hard day nght')) <= 3;
-- 245 | A Hard Day's Night
```

Lower-casing both sides first matters, because otherwise every case difference counts as an edit.

### Step 5: Trigrams

A **trigram** is a group of three consecutive characters. The `pg_trgm` extension breaks a string into all its trigrams (after lower-casing and padding with spaces), then measures how many trigrams two strings share. More shared trigrams means more similar strings.

```sql
SELECT show_trgm('Avatar');
-- {"  a"," av","ar ",ata,ava,tar,vat}
```

:::fig **Trigram matching.** Both strings are split into three-letter pieces. "Avatar" and the typo "Avatre" share several pieces, so their similarity is 0.4, above the default threshold of 0.3, and `title % 'Avatre'` finds the movie.
<svg class="dg" viewBox="0 0 720 170">
<text x="20" y="30" class="b mono">Avatar</text>
<g class="mono s">
<rect x="110" y="14" width="50" height="26" rx="5" class="bg"/><text x="135" y="32" text-anchor="middle">"  a"</text>
<rect x="166" y="14" width="50" height="26" rx="5" class="bg"/><text x="191" y="32" text-anchor="middle">" av"</text>
<rect x="222" y="14" width="50" height="26" rx="5" class="bg"/><text x="247" y="32" text-anchor="middle">ava</text>
<rect x="278" y="14" width="50" height="26" rx="5" class="bg"/><text x="303" y="32" text-anchor="middle">vat</text>
<rect x="334" y="14" width="50" height="26" rx="5" class="box"/><text x="359" y="32" text-anchor="middle">ata</text>
<rect x="390" y="14" width="50" height="26" rx="5" class="box"/><text x="415" y="32" text-anchor="middle">tar</text>
<rect x="446" y="14" width="50" height="26" rx="5" class="box"/><text x="471" y="32" text-anchor="middle">"ar "</text>
</g>
<text x="20" y="90" class="b mono">Avatre</text>
<g class="mono s">
<rect x="110" y="74" width="50" height="26" rx="5" class="bg"/><text x="135" y="92" text-anchor="middle">"  a"</text>
<rect x="166" y="74" width="50" height="26" rx="5" class="bg"/><text x="191" y="92" text-anchor="middle">" av"</text>
<rect x="222" y="74" width="50" height="26" rx="5" class="bg"/><text x="247" y="92" text-anchor="middle">ava</text>
<rect x="278" y="74" width="50" height="26" rx="5" class="bg"/><text x="303" y="92" text-anchor="middle">vat</text>
<rect x="334" y="74" width="50" height="26" rx="5" class="box"/><text x="359" y="92" text-anchor="middle">atr</text>
<rect x="390" y="74" width="50" height="26" rx="5" class="box"/><text x="415" y="92" text-anchor="middle">tre</text>
<rect x="446" y="74" width="50" height="26" rx="5" class="box"/><text x="471" y="92" text-anchor="middle">"re "</text>
</g>
<text x="530" y="40" class="s">4 shared trigrams</text>
<text x="530" y="58" class="s">out of 10 distinct</text>
<text x="530" y="90" class="ta b">similarity = 0.4</text>
<text x="20" y="140" class="s">Shared trigrams in green. Works well for typos in the middle or end of a word, and for names.</text>
</svg>
:::

Trigram searches can use a **GiST index**, which makes fuzzy matching fast even on large tables:

```sql
CREATE INDEX movies_title_trigram ON movies USING gist (title gist_trgm_ops);

SELECT * FROM movies WHERE title % 'Avatre';    -- finds Avatar
```

The `%` operator here means "is similar to". The book recommends trigrams for user input with typos, since they are good at finding approximate matches.

### Step 6: Full-text search with tsvector and tsquery

What if the user searches for "night day" and expects *A Hard Day's Night*? Word order differs and one word has an apostrophe, so neither LIKE nor trigrams help. PostgreSQL's built-in **full-text search** handles this with two types:

- **`tsvector`**: a document turned into a list of normalized words (**lexemes**) with their positions.
- **`tsquery`**: a search query, with operators such as `&` (and), `|` (or) and `!` (not).

The `@@` operator asks "does this vector match this query?"

```sql
SELECT title FROM movies WHERE title @@ 'night & day';
-- A Hard Day's Night, Six Days Seven Nights, Long Day's Journey Into Night

-- the same thing written out in full:
SELECT title FROM movies
WHERE to_tsvector(title) @@ to_tsquery('english', 'night & day');
```

:::fig **How `to_tsvector` turns a title into searchable words.** The text is split into tokens, stop words ("a") are dropped, words are reduced to their stems ("Day's" to "day", "Days" would also become "day"), and each lexeme keeps its position.
<svg class="dg wide" viewBox="0 0 720 220">
<rect x="10" y="20" width="200" height="40" rx="8" class="box"/><text x="110" y="45" text-anchor="middle" class="mono">A Hard Day's Night</text>
<line x1="110" y1="62" x2="110" y2="86" class="ln" marker-end="url(#arr)"/><text x="122" y="80" class="s">1. split into tokens</text>
<g class="mono">
<rect x="10" y="90" width="34" height="30" rx="5" class="box"/><text x="27" y="110" text-anchor="middle">A</text>
<rect x="50" y="90" width="52" height="30" rx="5" class="box"/><text x="76" y="110" text-anchor="middle">Hard</text>
<rect x="108" y="90" width="52" height="30" rx="5" class="box"/><text x="134" y="110" text-anchor="middle">Day</text>
<rect x="166" y="90" width="30" height="30" rx="5" class="box"/><text x="181" y="110" text-anchor="middle">s</text>
<rect x="202" y="90" width="60" height="30" rx="5" class="box"/><text x="232" y="110" text-anchor="middle">Night</text>
</g>
<line x1="270" y1="105" x2="320" y2="105" class="ln" marker-end="url(#arr)"/>
<text x="295" y="95" text-anchor="middle" class="s">2. drop</text>
<text x="295" y="128" text-anchor="middle" class="s">stop words</text>
<g class="mono">
<rect x="326" y="90" width="34" height="30" rx="5" class="br" opacity="0.6"/><text x="343" y="110" text-anchor="middle" class="tr">a</text>
<rect x="366" y="90" width="52" height="30" rx="5" class="box"/><text x="392" y="110" text-anchor="middle">hard</text>
<rect x="424" y="90" width="52" height="30" rx="5" class="box"/><text x="450" y="110" text-anchor="middle">day</text>
<rect x="482" y="90" width="30" height="30" rx="5" class="br" opacity="0.6"/><text x="497" y="110" text-anchor="middle" class="tr">s</text>
<rect x="518" y="90" width="60" height="30" rx="5" class="box"/><text x="548" y="110" text-anchor="middle">night</text>
</g>
<line x1="450" y1="124" x2="450" y2="158" class="ln" marker-end="url(#arr)"/><text x="462" y="146" class="s">3. stem, keep positions</text>
<rect x="290" y="162" width="320" height="40" rx="8" class="ba"/><text x="450" y="187" text-anchor="middle" class="mono">'day':3  'hard':2  'night':5</text>
<text x="150" y="187" text-anchor="middle" class="s">this is a tsvector →</text>
</svg>
:::

```sql
SELECT to_tsvector('A Hard Day''s Night'), to_tsquery('english', 'night & day');
--          to_tsvector         |   to_tsquery
-- -----------------------------+-----------------
--  'day':3 'hard':2 'night':5  | 'night' & 'day'
```

Some details the book explores:

- **Stop words** are very common words (a, the, of) that carry little meaning. Searching only for them returns nothing: `title @@ to_tsquery('english', 'a')` gives a notice that the query contains only stop words.
- **Dictionaries/configurations** decide how text is processed. With `'simple'`, nothing is dropped or stemmed: `to_tsvector('simple', 'A Hard Day''s Night')` gives `'a':1 'day':3 'hard':2 'night':5 's':4`.
- `ts_lexize('english_stem', 'Day''s')` shows what one word becomes: `{day}`.
- Other languages work too: `to_tsvector('german', 'was machst du gerade?')` gives `'gerad':4 'mach':2`.

#### Indexing full-text search with GIN

Without an index, every query has to compute `to_tsvector` for every row. `EXPLAIN` proves it with a `Seq Scan` (sequential scan, meaning every row is read). The fix is a **GIN** index, a *Generalized Inverted iNdex*:

```sql
CREATE INDEX movies_title_searchable ON movies
  USING gin(to_tsvector('english', title));
```

:::fig **An inverted index.** Instead of storing "movie → words", it stores "word → movies", like the index at the back of a book. To find titles with both *night* and *day*, PostgreSQL intersects two short lists instead of reading every title.
<svg class="dg" viewBox="0 0 720 200">
<text x="120" y="22" text-anchor="middle" class="b">lexeme</text><text x="430" y="22" text-anchor="middle" class="b">movies containing it</text>
<g class="mono">
<rect x="60" y="34" width="120" height="30" rx="5" class="ba"/><text x="120" y="54" text-anchor="middle">day</text>
<rect x="60" y="74" width="120" height="30" rx="5" class="ba"/><text x="120" y="94" text-anchor="middle">night</text>
<rect x="60" y="114" width="120" height="30" rx="5" class="box"/><text x="120" y="134" text-anchor="middle">hard</text>
<rect x="60" y="154" width="120" height="30" rx="5" class="box"/><text x="120" y="174" text-anchor="middle">star</text>
</g>
<line x1="182" y1="49" x2="230" y2="49" class="ln" marker-end="url(#arr)"/>
<line x1="182" y1="89" x2="230" y2="89" class="ln" marker-end="url(#arr)"/>
<line x1="182" y1="129" x2="230" y2="129" class="ln" marker-end="url(#arr)"/>
<line x1="182" y1="169" x2="230" y2="169" class="ln" marker-end="url(#arr)"/>
<g class="s">
<text x="240" y="54"><tspan class="ta b">A Hard Day's Night</tspan>, <tspan class="ta b">Six Days Seven Nights</tspan>, Groundhog Day, …</text>
<text x="240" y="94"><tspan class="ta b">A Hard Day's Night</tspan>, <tspan class="ta b">Six Days Seven Nights</tspan>, Night Moves, …</text>
<text x="240" y="134">A Hard Day's Night, Die Hard, …</text>
<text x="240" y="174">Star Wars, Stardust, Star Trek, …</text>
</g>
</svg>
:::

:::warn The index must match the query exactly
The index above was built on `to_tsvector('english', title)`. A query written as `to_tsvector(title) @@ ...` (without `'english'`) is a *different expression*, so PostgreSQL will not use the index. Always run `EXPLAIN` to confirm your index is used:
```sql
EXPLAIN SELECT * FROM movies
WHERE to_tsvector('english',title) @@ 'night & day';
-- Bitmap Heap Scan ... Recheck Cond ... -> Bitmap Index Scan on movies_title_searchable
```
:::

### Step 7: Sounds-alike matching with metaphones

What if a user searches for **"Broos Wlis"**, spelling Bruce Willis the way it sounds? Trigrams fail (`name % 'Broos Wlis'` finds nothing) because the letters are too different. A **metaphone** algorithm converts a word into a code that represents its *sound*, so names that sound alike get the same code.

```sql
SELECT metaphone('Bruce Willis', 6), metaphone('Broos Wils', 6);
--  BRSWLS | BRSWLS        -- same sound code!

SELECT title
FROM movies NATURAL JOIN movies_actors NATURAL JOIN actors
WHERE metaphone(name, 6) = metaphone('Broos Wils', 6);
-- The Fifth Element, Twelve Monkeys, Armageddon, Die Hard, ...
```

`NATURAL JOIN` joins tables on all columns that share a name (`movie_id`, `actor_id`), so you do not have to write the `ON` clause.

| Function | What it produces for "Bruce Willis" |
|---|---|
| `soundex(name)` | `B624` (very old, coarse, English names) |
| `metaphone(name, 6)` | `BRSWLS` (better English pronunciation rules) |
| `dmetaphone(name)` | `PRSL` (Double Metaphone: handles names from many languages) |
| `dmetaphone_alt(name)` | an alternative pronunciation code |

The book's favorite trick combines techniques: use metaphones for the *sound*, trigrams for *fuzziness* on the codes, and Levenshtein to *rank* the results:

```sql
SELECT * FROM actors
WHERE metaphone(name, 8) % metaphone('Robin Williams', 8)
ORDER BY levenshtein(lower('Robin Williams'), lower(name));
-- Robin Williams first, then Robin Wright, Richard Williams, ...
```

:::tip Which fuzzy technique should I use?
| Problem | Technique |
|---|---|
| User knows the start of the word | `LIKE 'star%'` with a pattern index |
| Complex patterns | regular expressions `~*` |
| Small typos in short strings | `levenshtein()` |
| Typos anywhere, fast on big tables | trigrams `%` with a GiST or GIN index |
| Words in any order, stemming, languages | full-text search `@@` with a GIN index |
| Spelled the way it sounds | `metaphone()` / `dmetaphone()` |
:::

### Step 8: Multidimensional search with cube

Now the recommendation engine. Each movie's `genre` column is a **cube**: a point in 18-dimensional space, one dimension per genre. Star Wars is `(0,7,0,0,0,0,0,0,0,7,0,0,0,0,10,0,0,0)`: Adventure 7, Fantasy 7, SciFi 10.

Two movies with similar genre scores are **close together** in that space. So "find similar movies" becomes "find the nearest points", which is a geometry problem.

:::fig **Movies as points in genre space**, shown in two of the 18 dimensions. Similar movies cluster together. `cube_distance` measures straight-line distance between two points, and `cube_enlarge` draws a box around a point so an index can quickly fetch only the movies inside it.
<svg class="dg" viewBox="0 0 720 330">
<line x1="60" y1="290" x2="420" y2="290" class="ln" marker-end="url(#arr)"/>
<line x1="60" y1="290" x2="60" y2="20" class="ln" marker-end="url(#arr)"/>
<text x="420" y="314" text-anchor="end" class="s">SciFi score →</text>
<text x="70" y="22" class="s">Adventure score ↑</text>
<rect x="232" y="64" width="160" height="160" rx="4" class="bv" fill-opacity="0.35" stroke-dasharray="6 4"/>
<text x="236" y="58" class="s tv">cube_enlarge(…, 5, 18): a box ±5</text>
<circle cx="330" cy="140" r="8" class="fv"/><text x="330" y="164" text-anchor="middle" class="b">Star Wars</text>
<circle cx="300" cy="120" r="6" class="fa"/><text x="250" y="110" class="s">Star Wars: Ep. V</text>
<circle cx="360" cy="180" r="6" class="fa"/><text x="384" y="200" text-anchor="end" class="s">Krull</text>
<circle cx="280" cy="190" r="6" class="fa"/><text x="244" y="212" class="s">Battlestar…</text>
<circle cx="110" cy="250" r="6" class="fm"/><text x="122" y="254" class="s">romantic comedy</text>
<circle cx="140" cy="80" r="6" class="fm"/><text x="152" y="84" class="s">Indiana Jones</text>
<line x1="330" y1="140" x2="303" y2="122" class="lv"/>
<text x="460" y="70" class="b">Two steps for fast search</text>
<text x="460" y="96" class="s">1. Draw a box around the target</text>
<text x="472" y="114" class="s">(cube_enlarge) and keep only</text>
<text x="472" y="132" class="s">movies inside it (@&gt;). The GiST</text>
<text x="472" y="150" class="s">index makes this fast.</text>
<text x="460" y="180" class="s">2. Sort the survivors by real</text>
<text x="472" y="198" class="s">distance (cube_distance) and</text>
<text x="472" y="216" class="s">take the closest.</text>
<text x="460" y="250" class="s">Grey points are outside the box,</text>
<text x="460" y="268" class="s">so they are never even compared.</text>
</svg>
:::

First, a helper to read a cube. `cube_ur_coord(cube, n)` returns the n-th coordinate. Joining it with `genres` lists the genres of the Star Wars vector:

```sql
SELECT name, cube_ur_coord('(0,7,0,0,0,0,0,0,0,7,0,0,0,0,10,0,0,0)', position) AS score
FROM genres g
WHERE cube_ur_coord('(0,7,0,0,0,0,0,0,0,7,0,0,0,0,10,0,0,0)', position) > 0;
--    name    | score
-- -----------+-------
--  Adventure |     7
--  Fantasy   |     7
--  SciFi     |    10
```

**Nearest neighbors** by distance (slow: computes the distance for every movie):

```sql
SELECT *, cube_distance(genre, '(0,7,0,0,0,0,0,0,0,7,0,0,0,0,10,0,0,0)') dist
FROM movies
ORDER BY dist;
```

`cube_distance` is the ordinary straight-line (Euclidean) distance. In two dimensions, from (1,1) to (4,5) it is 5, the 3-4-5 triangle you learned at school.

**Bounding box + distance** (fast: the GiST index filters first). `cube_enlarge(cube, radius, dimensions)` grows a point into a box, and `@>` means "contains":

```sql
SELECT cube_enlarge('(1,1)', 1, 2);         -- (0, 0),(2, 2)

SELECT title, cube_distance(genre, '(0,7,0,0,0,0,0,0,0,7,0,0,0,0,10,0,0,0)') dist
FROM movies
WHERE cube_enlarge('(0,7,0,0,0,0,0,0,0,7,0,0,0,0,10,0,0,0)'::cube, 5, 18) @> genre
ORDER BY dist;
```

Finally, the real recommendation query: **"movies like Mad Max"**, using a subquery to fetch Mad Max's own vector:

```sql
SELECT m.movie_id, m.title
FROM movies m,
     (SELECT genre, title FROM movies WHERE title = 'Mad Max') s
WHERE cube_enlarge(s.genre, 5, 18) @> m.genre
  AND s.title <> m.title
ORDER BY cube_distance(m.genre, s.genre)
LIMIT 10;
```

:::analogy Recommendations as geometry
Imagine every movie as a pin on a map, where "east" means more sci-fi and "north" means more adventure (and 16 more directions you cannot draw). Recommending films like the one you just watched means looking for the pins nearest to it. The box from `cube_enlarge` is like saying "only look within 5 km" before measuring exact distances.
:::

:::modern Text and similarity search today
- Everything in Day 3 still works in current PostgreSQL.
- Full-text search gained `websearch_to_tsquery()` (PostgreSQL 11), which accepts Google-style input like `"hard day" -night`, and `ts_rank` for ordering results by relevance.
- Trigram indexes now speed up `LIKE` and regular-expression searches too, not just `%`.
- The cube idea, finding nearest neighbors in many dimensions, is the same idea behind modern AI **vector search**. The **pgvector** extension stores embeddings with hundreds or thousands of dimensions and finds the closest ones with special indexes (HNSW, IVFFlat). Day 3's movie recommender is a small ancestor of today's semantic search.
:::

### Day 3 homework, solved

**1. A function that suggests five movies**, given either a movie title or an actor's name. If the input is a movie, return the nearest movies by genre. If it is an actor, return movies that actor appeared in.

```sql
CREATE OR REPLACE FUNCTION suggest(input text)
RETURNS TABLE (suggestion text) AS $$
BEGIN
  -- Is it a movie title?
  IF EXISTS (SELECT 1 FROM movies WHERE title ILIKE input) THEN
    RETURN QUERY
      SELECT m.title
      FROM movies m, (SELECT genre, title FROM movies WHERE title ILIKE input LIMIT 1) s
      WHERE cube_enlarge(s.genre, 5, 18) @> m.genre AND m.title <> s.title
      ORDER BY cube_distance(m.genre, s.genre)
      LIMIT 5;
  ELSE
    -- Otherwise treat it as an actor name (sounds-alike, ranked by spelling)
    RETURN QUERY
      SELECT m.title
      FROM movies m NATURAL JOIN movies_actors NATURAL JOIN actors a
      WHERE metaphone(a.name, 8) % metaphone(input, 8)
      ORDER BY levenshtein(lower(a.name), lower(input)), m.title
      LIMIT 5;
  END IF;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM suggest('Mad Max');
SELECT * FROM suggest('Bruce Willis');
```

`RETURNS TABLE (...)` plus `RETURN QUERY` lets a function return a whole result set that you can use like a table.

**2. Track user comments and find the most talked-about actors.** Store comments, turn each comment into lexemes (stop words are removed automatically), and match them against actors' last names:

```sql
CREATE TABLE comments (
  comment_id SERIAL PRIMARY KEY,
  movie_id integer REFERENCES movies,
  body text
);

INSERT INTO comments (movie_id, body) VALUES
  (1, 'Willis was great, and the ending surprised me'),
  (1, 'Willis again! Best action hero ever');

-- count how many comments mention each actor's last name
SELECT a.name, count(*) AS mentions
FROM actors a
JOIN comments c
  ON to_tsvector('english', c.body)
     @@ plainto_tsquery('english', split_part(a.name, ' ', -1))   -- last word of the name
GROUP BY a.name
ORDER BY mentions DESC
LIMIT 10;
```

`split_part(name, ' ', -1)` takes the last word of the name (negative positions need PostgreSQL 14 or newer; on older versions use `regexp_replace(name, '.* ', '')`). `plainto_tsquery` turns plain text into a query without needing `&` operators. To see the extracted keywords themselves, use `SELECT word, nentry FROM ts_stat('SELECT to_tsvector(''english'', body) FROM comments') ORDER BY nentry DESC;`.

## Wrap-up · Strengths and weaknesses

The authors' first advice: if you have not spent much time with relational databases, learn one well before throwing it away for something newer. Relational databases have had more than forty years of research and industrial improvement, and PostgreSQL is one of the best open-source results.

### Strengths

- **Decades of research and production use**, very consistent and durable data, and mature drivers for almost every programming language. Many frameworks, such as object-relational mappers (ORMs), assume a relational database underneath.
- **The flexibility of the join.** You do not need to know how you will query your model. With joins, filters, views and indexes, you can almost always get the data you want.
- **"Stepford data".** The authors' name for data that is uniform and fits a structured schema well (after *The Stepford Wives*, where everyone in the neighborhood is identical). Customers, orders, invoices and inventory are classic examples.
- **Beyond normal RDBMS features**: powerful constraints, custom languages, custom indexes, custom data types, even control over how queries are parsed.
- **Truly open source.** No company owns it. Anyone can use it for almost anything, and development is community-driven.

### Weaknesses

- **Partitioning is not its strength.** If you need to scale **out** (many parallel machines) rather than **up** (one powerful machine), the 2012 PostgreSQL was a poor fit.
- If your data is too **variable** to fit a rigid schema, if you need very high-volume simple key-value reads and writes, or if you only store large blobs, another datastore may suit you better.

### Parting thoughts

A relational database is an excellent choice when you want **query flexibility**. You design the data up front, but PostgreSQL makes no assumptions about how you will use it. Keep the schema normalized (no duplicated or computable values), add the right extensions, tune and index well, and it will perform well even with terabytes of data. And when data safety is paramount, ACID transactions make every commit atomic, consistent, isolated and durable.

:::modern PostgreSQL in 2026
PostgreSQL's reputation has only grown since 2012. It is consistently ranked among the most-used and most-loved databases in developer surveys. Its weakness in scaling out has been softened by built-in declarative partitioning (version 10 and later), logical replication, and extensions or derivatives such as Citus, which shards PostgreSQL across many machines. Cloud services (Amazon RDS and Aurora, Google Cloud SQL and AlloyDB, Azure, Neon, Supabase) make it easy to run. With `jsonb` for documents, full-text search and pgvector for embeddings, it now covers many jobs that once required a separate NoSQL database.
:::

:::key Chapter 2 in a nutshell
- **Day 1:** tables with typed columns and constraints (PRIMARY KEY, UNIQUE, NOT NULL, CHECK, FOREIGN KEY); CRUD; INNER, LEFT, RIGHT and FULL joins; B-tree and hash indexes.
- **Day 2:** aggregates, GROUP BY and HAVING; window functions that keep every row; ACID transactions; PL/pgSQL functions; triggers; views; rules and the query rewriter; crosstab pivots.
- **Day 3:** fuzzy search with LIKE, regex, Levenshtein, trigrams and metaphones; full-text search with tsvector, tsquery and GIN indexes; multidimensional nearest-neighbor search with cube and GiST indexes.
- **Choose it when** your data is regular and you want flexible queries with strong guarantees. **Look elsewhere** (in 2012, at least) when you must scale out across many machines or your data has no stable shape.
:::

@@quiz
Q: Why is PostgreSQL called "relational"?
- Because tables relate to each other through foreign keys
+ Because it is built on mathematical relations: tables are sets of tuples manipulated with relational algebra
- Because it can store relationships between people
- Because every table must have a relationship to another table
? The book stresses this point: "relational" comes from set theory, where a relation is a set of tuples. Foreign keys are optional and have nothing to do with the name.

Q: What happens when you run this, given that 'ca' is not in the countries table?
C: INSERT INTO cities VALUES ('Toronto','M4C1B5','ca');
- The city is inserted and 'ca' is added to countries automatically
- The city is inserted with a NULL country_code
+ PostgreSQL rejects the insert with a foreign key violation
- PostgreSQL inserts the row but prints a warning
? `country_code` REFERENCES countries, so the value must already exist there. This guarantee is called referential integrity.

Q: Events with no venue have `venue_id = NULL`. Which join returns every event, including those without a venue?
- `INNER JOIN venues`
+ `LEFT JOIN venues` (with events on the left)
- `RIGHT JOIN venues` (with events on the left)
- `NATURAL JOIN venues`
? An inner join drops rows with no match. A LEFT JOIN keeps every row from the left table and fills in NULLs where no venue matches.

Q: Which index type should you choose for a query like `WHERE starts >= '2012-04-01'`?
- A hash index, because it is the fastest
+ A B-tree index, because it keeps values sorted and can answer range queries
- No index can help with range queries
- A GIN index, because it is inverted
? Hash indexes only answer exact equality. B-trees store values in sorted order, so they handle =, <, >, ranges and ORDER BY. That is why B-tree is the default.

Q: What is the difference between WHERE and HAVING?
- They are identical; HAVING is just older syntax
+ WHERE filters rows before grouping; HAVING filters groups after aggregation, so it can use functions like `count(*)`
- WHERE only works with numbers; HAVING works with text
- HAVING filters rows before grouping; WHERE filters groups afterwards
? SQL evaluates FROM, then WHERE, then GROUP BY, then HAVING. At the WHERE stage no groups exist yet, so `count(*)` is only available in HAVING.

Q: What does a window function such as `count(*) OVER (PARTITION BY venue_id)` do that GROUP BY cannot?
- It runs faster than GROUP BY on every query
+ It computes the aggregate per group but keeps every individual row in the result
- It removes NULL values automatically
- It sorts the table permanently
? GROUP BY collapses each group into one row, so you lose columns like `title`. A window function writes the group's count next to every row instead.

Q: A transaction moves money between two accounts, and the server crashes after the first UPDATE. What does PostgreSQL do on restart?
- Keeps the first update and runs the second one automatically
+ Rolls back the first update, so both accounts are as they were before the transaction
- Asks the administrator which update to keep
- Deletes both accounts to stay consistent
? Atomicity means all or nothing. An uncommitted transaction is rolled back during recovery, so money is never created or destroyed by a half-finished transfer.

Q: Which statement about views and rules is correct, according to the book?
- A view stores a copy of its data that must be refreshed
+ A view is implemented as a rule that the rewriter applies to the query tree before planning
- Rules run after the query has been executed
- Views can never be updated, even with rules
? Views are rules: EXPLAIN shows that querying a view produces the same plan as running its underlying query. A DO INSTEAD rule can make a view updatable (and modern PostgreSQL makes simple views updatable automatically).

Q: Which technique finds "Bruce Willis" when the user types "Broos Wils"?
- `LIKE 'Broos%'`
- A B-tree index on actors.name
+ Comparing `metaphone()` codes, which represent how names sound
- `to_tsvector('english', name)`
? Metaphone turns both spellings into the same sound code (BRSWLS). Trigrams and LIKE fail because the letters are too different.

Q: Why must the full-text query use `to_tsvector('english', title)` exactly when the index was created on that expression?
- Because PostgreSQL only supports English
+ Because an expression index is only used when the query contains the same expression; `to_tsvector(title)` is a different expression
- Because GIN indexes require a language name in every query
- It does not matter; PostgreSQL rewrites the query to match
? The planner matches expressions literally. A query with a different expression falls back to a sequential scan, which EXPLAIN would reveal.

Q: In the movie recommender, why use `cube_enlarge(...) @> genre` before ordering by `cube_distance`?
- `cube_distance` does not work without it
+ The bounding-box test can use the GiST index to discard far-away movies quickly, so the exact distance is only computed for nearby candidates
- It converts the 18-dimension cube into 2 dimensions
- It sorts the movies alphabetically
? Computing distance to every movie means a full scan. The enlarged box is an indexable filter, so only movies inside it are compared and sorted.

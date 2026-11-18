title: HBase
lead: A column-oriented database for very big data, built on Hadoop and modeled on Google's BigTable. Tables and versions on Day 1; importing Wikipedia, regions and the write path on Day 2; Thrift and a cloud cluster on Day 3.

## Overview: introducing HBase

The authors compare HBase to a **nail gun**: a big, powerful tool that does one kind of job extremely well, and that you should not pick up to hang a single picture. HBase is for **big data**: billions of rows, terabytes or petabytes, on clusters of dozens to thousands of ordinary machines.

Key facts to keep in mind:

- It is a **column-oriented** (more precisely, *column-family*) database, closely modeled on Google's **BigTable** paper (2006).
- It runs on top of **Hadoop**: its files live in the **Hadoop Distributed File System (HDFS)**, it coordinates through **ZooKeeper**, and Hadoop's MapReduce can process its tables.
- It gives **strong consistency**: once a write succeeds, every reader sees it.
- It has built-in **versioning** (every cell keeps a history), **compression**, and **Bloom filters**.
- It **does not scale down**. The community considered five nodes the sensible minimum for production.

:::fig **HBase is part of an ecosystem.** It stores its data files in HDFS, uses ZooKeeper to coordinate servers and find each other, and can be processed in bulk by Hadoop MapReduce. Clients reach it through the Java API, the shell, Thrift or REST.
<svg class="dg" viewBox="0 0 720 260">
<rect x="20" y="16" width="680" height="46" rx="8" class="box"/>
<text x="360" y="44" text-anchor="middle" class="b">clients: HBase shell (JRuby) · Java API · Thrift · REST</text>
<line x1="360" y1="62" x2="360" y2="84" class="ln" marker-end="url(#arr)"/>
<rect x="120" y="88" width="480" height="60" rx="10" class="bv"/>
<text x="360" y="114" text-anchor="middle" class="lg">HBase</text>
<text x="360" y="134" text-anchor="middle" class="s">tables, rows, column families, versions · master + region servers</text>
<rect x="620" y="88" width="80" height="140" rx="10" class="bw"/>
<text x="660" y="150" text-anchor="middle" class="b">Zoo-</text><text x="660" y="168" text-anchor="middle" class="b">Keeper</text>
<text x="660" y="190" text-anchor="middle" class="s">coordination</text>
<rect x="20" y="88" width="80" height="140" rx="10" class="bg"/>
<text x="60" y="150" text-anchor="middle" class="b">Map-</text><text x="60" y="168" text-anchor="middle" class="b">Reduce</text>
<text x="60" y="190" text-anchor="middle" class="s">batch jobs</text>
<line x1="360" y1="148" x2="360" y2="170" class="ln" marker-end="url(#arr)"/>
<rect x="120" y="174" width="480" height="54" rx="10" class="ba"/>
<text x="360" y="198" text-anchor="middle" class="lg">HDFS</text>
<text x="360" y="216" text-anchor="middle" class="s">Hadoop Distributed File System: files replicated across machines</text>
<line x1="600" y1="118" x2="618" y2="118" class="ln2"/><line x1="100" y1="118" x2="118" y2="118" class="ln2"/>
<text x="360" y="252" text-anchor="middle" class="s">all running on clusters of commodity hardware</text>
</svg>
:::

:::warn Familiar words, different meanings
HBase uses the words **table**, **row** and **column**, which makes SQL users feel at home. Don't trust that feeling. An HBase "table" has no fixed columns, no types, no joins and no secondary indexes. The authors encourage you to shed the relational meanings of these words as you go; the differences become clearer each day.
:::

## Day 1 · CRUD and table administration

### Step 1: Running HBase in standalone mode

For learning, HBase runs on one machine in **standalone mode**, storing files on the local disk instead of HDFS. The only required setting is where to keep data, in `conf/hbase-site.xml`:

```xml
<configuration>
  <property>
    <name>hbase.rootdir</name>
    <value>file:///path/to/hbase</value>
  </property>
</configuration>
```

```bash
bin/start-hbase.sh      # start the server
bin/hbase shell         # open the interactive shell (it is JRuby: Ruby on the JVM)
```

```text
hbase> version
0.90.3, r1100350, Sat May  7 13:31:12 PDT 2011
hbase> status
1 servers, 0 dead, 2.0000 average load
```

If something goes wrong, the log files in `logs/` are the first place to look. The book also lists networking properties (`hbase.master.dns.interface`, `hbase.regionserver.info.bindAddress` and so on) to set to `127.0.0.1`/`lo` if your machine's network setup confuses HBase.

### Step 2: The data model

This is the most important idea in the chapter. An HBase table is best pictured as a **sorted, multidimensional map**:

> table → **row key** → **column family** → **column qualifier** → **timestamp** → value

:::fig **An HBase table is a map of maps.** Each row key holds column families (fixed when the table is created). Each family holds any number of column qualifiers (decided per row, at write time). Each cell keeps several timestamped versions. Every key and value is just an array of bytes.
<svg class="dg wide" viewBox="0 0 720 270">
<rect x="10" y="100" width="110" height="60" rx="8" class="bv"/>
<text x="65" y="124" text-anchor="middle" class="b">row key</text><text x="65" y="144" text-anchor="middle" class="mono s">"Home"</text>
<line x1="122" y1="130" x2="160" y2="70" class="ln" marker-end="url(#arr)"/>
<line x1="122" y1="130" x2="160" y2="190" class="ln" marker-end="url(#arr)"/>
<rect x="164" y="40" width="130" height="56" rx="8" class="ba"/>
<text x="229" y="63" text-anchor="middle" class="b">family</text><text x="229" y="82" text-anchor="middle" class="mono s">text</text>
<rect x="164" y="164" width="130" height="56" rx="8" class="ba"/>
<text x="229" y="187" text-anchor="middle" class="b">family</text><text x="229" y="206" text-anchor="middle" class="mono s">revision</text>
<line x1="296" y1="68" x2="334" y2="68" class="ln" marker-end="url(#arr)"/>
<line x1="296" y1="192" x2="334" y2="160" class="ln" marker-end="url(#arr)"/>
<line x1="296" y1="192" x2="334" y2="224" class="ln" marker-end="url(#arr)"/>
<rect x="338" y="44" width="120" height="48" rx="8" class="box"/>
<text x="398" y="64" text-anchor="middle" class="b">qualifier</text><text x="398" y="82" text-anchor="middle" class="mono s">"" (empty)</text>
<rect x="338" y="136" width="120" height="48" rx="8" class="box"/>
<text x="398" y="156" text-anchor="middle" class="b">qualifier</text><text x="398" y="174" text-anchor="middle" class="mono s">author</text>
<rect x="338" y="200" width="120" height="48" rx="8" class="box"/>
<text x="398" y="220" text-anchor="middle" class="b">qualifier</text><text x="398" y="238" text-anchor="middle" class="mono s">comment</text>
<line x1="460" y1="68" x2="498" y2="68" class="ln" marker-end="url(#arr)"/>
<line x1="460" y1="160" x2="498" y2="160" class="ln" marker-end="url(#arr)"/>
<line x1="460" y1="224" x2="498" y2="224" class="ln" marker-end="url(#arr)"/>
<rect x="502" y="22" width="208" height="30" rx="5" class="bg"/><text x="512" y="42" class="mono s">t3 → "…to the wiki!!"</text>
<rect x="502" y="56" width="208" height="30" rx="5" class="box"/><text x="512" y="76" class="mono s">t2 → "…to the wiki!"</text>
<rect x="502" y="90" width="208" height="30" rx="5" class="box"/><text x="512" y="110" class="mono s">t1 → "Welcome"</text>
<rect x="502" y="145" width="208" height="30" rx="5" class="bg"/><text x="512" y="165" class="mono s">t3 → "jimbo"</text>
<rect x="502" y="209" width="208" height="30" rx="5" class="bg"/><text x="512" y="229" class="mono s">t3 → "fixed typo"</text>
<text x="606" y="262" text-anchor="middle" class="s">timestamp → value (newest first)</text>
<text x="65" y="186" text-anchor="middle" class="s">rows sorted</text><text x="65" y="202" text-anchor="middle" class="s">by key</text>
</svg>
:::

| HBase term | What it is | Decided when |
|---|---|---|
| **Table** | A named collection of rows. | Created by an administrator. |
| **Row key** | Unique identifier of a row. Rows are **stored sorted by key**. | Every write. |
| **Column family** | A group of columns stored together on disk, with its own settings (versions, compression, Bloom filter, in-memory). | Table creation (changing it needs `alter`). |
| **Column qualifier** | The name of a column inside a family. Any number, different for every row. | Every write. |
| **Column** | `family:qualifier`, for example `revision:author`. | Every write. |
| **Cell** | The value at (row, column). | Every write. |
| **Timestamp / version** | Each cell keeps several values, labeled by timestamp. | Every write (defaults to "now"). |

:::analogy A row as a nested dictionary
In JSON, the "Home" row of the wiki table looks like this:
```json
{ "Home": {
    "text":     { "":        { "t3": "Welcome to the wiki!!", "t2": "Welcome to the wiki!" } },
    "revision": { "author":  { "t3": "jimbo" },
                  "comment": { "t3": "fixed typo" } } } }
```
Every level is sorted. Missing columns simply do not appear, so sparse data costs nothing.
:::

### Step 3: Creating a table and doing CRUD

The book models a **wiki**: every page is a row, keyed by its title, and the page text goes in a column family named `text`:

```text
hbase> create 'wiki', 'text'
0 row(s) in 1.2160 seconds
```

When creating a table you name **only the column families**. Columns inside them are invented when you write.

```text
hbase> put 'wiki', 'Home', 'text:', 'Welcome to the wiki!'

hbase> get 'wiki', 'Home', 'text:'
COLUMN          CELL
 text:          timestamp=1295774833226, value=Welcome to the wiki!
1 row(s) in 0.0430 seconds
```

`put` takes table, row key, column and value. The column `text:` is family `text` with an **empty qualifier**, which is fine. The `timestamp` is milliseconds since 1 January 1970 (the Unix epoch).

| Operation | Shell command |
|---|---|
| Create table | `create 'wiki', 'text'` |
| Write a cell | `put 'wiki', 'Home', 'text:', 'Welcome…'` |
| Read a row or cell | `get 'wiki', 'Home'` / `get 'wiki', 'Home', 'text:'` |
| Read many rows in key order | `scan 'wiki'` |
| Delete one cell | `delete 'wiki', 'Home', 'revision:author'` |
| Delete a whole row | `deleteall 'wiki', 'Home'` |
| Count rows | `count 'wiki'` |
| Table structure | `describe 'wiki'` |

### Step 4: Versions and altering a table

Write to the same cell again and HBase does **not** overwrite: it adds a new **version** with a newer timestamp. A `get` returns the newest unless you ask for more. In 0.90 each family kept **3 versions** by default.

For a wiki, page history is exactly what we want, so the book raises the limit and adds a second family, `revision`, for each edit's author and comment. Changing a table's families requires taking it **offline** first:

```text
hbase> disable 'wiki'

hbase> alter 'wiki', { NAME => 'text', VERSIONS =>
hbase*   org.apache.hadoop.hbase.HConstants::ALL_VERSIONS }

hbase> alter 'wiki', { NAME => 'revision', VERSIONS =>
hbase*   org.apache.hadoop.hbase.HConstants::ALL_VERSIONS }

hbase> enable 'wiki'
```

`ALL_VERSIONS` is a Java constant (the largest integer), reached from JRuby by its full Java path. Reading old versions:

```text
hbase> get 'wiki', 'Home', { COLUMN => 'text:', VERSIONS => 3 }
hbase> get 'wiki', 'Home', { COLUMN => 'text:', TIMESTAMP => 1295774833226 }
```

:::fig **Versioning gives you history for free.** Each put to the same cell adds a new timestamped version on top. A normal get returns the newest; you can ask for several versions or for the value at a given timestamp. Old versions beyond the family's VERSIONS limit are removed during compaction.
<svg class="dg" viewBox="0 0 720 200">
<text x="20" y="30" class="b">cell wiki / Home / text:</text>
<rect x="20" y="44" width="300" height="34" rx="6" class="bg"/><text x="34" y="66" class="mono s">ts 1295774955442</text><text x="306" y="66" text-anchor="end" class="mono s">"…wiki!!"</text>
<rect x="30" y="84" width="300" height="34" rx="6" class="box"/><text x="44" y="106" class="mono s">ts 1295774833226</text><text x="316" y="106" text-anchor="end" class="mono s">"…wiki!"</text>
<rect x="40" y="124" width="300" height="34" rx="6" class="box"/><text x="54" y="146" class="mono s">ts 1295774700001</text><text x="326" y="146" text-anchor="end" class="mono s">"Welcome"</text>
<text x="190" y="182" text-anchor="middle" class="s">older versions underneath</text>
<line x1="330" y1="60" x2="420" y2="60" class="lgr" marker-end="url(#arrg)"/>
<text x="430" y="56" class="mono s">get … 'text:'</text><text x="430" y="72" class="s">returns the newest</text>
<line x1="350" y1="120" x2="420" y2="120" class="ln" marker-end="url(#arr)"/>
<text x="430" y="116" class="mono s">get … VERSIONS =&gt; 3</text><text x="430" y="132" class="s">returns all three</text>
</svg>
:::

### Step 5: Scripting HBase with JRuby and the Java API

The HBase shell is a full JRuby interpreter, so you can call HBase's **Java API** directly. The book uses this to write a page's text and its revision info **in one atomic operation**. Key classes:

| Java class | Role |
|---|---|
| `HTable` | A connection to one table. |
| `Put` | A bundle of cell writes **for one row**, applied atomically. |
| `Get` / `Scan` | Read one row / iterate over a range of rows. |
| `Bytes` | Converts strings and numbers to and from byte arrays. |

```ruby
import 'org.apache.hadoop.hbase.client.HTable'
import 'org.apache.hadoop.hbase.client.Put'

def jbytes( *args )
  args.map { |arg| arg.to_s.to_java_bytes }    # Ruby strings → Java byte[]
end

table = HTable.new( @hbase.configuration, "wiki" )

p = Put.new( *jbytes( "Home" ) )                       # row key
p.add( *jbytes( "text", "", "Hello world" ) )          # family, qualifier, value
p.add( *jbytes( "revision", "author", "jimbo" ) )
p.add( *jbytes( "revision", "comment", "my first edit" ) )

table.put( p )
```

Run it with `bin/hbase shell put_multiple_columns.rb`. Then `get 'wiki', 'Home'` shows all three cells with the **same timestamp**, because one `Put` is applied atomically.

:::deep Atomic per row, and only per row
HBase guarantees that all changes in a single `Put` to **one row** happen together or not at all. There are no transactions spanning several rows or tables (in the book's version). That is one reason HBase schema design puts related data in the **same row**: the row is the unit of consistency.
:::

### Day 1 homework, solved

**Find:** delete one cell with `delete 'wiki', 'Home', 'revision:comment'`; delete a whole row with `deleteall 'wiki', 'Home'`.

**Do:** write `put_many(table_name, row, column_values)` that builds one `Put` from a hash of columns:

```ruby
def put_many( table_name, row, column_values )
  table = HTable.new( @hbase.configuration, table_name )
  p = Put.new( *jbytes( row ) )
  column_values.each do |column, value|
    family, qualifier = column.split(':')
    p.add( *jbytes( family, qualifier || "", value ) )
  end
  table.put( p )
end
```

```text
hbase> put_many 'wiki', 'Some title', {
hbase*   "text:" => "Some article text",
hbase*   "revision:author" => "jschmoe",
hbase*   "revision:comment" => "no comment" }
hbase> get 'wiki', 'Some title'
```

## Day 2 · Working with big data

Day 2 fills the wiki table with **real Wikipedia data** (millions of pages), then uses that data to explore how HBase stores, splits and finds rows.

### Step 1: Streaming a huge XML file into HBase

Wikipedia publishes its articles as one enormous XML file. You cannot load it into memory, so the book uses a **streaming (StAX) XML parser**: it reads the file event by event (start tag, text, end tag) and writes each finished page to HBase as it goes.

```ruby
import 'javax.xml.stream.XMLStreamConstants'
factory = javax.xml.stream.XMLInputFactory.newInstance
reader  = factory.createXMLStreamReader(java.lang.System.in)

while reader.has_next
  type = reader.next
  if type == XMLStreamConstants::START_ELEMENT
    tag = reader.local_name                       # e.g. "title", "text", "username"
  elsif type == XMLStreamConstants::CHARACTERS
    text << reader.text                           # collect text inside the tag
  elsif type == XMLStreamConstants::END_ELEMENT
    # when </page> ends: build a Put for this page and send it
  end
end
```

For each page the script builds one `Put`, keyed by the page **title**, with the article in `text:` and the editor's name and comment in `revision:author` and `revision:comment`, all stamped with the revision's real timestamp. The dump is piped straight from the internet, through `bzcat` (decompression), into the script:

```bash
curl <dump_url> | bzcat | \
  bin/hbase shell import_from_wikipedia.rb
```

#### Speed versus safety while importing

| Call | Effect |
|---|---|
| `table.setAutoFlush(false)` | Buffer puts on the client and send them in batches instead of one network call per put. |
| `table.flushCommits()` | Send the buffered batch now (call it every N pages and at the end). |
| `put.setWriteToWAL(false)` | Skip the write-ahead log. Much faster, but data in memory is lost if a server crashes before flushing. |

The import runs for hours. While it runs, `du -h` on the data directory shows the files growing.

### Step 2: Compression and Bloom filters

Wikipedia text is highly compressible, so the book enables **GZ compression** on the text family and a **Bloom filter**:

```text
hbase> alter 'wiki', {NAME=>'text', COMPRESSION=>'GZ', BLOOMFILTER=>'ROW'}
```

Compression is a per-family setting, which is one reason to put data with different characteristics in different families.

A **Bloom filter** is a tiny, clever data structure that answers the question "**is this row key possibly in this file?**" with either **"definitely not"** or **"maybe"**. HBase keeps one per data file, so a read can skip every file that definitely does not contain the row, instead of opening each one.

:::fig **How a Bloom filter works.** Adding a key sets the bits chosen by a few hash functions. To check a key, look at its bits: if any is 0, the key was **definitely never added**; if all are 1, it **might** be there (other keys may have set those bits). No false negatives, a few false positives, very little memory.
<svg class="dg wide" viewBox="0 0 720 230">
<text x="20" y="26" class="b">bit array (one per data file)</text>
<g class="mono s">
<rect x="20" y="40" width="40" height="36" class="box"/><text x="40" y="63" text-anchor="middle">0</text>
<rect x="60" y="40" width="40" height="36" class="bv"/><text x="80" y="63" text-anchor="middle" class="b">1</text>
<rect x="100" y="40" width="40" height="36" class="box"/><text x="120" y="63" text-anchor="middle">0</text>
<rect x="140" y="40" width="40" height="36" class="bv"/><text x="160" y="63" text-anchor="middle" class="b">1</text>
<rect x="180" y="40" width="40" height="36" class="box"/><text x="200" y="63" text-anchor="middle">0</text>
<rect x="220" y="40" width="40" height="36" class="box"/><text x="240" y="63" text-anchor="middle">0</text>
<rect x="260" y="40" width="40" height="36" class="bv"/><text x="280" y="63" text-anchor="middle" class="b">1</text>
<rect x="300" y="40" width="40" height="36" class="bv"/><text x="320" y="63" text-anchor="middle" class="b">1</text>
<rect x="340" y="40" width="40" height="36" class="box"/><text x="360" y="63" text-anchor="middle">0</text>
<rect x="380" y="40" width="40" height="36" class="bv"/><text x="400" y="63" text-anchor="middle" class="b">1</text>
</g>
<text x="20" y="116" class="b">add "Home"</text><text x="20" y="134" class="s">hashes → 1, 3, 7</text>
<line x1="110" y1="108" x2="80" y2="80" class="lv" marker-end="url(#arrv)"/><line x1="120" y1="108" x2="160" y2="80" class="lv" marker-end="url(#arrv)"/><line x1="130" y1="108" x2="320" y2="80" class="lv" marker-end="url(#arrv)"/>
<text x="460" y="56" class="b">check "Zebra"</text><text x="460" y="74" class="s">hashes → 2, 6, 9</text>
<text x="460" y="96" class="s">bit 2 is 0 →</text><text x="460" y="114" class="tr b">definitely not here</text>
<text x="460" y="134" class="s">skip this file entirely</text>
<text x="460" y="170" class="b">check "Home"</text><text x="460" y="188" class="s">bits 1, 3, 7 all 1 →</text>
<text x="460" y="206" class="tg b">maybe here: read the file</text>
<text x="20" y="190" class="s">BLOOMFILTER =&gt; 'ROW' hashes the row key;</text>
<text x="20" y="208" class="s">'ROWCOL' hashes row key + column.</text>
</svg>
:::

### Step 3: How HBase writes: WAL, MemStore and store files

To understand both durability and speed, follow a write through a **region server** (the process that stores part of a table):

:::fig **The HBase write path.** A put is first appended to the write-ahead log (WAL) for safety, then placed in the in-memory MemStore, sorted. When the MemStore fills up, it is flushed to an immutable, sorted file (an HFile) in HDFS. Background compactions merge small files into bigger ones and drop expired versions.
<svg class="dg wide" viewBox="0 0 720 260">
<rect x="10" y="100" width="90" height="56" rx="8" class="box"/><text x="55" y="124" text-anchor="middle" class="b">client</text><text x="55" y="142" text-anchor="middle" class="mono s">put</text>
<line x1="100" y1="128" x2="140" y2="128" class="ln" marker-end="url(#arr)"/>
<rect x="144" y="16" width="420" height="160" rx="12" class="soft"/>
<text x="354" y="38" text-anchor="middle" class="b">region server</text>
<rect x="164" y="56" width="150" height="50" rx="8" class="bw"/><text x="239" y="78" text-anchor="middle" class="b">1. WAL</text><text x="239" y="96" text-anchor="middle" class="s">append to log</text>
<rect x="164" y="118" width="150" height="50" rx="8" class="bv"/><text x="239" y="140" text-anchor="middle" class="b">2. MemStore</text><text x="239" y="158" text-anchor="middle" class="s">sorted, in memory</text>
<line x1="239" y1="106" x2="239" y2="116" class="ln" marker-end="url(#arr)"/>
<line x1="316" y1="143" x2="380" y2="143" class="ln" marker-end="url(#arr)"/>
<text x="348" y="134" text-anchor="middle" class="s">3. flush</text><text x="348" y="162" text-anchor="middle" class="s">when full</text>
<rect x="384" y="56" width="164" height="112" rx="8" class="box"/><text x="466" y="78" text-anchor="middle" class="b">HFiles</text>
<rect x="400" y="88" width="132" height="18" rx="3" class="ba"/><rect x="400" y="110" width="132" height="18" rx="3" class="ba"/><rect x="400" y="132" width="132" height="18" rx="3" class="ba"/>
<text x="466" y="162" text-anchor="middle" class="s">immutable, sorted</text>
<path d="M164,81 L154,81 L154,202" class="lw dash" marker-end="url(#arrw)"/>
<line x1="466" y1="168" x2="466" y2="200" class="ln dash"/>
<rect x="144" y="204" width="420" height="44" rx="10" class="ba"/><text x="354" y="231" text-anchor="middle" class="b">HDFS: every file replicated on several machines</text>
<rect x="584" y="56" width="126" height="112" rx="8" class="bg"/><text x="647" y="82" text-anchor="middle" class="b">4. compaction</text>
<text x="647" y="104" text-anchor="middle" class="s">merge small</text><text x="647" y="120" text-anchor="middle" class="s">files, drop old</text><text x="647" y="136" text-anchor="middle" class="s">versions and</text><text x="647" y="152" text-anchor="middle" class="s">deletes</text>
<line x1="550" y1="112" x2="582" y2="112" class="ln" marker-end="url(#arr)"/>
</svg>
:::

The **write-ahead log (WAL)** is the key to disaster recovery. If a region server crashes, whatever was only in its MemStore is lost from memory, but it is still in the WAL on HDFS. Another server replays the log and rebuilds the missing data. That is why `setWriteToWAL(false)` is fast but dangerous.

:::deep Why "write to memory, flush to sorted files" is fast
Disks (especially spinning ones) are slow at random writes and fast at long sequential writes. HBase only ever **appends**: to the log, and by writing whole sorted files at once. It never updates a file in place. Reads then merge the MemStore with the files, newest first. This design is called a **log-structured merge tree (LSM tree)**, and it is shared by Cassandra, LevelDB, RocksDB and many others.
:::

### Step 4: Regions and region servers

A table with millions of rows cannot live on one server. HBase splits each table into **regions**: contiguous ranges of **row keys** (remember, rows are sorted). As a region grows past a size limit it splits in two. Each region is served by exactly one **region server**, and a **master** server assigns regions and moves them to balance load.

:::fig **Regions split a sorted table by row-key range.** Each region holds a start key (inclusive) and an end key (exclusive) and lives on one region server. Because keys are sorted, a scan from "Admiral Ackbar" to "It's a Trap!" touches only the regions covering that range.
<svg class="dg wide" viewBox="0 0 720 280">
<text x="20" y="24" class="b">wiki table, rows sorted by title</text>
<rect x="20" y="36" width="220" height="56" rx="8" class="bv"/><text x="130" y="58" text-anchor="middle" class="b">region 1</text><text x="130" y="78" text-anchor="middle" class="mono s">'' → 'Demographics of M…'</text>
<rect x="250" y="36" width="220" height="56" rx="8" class="bv"/><text x="360" y="58" text-anchor="middle" class="b">region 2</text><text x="360" y="78" text-anchor="middle" class="mono s">'Demographics…' → 'June 30'</text>
<rect x="480" y="36" width="220" height="56" rx="8" class="bv"/><text x="590" y="58" text-anchor="middle" class="b">region 3</text><text x="590" y="78" text-anchor="middle" class="mono s">'June 30' → ''</text>
<rect x="20" y="160" width="200" height="80" rx="10" class="box"/><text x="120" y="188" text-anchor="middle" class="b">region server A</text><text x="120" y="210" text-anchor="middle" class="s">regions 1, 3</text>
<rect x="260" y="160" width="200" height="80" rx="10" class="box"/><text x="360" y="188" text-anchor="middle" class="b">region server B</text><text x="360" y="210" text-anchor="middle" class="s">region 2</text>
<rect x="500" y="160" width="200" height="80" rx="10" class="bw"/><text x="600" y="188" text-anchor="middle" class="b">master</text><text x="600" y="210" text-anchor="middle" class="s">assigns and balances</text>
<line x1="130" y1="94" x2="120" y2="156" class="ln" marker-end="url(#arr)"/>
<line x1="590" y1="94" x2="160" y2="156" class="ln dash" marker-end="url(#arr)"/>
<line x1="360" y1="94" x2="360" y2="156" class="ln" marker-end="url(#arr)"/>
<text x="20" y="270" class="s">start key inclusive, end key exclusive; '' means "the very beginning" or "the very end"</text>
</svg>
:::

How does a client find the region for a row? HBase keeps the answer in **special tables of its own**:

- **`.META.`** lists every region of every user table: its start key, end key and the server hosting it.
- **`-ROOT-`** lists the regions of `.META.` itself (since `.META.` can also be big and split).
- **ZooKeeper** stores where `-ROOT-` is.

```text
hbase> scan '.META.', { COLUMNS => [ 'info:server', 'info:regioninfo' ] }
 wiki,,1300099733696.a79c0f6896c005711cf6a4448775a33b.
   column=info:regioninfo, value=REGION => {
     NAME => 'wiki,,1300099733696.a79c...',
     STARTKEY => '',
     ENDKEY => 'Demographics of Macedonia', ...}
   column=info:server, value=localhost:39005
```

:::fig **Finding a row in the 2012 version of HBase.** The client asks ZooKeeper where -ROOT- is, -ROOT- says where the right part of .META. is, .META. says which region server holds the row, and then the client talks to that server directly. Clients cache these answers, so the lookup chain is rarely repeated.
<svg class="dg wide" viewBox="0 0 720 150">
<rect x="0" y="40" width="100" height="56" rx="8" class="box"/><text x="50" y="66" text-anchor="middle" class="b">client</text><text x="50" y="84" text-anchor="middle" class="s">row "Star Wars"?</text>
<rect x="130" y="40" width="120" height="56" rx="8" class="bw"/><text x="190" y="66" text-anchor="middle" class="b">ZooKeeper</text><text x="190" y="84" text-anchor="middle" class="s">where is -ROOT-?</text>
<rect x="280" y="40" width="120" height="56" rx="8" class="bv"/><text x="340" y="66" text-anchor="middle" class="b mono">-ROOT-</text><text x="340" y="84" text-anchor="middle" class="s">which .META. region?</text>
<rect x="430" y="40" width="120" height="56" rx="8" class="bv"/><text x="490" y="66" text-anchor="middle" class="b mono">.META.</text><text x="490" y="84" text-anchor="middle" class="s">which server?</text>
<rect x="580" y="40" width="130" height="56" rx="8" class="bg"/><text x="645" y="66" text-anchor="middle" class="b">region server</text><text x="645" y="84" text-anchor="middle" class="s">reads the row</text>
<line x1="100" y1="68" x2="128" y2="68" class="ln" marker-end="url(#arr)"/>
<line x1="250" y1="68" x2="278" y2="68" class="ln" marker-end="url(#arr)"/>
<line x1="400" y1="68" x2="428" y2="68" class="ln" marker-end="url(#arr)"/>
<line x1="550" y1="68" x2="578" y2="68" class="ln" marker-end="url(#arr)"/>
<text x="360" y="130" text-anchor="middle" class="s">answers are cached by the client; HBase 0.96+ removed -ROOT- (one less hop)</text>
</svg>
:::

`describe 'wiki'`, `describe '.META.'` and `describe '-ROOT-'` show each table's families and settings.

### Step 5: Scanning to build a links table

A `scan` reads rows **in key order** between a start row and a stop row. The book uses a scan over the whole wiki table to extract every `[[link]]` inside article text and record them in a new table:

```text
hbase> create 'links', {
  NAME => 'to', VERSIONS => 1, BLOOMFILTER => 'ROWCOL'
},{
  NAME => 'from', VERSIONS => 1, BLOOMFILTER => 'ROWCOL'
}
```

For each article, the script (`generate_wiki_links.rb`) writes:

- in the article's own row: one column `to:<target>` for every page it links to;
- in each target page's row: one column `from:<article>` saying who links to it.

```ruby
scanner = wiki_table.getScanner( Scan.new )   # whole table, in key order
while (result = scanner.next())
  title = Bytes.toString( result.getRow() )
  text  = Bytes.toString( result.getValue( *jbytes('text', '') ) )
  if text
    put_to = nil
    text.scan(/\[\[([^\]\|\:]+)[^\]]*\]\]/) do
      link = $1
      put_to ||= Put.new( *jbytes( title ) )
      put_to.add( *jbytes( 'to', link, 1 ) )
      put_from = Put.new( *jbytes( link ) )
      put_from.add( *jbytes( 'from', title, 1 ) )
      links_table.put( put_from )
    end
    links_table.put( put_to ) if put_to
  end
end
```

:::fig **A wide row in the links table.** The row for "Star Wars" has one column per page it links to and one per page linking to it: possibly thousands of columns, each with an empty-ish value. In HBase that is perfectly normal; column qualifiers are data.
<svg class="dg wide" viewBox="0 0 720 170">
<rect x="10" y="50" width="110" height="80" rx="8" class="bv"/><text x="65" y="86" text-anchor="middle" class="b mono">Star Wars</text><text x="65" y="106" text-anchor="middle" class="s">row key</text>
<rect x="130" y="20" width="580" height="60" rx="8" class="ba"/>
<text x="142" y="40" class="s b ta">family to:</text>
<g class="mono s"><text x="142" y="64">to:George Lucas</text><text x="282" y="64">to:Harrison Ford</text><text x="428" y="64">to:Lightsaber</text><text x="552" y="64">… 1,500 more</text></g>
<rect x="130" y="96" width="580" height="60" rx="8" class="bg"/>
<text x="142" y="116" class="s b tg">family from:</text>
<g class="mono s"><text x="142" y="140">from:1977 in film</text><text x="292" y="140">from:Admiral Ackbar</text><text x="452" y="140">from:Jedi</text><text x="552" y="140">… 4,000 more</text></g>
</svg>
:::

```text
hbase> scan 'links', STARTROW => "Admiral Ackbar", ENDROW => "It's a Trap!"
hbase> get 'links', 'Star Wars'
hbase> count 'wiki', INTERVAL => 100000, CACHE => 10000
```

`count` has to scan the whole table, so on millions of rows it reports progress every `INTERVAL` rows and fetches `CACHE` rows per network call to go faster.

### Step 6: Schema design tips from the book

| Guideline | Why |
|---|---|
| **Few column families** (one to three). | Each family has its own files and flushes; many families mean many small files and slow operations. |
| **Many columns are fine**, even millions per row. | Qualifiers are just data inside the family. |
| **Group data by access pattern and settings.** | Data read together, or needing the same compression or versioning, belongs in the same family. |
| **Design the row key for your queries.** | The row key is the only index. Rows are sorted by it, so related rows should share a prefix and scans can fetch them in one pass. |
| **Avoid "hot" keys**, such as raw timestamps. | Sequential keys send every new write to the same region (one busy server). Prefixing or hashing spreads the load. |
| **Tall and narrow vs. wide.** | One row per item (tall) scales across regions better than one huge row (wide), since a row never splits across regions. |

### Day 2 homework, solved

**Find (summaries):**
- **Compression pros and cons:** less disk and less I/O, especially for text, at the cost of CPU to compress and decompress. GZ compresses best but slowly; LZO and Snappy (and today LZ4 and ZSTD) are faster with less compression.
- **Bloom filters:** see the figure above. They let HBase skip files that cannot contain the requested row (or row+column), which speeds up random reads.
- **Other compression-related family options:** `BLOCKSIZE` (bigger blocks compress better but slow random reads), `DATA_BLOCK_ENCODING` (cheap encodings such as prefix or diff encoding for similar keys), `COMPRESSION_COMPACT` (a separate codec used during compaction), and `IN_MEMORY`/`BLOCKCACHE` (keep hot data cached).
- **Choosing by data type:** large text compresses well, so use GZ or ZSTD for archives; small, frequently read values gain little and pay CPU on every read, so use a fast codec or none.

**Do: a `foods` table from the USDA MyPyramid XML data.**

```text
hbase> create 'foods', { NAME => 'facts', VERSIONS => 1, COMPRESSION => 'GZ', BLOOMFILTER => 'ROW' }
```

Use `Food_Code` as the row key (it is unique; a display name may not be), one family `facts` with a column per XML tag, `VERSIONS => 1` because the data does not change, and compression since the values are repetitive text. The import script follows the Wikipedia one, collecting each `<Food_Display_Row>` and writing it as one `Put`:

```ruby
import 'org.apache.hadoop.hbase.client.HTable'
import 'org.apache.hadoop.hbase.client.Put'
import 'javax.xml.stream.XMLStreamConstants'

def jbytes( *args ) args.map { |a| a.to_s.to_java_bytes } end

factory = javax.xml.stream.XMLInputFactory.newInstance
reader  = factory.createXMLStreamReader(java.lang.System.in)
table   = HTable.new( @hbase.configuration, 'foods' )
table.setAutoFlush( false )

row = nil; tag = nil; text = ''; count = 0
while reader.has_next
  case reader.next
  when XMLStreamConstants::START_ELEMENT
    tag = reader.local_name
    row = {} if tag == 'Food_Display_Row'
    text = ''
  when XMLStreamConstants::CHARACTERS
    text << reader.text
  when XMLStreamConstants::END_ELEMENT
    name = reader.local_name
    if name == 'Food_Display_Row'
      p = Put.new( *jbytes( row['Food_Code'] ) )
      row.each { |k, v| p.add( *jbytes( 'facts', k, v ) ) }
      table.put( p )
      count += 1
      table.flushCommits if count % 500 == 0
    elsif row
      row[name] = text.strip
    end
  end
end
table.flushCommits
puts "#{count} foods imported"
exit
```

```bash
cat Food_Display_Table.xml | bin/hbase shell import_food_data.rb
```

```text
hbase> get 'foods', '13110100'
hbase> scan 'foods', { COLUMNS => ['facts:Display_Name', 'facts:Calories'], LIMIT => 5 }
```

## Day 3 · Taking it to the cloud

Day 3 leaves the shell behind: first connecting from another language with **Thrift**, then launching a real multi-node cluster on **Amazon EC2** with **Apache Whirr**.

### Step 1: Thrift

The Java API only works from JVM languages. **Thrift** (originally from Facebook) solves this: you describe a service once in an **interface definition language (IDL)** file, and Thrift **generates client code** for many languages (Ruby, Python, PHP, C++, Go...). HBase ships with an `Hbase.thrift` file and a Thrift server.

:::fig **How Thrift connects any language to HBase.** The Hbase.thrift interface file is compiled into client code for your language. Your program calls those generated functions; they send compact binary messages to the Thrift server, which calls HBase's Java API.
<svg class="dg wide" viewBox="0 0 720 200">
<rect x="10" y="20" width="140" height="56" rx="8" class="bw"/><text x="80" y="44" text-anchor="middle" class="b mono">Hbase.thrift</text><text x="80" y="62" text-anchor="middle" class="s">service description</text>
<line x1="150" y1="48" x2="200" y2="48" class="ln" marker-end="url(#arr)"/>
<text x="175" y="38" text-anchor="middle" class="s">thrift --gen</text>
<rect x="204" y="10" width="150" height="34" rx="6" class="box"/><text x="279" y="32" text-anchor="middle" class="s">Ruby client code</text>
<rect x="204" y="50" width="150" height="34" rx="6" class="box"/><text x="279" y="72" text-anchor="middle" class="s">Python client code</text>
<rect x="204" y="90" width="150" height="34" rx="6" class="box"/><text x="279" y="112" text-anchor="middle" class="s">PHP, C++, Go…</text>
<rect x="204" y="140" width="150" height="50" rx="8" class="ba"/><text x="279" y="162" text-anchor="middle" class="b">your program</text><text x="279" y="180" text-anchor="middle" class="s">uses Ruby code</text>
<line x1="356" y1="165" x2="440" y2="165" class="ln" marker-end="url(#arr)"/>
<text x="398" y="155" text-anchor="middle" class="s">binary, TCP 9090</text>
<rect x="444" y="138" width="130" height="54" rx="8" class="bv"/><text x="509" y="162" text-anchor="middle" class="b">Thrift server</text><text x="509" y="180" text-anchor="middle" class="s">part of HBase</text>
<line x1="576" y1="165" x2="616" y2="165" class="ln" marker-end="url(#arr)"/>
<rect x="620" y="138" width="90" height="54" rx="8" class="bv"/><text x="665" y="170" text-anchor="middle" class="b">HBase</text>
</svg>
:::

```bash
thrift -version                          # check the Thrift compiler is installed
gem install thrift                       # Ruby runtime library
thrift --gen rb <path_to_Hbase.thrift>   # generates gen-rb/ with Hbase client code
bin/hbase-daemon.sh start thrift -b 127.0.0.1
```

A small Ruby client that lists every table and its column families:

```ruby
$:.push('./gen-rb')
require 'thrift'
require 'hbase'

socket    = Thrift::Socket.new( 'localhost', 9090 )
transport = Thrift::BufferedTransport.new( socket )
protocol  = Thrift::BinaryProtocol.new( transport )
client    = Apache::Hadoop::Hbase::Thrift::Hbase::Client.new( protocol )

transport.open()
client.getTableNames().sort.each do |table|
  puts "#{table}"
  client.getColumnDescriptors( table ).each do |col, desc|
    puts "  #{desc.name}"
    puts "    maxVersions: #{desc.maxVersions}"
    puts "    compression: #{desc.compression}"
    puts "    bloomFilterType: #{desc.bloomFilterType}"
  end
end
transport.close()
```

The three layers (socket, transport, protocol) are Thrift's way of separating "how bytes travel" from "how data is encoded".

### Step 2: A real cluster on EC2 with Whirr

Standalone mode is a toy. A real HBase deployment needs HDFS, ZooKeeper, a master and several region servers, which is a lot to install by hand. **Apache Whirr** automated it: you describe the cluster in a properties file and Whirr creates the machines on a cloud provider and installs everything.

```bash
bin/whirr version
mkdir keys
ssh-keygen -t rsa -P '' -f keys/id_rsa      # SSH key for logging in to the nodes
```

```properties
# hbase.properties
whirr.cluster-name=myhbasecluster
whirr.instance-templates=\
  1 zookeeper+hadoop-namenode+hadoop-jobtracker+hbase-master,\
  5 hadoop-datanode+hadoop-tasktracker+hbase-regionserver
whirr.provider=aws-ec2
whirr.identity=${env:AWS_ACCESS_KEY_ID}
whirr.credential=${env:AWS_SECRET_ACCESS_KEY}
whirr.private-key-file=keys/id_rsa
whirr.public-key-file=keys/id_rsa.pub
whirr.hbase.tarball.url=http://archive.apache.org/dist/hbase/hbase-0.90.3/hbase-0.90.3.tar.gz
```

:::fig **The cluster Whirr builds.** One machine runs the coordinating services (ZooKeeper, the HDFS NameNode, the Hadoop JobTracker and the HBase master). Five worker machines each store HDFS data, run MapReduce tasks, and serve HBase regions.
<svg class="dg wide" viewBox="0 0 720 230">
<rect x="250" y="10" width="220" height="80" rx="10" class="bw"/>
<text x="360" y="32" text-anchor="middle" class="b">1 coordinator node</text>
<text x="360" y="52" text-anchor="middle" class="s">ZooKeeper · NameNode</text>
<text x="360" y="70" text-anchor="middle" class="s">JobTracker · HBase master</text>
<g>
<rect x="10" y="140" width="130" height="80" rx="10" class="bv"/><text x="75" y="164" text-anchor="middle" class="b">worker 1</text><text x="75" y="184" text-anchor="middle" class="s">DataNode</text><text x="75" y="200" text-anchor="middle" class="s">TaskTracker</text><text x="75" y="216" text-anchor="middle" class="s">RegionServer</text>
<rect x="152" y="140" width="130" height="80" rx="10" class="bv"/><text x="217" y="164" text-anchor="middle" class="b">worker 2</text><text x="217" y="184" text-anchor="middle" class="s">DataNode</text><text x="217" y="200" text-anchor="middle" class="s">TaskTracker</text><text x="217" y="216" text-anchor="middle" class="s">RegionServer</text>
<rect x="294" y="140" width="130" height="80" rx="10" class="bv"/><text x="359" y="164" text-anchor="middle" class="b">worker 3</text><text x="359" y="184" text-anchor="middle" class="s">DataNode</text><text x="359" y="200" text-anchor="middle" class="s">TaskTracker</text><text x="359" y="216" text-anchor="middle" class="s">RegionServer</text>
<rect x="436" y="140" width="130" height="80" rx="10" class="bv"/><text x="501" y="164" text-anchor="middle" class="b">worker 4</text><text x="501" y="184" text-anchor="middle" class="s">DataNode</text><text x="501" y="200" text-anchor="middle" class="s">TaskTracker</text><text x="501" y="216" text-anchor="middle" class="s">RegionServer</text>
<rect x="578" y="140" width="130" height="80" rx="10" class="bv"/><text x="643" y="164" text-anchor="middle" class="b">worker 5</text><text x="643" y="184" text-anchor="middle" class="s">DataNode</text><text x="643" y="200" text-anchor="middle" class="s">TaskTracker</text><text x="643" y="216" text-anchor="middle" class="s">RegionServer</text>
</g>
<line x1="320" y1="92" x2="75" y2="138" class="ln2"/><line x1="340" y1="92" x2="217" y2="138" class="ln2"/><line x1="360" y1="92" x2="359" y2="138" class="ln2"/><line x1="380" y1="92" x2="501" y2="138" class="ln2"/><line x1="400" y1="92" x2="643" y2="138" class="ln2"/>
</svg>
:::

```bash
bin/whirr launch-cluster --config hbase.properties   # takes several minutes
ssh -i keys/id_rsa ${USER}@<SERVER_NAME>              # log in to a node
/usr/local/hbase-0.90.3/bin/hbase shell               # and use HBase there

bin/whirr destroy-cluster --config hbase.properties  # IMPORTANT when you are done
```

:::warn Don't forget to destroy the cluster
Six cloud machines cost money every hour they run, whether or not you use them. The book stresses running `destroy-cluster` as soon as you finish experimenting.
:::

### Day 3 homework, solved

The homework connects your local Thrift client to the EC2 cluster:

1. SSH to a node, open `hbase shell`, and `create 'test', 'data'`.
2. On that node, start Thrift listening on all interfaces: `sudo /usr/local/hbase-0.90.3/bin/hbase-daemon.sh start thrift -b 0.0.0.0`.
3. In the EC2 console, open **TCP port 9090** in the cluster's security group.
4. Change the Ruby client's `Thrift::Socket.new('localhost', 9090)` to the node's public hostname and run it. It should print `test` and its `data:` family.

The authors stress that this opens an **unencrypted** port to the internet. In production you would use a VPN or private network instead.

## Wrap-up · Strengths and weaknesses

HBase mixes simplicity and complexity. The storage model is simple, with a few built-in constraints. But its terms (table, column) carry relational baggage, and most schema design is about **performance**: which families, which options, which row key.

### Strengths

- **Robust scale-out architecture**: for data measured in many gigabytes to terabytes and beyond.
- **Built-in versioning**: page history for a wiki comes for free.
- **Compression and Bloom filters** per column family.
- **Rack awareness**: HBase (through HDFS) replicates data within and between racks in a data center, so failures are handled quickly.
- **A helpful community**, with no single company controlling the project.

### Weaknesses

- **It doesn't scale down.** Five nodes is the practical minimum, so it is overkill for small problems, and harder to administer.
- **It is never alone.** You also run Hadoop, HDFS and ZooKeeper. That ecosystem gives robustness but adds operational burden.
- **The row key is the only index.** No sorting or indexing on other fields; otherwise you scan or maintain your own index tables.
- **No data types.** Everything is bytes; your application must interpret them.
- Expert-level documentation and a steep learning curve.

### HBase and CAP

HBase is **CP**: consistent and partition-tolerant. A successful write is immediately visible to every client. When a node fails, other nodes take over its regions, so in practice it stays available. In the extreme case where too few nodes survive, HBase refuses requests rather than return stale data. Unlike Riak, you cannot tune this per request. (Cluster-to-cluster replication across data centers, which the book does not cover, is eventually consistent: replica clusters may lag behind the primary.)

:::modern HBase in 2026
- **Still alive and maintained** by the Apache community. HBase 3.0, the first new major version since 2.0 (2018), was released in August 2026 after several years of alpha and beta releases; the 2.5 and 2.6 lines are still maintained. It remains in use at large companies for huge, write-heavy workloads.
- **`-ROOT-` was removed** in HBase 0.96 (2013); the catalog table `.META.` is now called **`hbase:meta`**, and ZooKeeper points straight to it.
- **The Java client API changed**: `HTable.new(...)` became `ConnectionFactory.createConnection(conf).getTable(...)`, `setAutoFlush`/`flushCommits` became `BufferedMutator`, and `setWriteToWAL(false)` became `setDurability(Durability.SKIP_WAL)`.
- **Apache Whirr was retired** in 2015. Today you would run HBase on Amazon EMR, on Kubernetes, or use **Google Cloud Bigtable**, which offers an HBase-compatible API.
- **SQL on top:** Apache Phoenix adds a SQL layer and secondary indexes to HBase.
- **Alternatives** in the wide-column space: **Apache Cassandra** and **ScyllaDB** (which use the column-family model with Dynamo-style distribution and a SQL-like language, CQL), and Bigtable itself. Meanwhile much big-data analytics moved to Spark, columnar file formats (Parquet) and cloud data warehouses.
:::

:::key Chapter 4 in a nutshell
- **Data model:** table → sorted row key → column family (fixed) → qualifier (free) → timestamp → bytes. Sparse rows cost nothing.
- **Day 1:** `create`, `put`, `get`, `scan`, `delete`; versions per cell; `disable`/`alter`/`enable` to change families; atomic `Put` per row via the Java API in JRuby.
- **Day 2:** streaming import of Wikipedia; batching (`setAutoFlush`), the WAL, MemStore, HFiles and compaction; GZ compression and Bloom filters; regions, region servers, `.META.` and `-ROOT-`; scans and the links table; schema tips.
- **Day 3:** Thrift for other languages; launching an EC2 cluster with Whirr.
- **Choose it when** you have truly big data, need versioning and strong consistency, and can run a Hadoop cluster. **Avoid it** for small data or ad hoc queries.
:::

@@quiz
Q: Which statement best describes HBase's data model?
- Fixed tables with typed columns, like PostgreSQL
+ A sorted map: row key → column family → column qualifier → timestamp → value (bytes)
- A graph of nodes and relationships
- A list of JSON documents in collections
? HBase is a sparse, sorted, multidimensional map. Families are fixed per table; qualifiers, values and versions are decided at write time, and everything is bytes.

Q: What must you specify when you create an HBase table?
- Every column name and its type
- The row keys it will contain
+ Only the column families (with their options)
- Nothing; tables are created on the first put
? `create 'wiki', 'text'` names the table and its column families. Column qualifiers are invented freely by each put.

Q: You `put` a new value into a cell that already has a value. What happens?
- The old value is overwritten and lost immediately
+ A new version with a newer timestamp is added; older versions are kept up to the family's VERSIONS limit
- HBase rejects the write
- The two values are concatenated
? Every cell is versioned by timestamp. A get returns the newest version by default, and older ones can be requested until they are removed by compaction.

Q: Why does the book run `disable 'wiki'` before `alter`?
+ Changing a table's column families required taking the table offline first
- To delete all its data
- Because alter only works on empty tables
- To stop other users from reading the wiki forever
? In the HBase versions of the book, schema changes such as adding a family or changing VERSIONS needed the table disabled, then re-enabled afterwards.

Q: What does a Bloom filter tell HBase about a data file?
- Exactly which row the file contains
- How compressed the file is
+ Whether a row key is definitely not in the file, or might be in it
- The timestamp of the newest version
? A Bloom filter can say "definitely not here" (so the file is skipped) or "maybe here". It never gives false negatives, which is what makes skipping safe.

Q: What is the purpose of the write-ahead log (WAL)?
- To speed up reads by caching popular rows
+ To record every write durably before it is applied in memory, so it can be replayed if a region server crashes
- To store old versions of cells
- To log errors for administrators
? Writes go to the WAL and then to the in-memory MemStore. If the server dies before flushing the MemStore to an HFile, the WAL is replayed. Skipping the WAL is faster but risks data loss.

Q: How does HBase spread a large table across many servers?
- By hashing each row key to a random server
+ By splitting it into regions, each a contiguous range of sorted row keys, assigned to region servers
- By putting each column family on a different server
- It cannot; each table lives on one server
? Regions are key ranges (start inclusive, end exclusive). They split as they grow and are assigned to region servers by the master. The `.META.` table records where each region lives.

Q: Which query is efficient in HBase without extra work?
+ Fetch all rows whose keys fall between "Admiral Ackbar" and "It's a Trap!"
- Find every page whose author is "jimbo"
- Find the 10 longest articles
- Join the wiki table with a users table
? Rows are sorted by key, so a scan over a key range is efficient. HBase has no secondary indexes or joins, so filtering on other fields requires a full scan or a hand-built index table.

Q: What problem does Thrift solve for HBase?
- It compresses HBase files
+ It lets programs in non-JVM languages (Ruby, Python, PHP...) talk to HBase through generated client code
- It replaces ZooKeeper
- It launches clusters on Amazon EC2
? Thrift compiles an interface description (Hbase.thrift) into client libraries for many languages, which talk binary over TCP to HBase's Thrift server.

Q: Where does HBase sit in the CAP trade-off, according to the book?
- AP: always available, eventually consistent
+ CP: strongly consistent; if too few nodes survive a partition it refuses requests rather than serve stale data
- CA: it is not distributed
- Tunable per request, like Riak
? HBase guarantees that a successful write is seen by the next read. It handles node failures by reassigning regions, but in a severe partition it chooses consistency over availability.

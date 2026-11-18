title: Redis
lead: A blazing-fast, in-memory data structure server. Strings, hashes, lists, sets, sorted sets and expiry on Day 1; pipelining, pub/sub, durability, replication, sharding and Bloom filters on Day 2; a polyglot application with CouchDB and Neo4J on Day 3.

## Overview: a data structure server

**Redis** (REmote DIctionary Server) is a key-value store, but a very unusual one. Its values are not opaque blobs: they are real **data structures** (strings, hashes, lists, sets and sorted sets) and Redis provides commands that operate on them directly, on the server, atomically. That is why its own documentation calls it a **data structure server**.

Its other defining feature is **speed**. Redis keeps the whole dataset **in memory** and writes to disk in the background. Reads and writes take microseconds, and a single server handles tens of thousands of operations per second, even on a laptop. The trade-off: if the machine fails before data is saved, the most recent writes can be lost, and the dataset must fit in RAM.

The authors compare Redis to a **multitool**: a knife, can opener and corkscrew in one. It is rarely the main database of a system, but it is the perfect helper: a cache, a queue, a message broker, a leaderboard, a session store, a set calculator.

:::fig **Redis values are data structures.** Every key holds one of five types, and each type has its own family of commands, run atomically on the server: `GET`/`INCR` for strings, `H…` for hashes, `L…`/`R…` for lists, `S…` for sets, `Z…` for sorted sets.
<svg class="dg wide" viewBox="0 0 720 300">
<text x="10" y="24" class="b">string</text>
<rect x="110" y="8" width="70" height="26" rx="5" class="bw"/><text x="145" y="26" text-anchor="middle" class="mono s">7wks</text>
<line x1="182" y1="21" x2="210" y2="21" class="ln" marker-end="url(#arr)"/>
<rect x="214" y="8" width="230" height="26" rx="5" class="box"/><text x="224" y="26" class="mono s">"http://www.sevenweeks.org/"</text>
<text x="470" y="26" class="s">GET SET INCR APPEND</text>
<text x="10" y="80" class="b">hash</text>
<rect x="110" y="64" width="70" height="26" rx="5" class="bw"/><text x="145" y="82" text-anchor="middle" class="mono s">user:eric</text>
<line x1="182" y1="77" x2="210" y2="77" class="ln" marker-end="url(#arr)"/>
<rect x="214" y="52" width="230" height="50" rx="5" class="box"/>
<text x="224" y="72" class="mono s">name → "Eric Redmond"</text><text x="224" y="92" class="mono s">password → "s3cret"</text>
<text x="470" y="82" class="s">HSET HGET HKEYS HVALS</text>
<text x="10" y="140" class="b">list</text>
<rect x="110" y="124" width="70" height="26" rx="5" class="bw"/><text x="145" y="142" text-anchor="middle" class="mono s">wishlist</text>
<line x1="182" y1="137" x2="210" y2="137" class="ln" marker-end="url(#arr)"/>
<g class="mono s"><rect x="214" y="124" width="70" height="26" rx="5" class="box"/><text x="249" y="142" text-anchor="middle">7wks</text>
<rect x="288" y="124" width="70" height="26" rx="5" class="box"/><text x="323" y="142" text-anchor="middle">gog</text>
<rect x="362" y="124" width="70" height="26" rx="5" class="box"/><text x="397" y="142" text-anchor="middle">prag</text></g>
<text x="470" y="142" class="s">LPUSH RPUSH LPOP LRANGE</text>
<text x="10" y="200" class="b">set</text>
<rect x="110" y="184" width="70" height="26" rx="5" class="bw"/><text x="145" y="202" text-anchor="middle" class="mono s">news</text>
<line x1="182" y1="197" x2="210" y2="197" class="ln" marker-end="url(#arr)"/>
<ellipse cx="329" cy="197" rx="115" ry="24" class="box"/><text x="329" y="202" text-anchor="middle" class="mono s">{ nytimes.com, pragprog.com }</text>
<text x="470" y="202" class="s">SADD SINTER SUNION SDIFF</text>
<text x="10" y="264" class="b">sorted set</text>
<rect x="110" y="248" width="70" height="26" rx="5" class="bw"/><text x="145" y="266" text-anchor="middle" class="mono s">visits</text>
<line x1="182" y1="261" x2="210" y2="261" class="ln" marker-end="url(#arr)"/>
<g class="mono s"><rect x="214" y="248" width="70" height="26" rx="5" class="box"/><text x="249" y="266" text-anchor="middle">gog 9</text>
<rect x="288" y="248" width="70" height="26" rx="5" class="box"/><text x="323" y="266" text-anchor="middle">7wks 500</text>
<rect x="362" y="248" width="82" height="26" rx="5" class="box"/><text x="403" y="266" text-anchor="middle">prag 9999</text></g>
<text x="470" y="266" class="s">ZADD ZRANGE ZRANGEBYSCORE</text>
<text x="329" y="294" text-anchor="middle" class="s">always ordered by score</text>
</svg>
:::

## Day 1 · CRUD and datatypes

### Step 1: Starting up

```bash
redis-server              # start the server on port 6379
redis-cli                 # open the command-line client
```

```text
redis 127.0.0.1:6379> PING
PONG
redis 127.0.0.1:6379> help
```

The running example of the chapter is a **URL shortener**, like bit.ly: short codes mapped to long URLs.

### Step 2: Strings: SET, GET and counters

```text
redis 127.0.0.1:6379> SET 7wks http://www.sevenweeks.org/
OK
redis 127.0.0.1:6379> GET 7wks
"http://www.sevenweeks.org/"

redis 127.0.0.1:6379> MSET gog http://www.google.com yah http://www.yahoo.com
OK
redis 127.0.0.1:6379> MGET gog yah
1) "http://www.google.com/"
2) "http://www.yahoo.com/"
```

`MSET`/`MGET` set or get several keys in one command, saving round trips. Redis stores strings, but it recognizes integers and can do arithmetic on them atomically, which is perfect for generating the next short code or counting clicks:

```text
redis 127.0.0.1:6379> SET count 2
redis 127.0.0.1:6379> INCR count
(integer) 3
redis 127.0.0.1:6379> GET count
"3"
redis 127.0.0.1:6379> SET bad_count "a"
redis 127.0.0.1:6379> INCR bad_count
(error) ERR value is not an integer or out of range
```

Related commands: `INCRBY count 10`, `DECR`, `DECRBY`.

:::deep Why atomic counters are a big deal
Redis runs commands **one at a time** on a single thread. A command never sees another command half-finished. So when a thousand web servers call `INCR count` at the same moment, every increment is counted, without locks or transactions. The same is true for every Redis command, which is why data structure operations on the server are so useful.
:::

### Step 3: Transactions with MULTI and EXEC

To run **several** commands as one unit, wrap them in `MULTI` … `EXEC`. Redis **queues** the commands and then runs them all together, with no other client's commands in between:

```text
redis 127.0.0.1:6379> MULTI
OK
redis 127.0.0.1:6379> SET prag http://pragprog.com
QUEUED
redis 127.0.0.1:6379> INCR count
QUEUED
redis 127.0.0.1:6379> EXEC
1) OK
2) (integer) 4
```

`DISCARD` throws the queued commands away instead.

:::warn Not quite a SQL transaction
A Redis transaction guarantees the queued commands run **together and in order**. It does **not** roll back: if one queued command fails (say, `INCR` on a non-number), the others still run. And `DISCARD` only works before `EXEC`; it empties the queue, it does not undo anything. Think of MULTI as "run this batch without interruption", not as BEGIN/ROLLBACK.
:::

### Step 4: Hashes

You could store a user's fields as separate keys (`user:eric:name`, `user:eric:password`), but a **hash** keeps them together under one key, like a small document or a row:

```text
redis 127.0.0.1:6379> MSET user:eric:name "Eric Redmond" user:eric:password s3cret
redis 127.0.0.1:6379> MGET user:eric:name user:eric:password

redis 127.0.0.1:6379> HMSET user:eric name "Eric Redmond" password s3cret
OK
redis 127.0.0.1:6379> HVALS user:eric
1) "Eric Redmond"
2) "s3cret"
redis 127.0.0.1:6379> HKEYS user:eric
1) "name"
2) "password"
redis 127.0.0.1:6379> HGET user:eric password
"s3cret"
```

Others: `HDEL` (delete a field), `HINCRBY` (increment a numeric field), `HLEN` (number of fields), `HGETALL` (all fields and values). Hash values cannot nest: a field holds a string, not another hash.

:::tip Key naming
Redis has no tables, so the convention is to build structure into key names with colons: `user:eric`, `user:eric:wishlist`, `band:Beatles`. It costs nothing and makes keys readable and easy to group.
:::

### Step 5: Lists

A **list** is an ordered sequence of strings. You add and remove at **both ends**, so a list works as a **queue** (push at one end, pop at the other) or a **stack** (push and pop at the same end).

```text
redis 127.0.0.1:6379> RPUSH eric:wishlist 7wks gog prag
(integer) 3
redis 127.0.0.1:6379> LRANGE eric:wishlist 0 -1        # 0 to -1 = whole list
1) "7wks"
2) "gog"
3) "prag"
redis 127.0.0.1:6379> LREM eric:wishlist 0 gog          # remove all "gog" (0 = all)
redis 127.0.0.1:6379> LPOP eric:wishlist                # take from the left
"7wks"
redis 127.0.0.1:6379> RPOPLPUSH eric:wishlist eric:visited
"prag"
```

`RPOPLPUSH` pops from the right of one list and pushes onto the left of another **in one atomic step**. If a worker takes a job this way, the job is never in neither list, so it cannot be lost between the two operations.

:::fig **List operations.** L commands work on the left end, R commands on the right. RPOPLPUSH atomically moves an item from the right of one list to the left of another, for example from "to do" to "in progress".
<svg class="dg wide" viewBox="0 0 720 200">
<text x="10" y="40" class="b mono s">eric:wishlist</text>
<g class="mono s">
<rect x="150" y="20" width="90" height="34" rx="6" class="box"/><text x="195" y="42" text-anchor="middle">7wks</text>
<rect x="244" y="20" width="90" height="34" rx="6" class="box"/><text x="289" y="42" text-anchor="middle">gog</text>
<rect x="338" y="20" width="90" height="34" rx="6" class="bw"/><text x="383" y="42" text-anchor="middle">prag</text>
</g>
<line x1="146" y1="37" x2="96" y2="80" class="ln" marker-end="url(#arr)"/><text x="40" y="96" class="mono s">LPOP</text>
<line x1="100" y1="16" x2="146" y2="30" class="ln" marker-end="url(#arr)"/><text x="40" y="16" class="mono s">LPUSH</text>
<line x1="480" y1="16" x2="432" y2="30" class="ln" marker-end="url(#arr)"/><text x="486" y="16" class="mono s">RPUSH</text>
<path d="M383,56 C383,100 210,100 210,128" class="lw" marker-end="url(#arrw)"/>
<text x="330" y="98" class="mono s tw b">RPOPLPUSH</text>
<text x="10" y="156" class="b mono s">eric:visited</text>
<g class="mono s">
<rect x="150" y="134" width="90" height="34" rx="6" class="bw"/><text x="195" y="156" text-anchor="middle">prag</text>
<rect x="244" y="134" width="90" height="34" rx="6" class="box"/><text x="289" y="156" text-anchor="middle">…</text>
</g>
<text x="560" y="140" class="s">one atomic step:</text><text x="560" y="158" class="s">the item is never</text><text x="560" y="176" class="s">in neither list</text>
</svg>
:::

#### Blocking lists: a message queue in two commands

The **blocking** pop commands (`BLPOP`, `BRPOP`, `BRPOPLPUSH`) wait until the list has something to pop, up to a timeout. That turns a list into a **message queue** between programs. Open two terminals:

```text
# terminal 1: a consumer waits up to 300 seconds for a comment
redis 127.0.0.1:6379> BRPOP comments 300

# terminal 2: a producer pushes one
redis 127.0.0.1:6379> LPUSH comments "Prag is great! I buy all my books there."

# terminal 1 wakes up immediately:
1) "comments"
2) "Prag is great! I buy all my books there."
(50.22s)                   # how long the consumer was blocked
```

:::fig **A blocking list as a job queue.** Producers push jobs on one end. Workers block on BRPOP at the other end and wake up the moment a job arrives, with no polling. If several workers wait, each job goes to exactly one of them.
<svg class="dg wide" viewBox="0 0 720 200">
<rect x="10" y="30" width="120" height="44" rx="8" class="box"/><text x="70" y="57" text-anchor="middle" class="b">web app</text>
<rect x="10" y="110" width="120" height="44" rx="8" class="box"/><text x="70" y="137" text-anchor="middle" class="b">mobile app</text>
<line x1="132" y1="52" x2="216" y2="86" class="ln" marker-end="url(#arr)"/><line x1="132" y1="132" x2="216" y2="100" class="ln" marker-end="url(#arr)"/>
<text x="170" y="52" class="mono s">LPUSH</text>
<rect x="220" y="70" width="280" height="44" rx="8" class="bw"/>
<g class="mono s"><text x="236" y="97">job5</text><text x="290" y="97">job4</text><text x="344" y="97">job3</text><text x="398" y="97">job2</text><text x="452" y="97">job1</text></g>
<text x="360" y="62" text-anchor="middle" class="s b">list "comments"</text>
<line x1="502" y1="86" x2="586" y2="52" class="ln" marker-end="url(#arr)"/><line x1="502" y1="100" x2="586" y2="132" class="ln" marker-end="url(#arr)"/>
<text x="514" y="52" class="mono s">BRPOP</text>
<rect x="590" y="30" width="120" height="44" rx="8" class="bg"/><text x="650" y="50" text-anchor="middle" class="b">worker 1</text><text x="650" y="66" text-anchor="middle" class="s">busy with job1</text>
<rect x="590" y="110" width="120" height="44" rx="8" class="bg"/><text x="650" y="130" text-anchor="middle" class="b">worker 2</text><text x="650" y="146" text-anchor="middle" class="s">waiting (blocked)</text>
<text x="360" y="186" text-anchor="middle" class="s">no polling: a blocked worker wakes up the instant a job is pushed</text>
</svg>
:::

### Step 6: Sets

A **set** is an unordered collection of **unique** strings. Adding the same value twice has no effect. Sets shine at **set algebra**, computed on the server:

```text
redis 127.0.0.1:6379> SADD news nytimes.com pragprog.com
redis 127.0.0.1:6379> SMEMBERS news
1) "pragprog.com"
2) "nytimes.com"
redis 127.0.0.1:6379> SADD tech pragprog.com apple.com

redis 127.0.0.1:6379> SINTER news tech          # in both
1) "pragprog.com"
redis 127.0.0.1:6379> SDIFF news tech           # in news but not in tech
1) "nytimes.com"
redis 127.0.0.1:6379> SUNION news tech          # in either
1) "pragprog.com"
2) "nytimes.com"
3) "apple.com"
redis 127.0.0.1:6379> SUNIONSTORE websites news tech     # store the union in a new key
```

:::fig **Set algebra on the server.** `SINTER` returns what is in both sets, `SDIFF` what is only in the first, and `SUNION` everything. The `…STORE` variants save the result in a new key.
<svg class="dg" viewBox="0 0 720 210">
<circle cx="270" cy="112" r="90" class="bw" fill-opacity="0.45"/>
<circle cx="370" cy="112" r="90" class="ba" fill-opacity="0.45"/>
<text x="230" y="14" text-anchor="middle" class="b">news</text><text x="410" y="14" text-anchor="middle" class="b">tech</text>
<text x="226" y="117" text-anchor="middle" class="mono s">nytimes.com</text>
<text x="320" y="117" text-anchor="middle" class="mono s b">pragprog.com</text>
<text x="416" y="117" text-anchor="middle" class="mono s">apple.com</text>
<text x="520" y="70" class="mono s">SINTER → pragprog.com</text>
<text x="520" y="100" class="mono s">SDIFF  → nytimes.com</text>
<text x="520" y="130" class="mono s">SUNION → all three</text>
</svg>
:::

Others: `SREM` (remove), `SMOVE` (move between sets atomically), `SCARD` (count), `SISMEMBER` (is it in?), `SPOP` (remove a random member), `SRANDMEMBER` (peek at a random member). Typical uses: tags, unique visitors, "who is online", friends in common.

### Step 7: Sorted sets

A **sorted set** is a set where every member has a **score** (a number), and members are kept **ordered by score**. That makes leaderboards, rankings, priority queues and time-ordered feeds trivial.

```text
redis 127.0.0.1:6379> ZADD visits 500 7wks 9 gog 9999 prag
(integer) 3
redis 127.0.0.1:6379> ZINCRBY visits 1 prag
"10000"
redis 127.0.0.1:6379> ZRANGE visits 0 1                     # lowest two
1) "gog"
2) "7wks"
redis 127.0.0.1:6379> ZREVRANGE visits 0 -1 WITHSCORES      # highest first
1) "prag"
2) "10000"
3) "7wks"
4) "500"
5) "gog"
6) "9"
redis 127.0.0.1:6379> ZRANGEBYSCORE visits 9 9999           # score range, inclusive
1) "gog"
2) "7wks"
redis 127.0.0.1:6379> ZRANGEBYSCORE visits (9 9999          # "(" makes it exclusive
1) "7wks"
redis 127.0.0.1:6379> ZRANGEBYSCORE visits -inf inf         # everything
```

Remove by rank or score with `ZREMRANGEBYRANK` and `ZREMRANGEBYSCORE`.

#### Combining sorted sets with weights

`ZUNIONSTORE` (and `ZINTERSTORE`) combine several sorted sets into a new one, multiplying each set's scores by a **weight** and then combining them with `SUM`, `MIN` or `MAX`:

```text
ZUNIONSTORE destination numkeys key [key ...] [WEIGHTS weight [weight ...]] [AGGREGATE SUM|MIN|MAX]
```

The book calculates an **importance** score from visits plus twice the votes:

```text
redis 127.0.0.1:6379> ZADD votes 2 7wks 0 gog 9001 prag
redis 127.0.0.1:6379> ZUNIONSTORE importance 2 visits votes WEIGHTS 1 2 AGGREGATE SUM
(integer) 3
redis 127.0.0.1:6379> ZRANGEBYSCORE importance -inf inf WITHSCORES
1) "gog"
2) "9"
3) "7wks"
4) "504"
5) "prag"
6) "28002"
```

:::fig **ZUNIONSTORE with weights.** Each member's new score is the weighted sum of its scores in the input sets: importance = visits × 1 + votes × 2.
<svg class="dg wide" viewBox="0 0 720 210">
<text x="80" y="24" text-anchor="middle" class="b">visits (×1)</text>
<g class="mono s"><rect x="10" y="36" width="140" height="30" rx="5" class="box"/><text x="20" y="56">gog 9</text>
<rect x="10" y="72" width="140" height="30" rx="5" class="box"/><text x="20" y="92">7wks 500</text>
<rect x="10" y="108" width="140" height="30" rx="5" class="box"/><text x="20" y="128">prag 10000</text></g>
<text x="270" y="24" text-anchor="middle" class="b">votes (×2)</text>
<g class="mono s"><rect x="200" y="36" width="140" height="30" rx="5" class="box"/><text x="210" y="56">gog 0</text>
<rect x="200" y="72" width="140" height="30" rx="5" class="box"/><text x="210" y="92">7wks 2</text>
<rect x="200" y="108" width="140" height="30" rx="5" class="box"/><text x="210" y="128">prag 9001</text></g>
<line x1="350" y1="87" x2="400" y2="87" class="ln" marker-end="url(#arr)"/>
<text x="545" y="24" text-anchor="middle" class="b">importance</text>
<g class="mono s"><rect x="410" y="36" width="300" height="30" rx="5" class="bg"/><text x="420" y="56">gog   9 + 2×0    = 9</text>
<rect x="410" y="72" width="300" height="30" rx="5" class="bg"/><text x="420" y="92">7wks  500 + 2×2  = 504</text>
<rect x="410" y="108" width="300" height="30" rx="5" class="bg"/><text x="420" y="128">prag  10000 + 2×9001 = 28002</text></g>
<text x="360" y="176" text-anchor="middle" class="s">ZUNIONSTORE votes 1 votes WEIGHTS 2 doubles every vote in place</text>
</svg>
:::

A union of a single set with a weight is a quick way to **multiply all scores**: `ZUNIONSTORE votes 1 votes WEIGHTS 2` doubles every vote.

### Step 8: Expiry

Any key can be given a **time to live**. When it expires, Redis deletes it automatically, which is exactly what a cache or a session store needs.

```text
redis 127.0.0.1:6379> SET ice "I'm melting…"
redis 127.0.0.1:6379> EXPIRE ice 10
redis 127.0.0.1:6379> EXISTS ice
(integer) 1
# … 10 seconds later …
redis 127.0.0.1:6379> EXISTS ice
(integer) 0

redis 127.0.0.1:6379> SETEX ice 10 "I'm melting…"      # set and expire in one command
redis 127.0.0.1:6379> TTL ice                           # seconds left
(integer) 8
redis 127.0.0.1:6379> PERSIST ice                       # cancel the expiry
```

`EXPIREAT` takes an absolute Unix timestamp instead of a number of seconds.

:::fig **A key with a time to live.** After `EXPIRE ice 10`, `TTL` counts down. When it reaches zero the key is gone, unless `PERSIST` removes the expiry first.
<svg class="dg" viewBox="0 0 720 150">
<line x1="40" y1="70" x2="680" y2="70" class="ln2"/>
<circle cx="80" cy="70" r="8" class="fw"/><text x="80" y="46" text-anchor="middle" class="mono s">SET ice</text>
<circle cx="200" cy="70" r="8" class="fw"/><text x="200" y="46" text-anchor="middle" class="mono s">EXPIRE ice 10</text>
<rect x="200" y="60" width="400" height="20" rx="10" class="bw" fill-opacity="0.6"/>
<text x="300" y="104" text-anchor="middle" class="mono s">TTL 8</text><text x="420" y="104" text-anchor="middle" class="mono s">TTL 4</text><text x="540" y="104" text-anchor="middle" class="mono s">TTL 1</text>
<circle cx="600" cy="70" r="9" class="fr"/><text x="600" y="46" text-anchor="middle" class="s tr b">deleted</text>
<text x="360" y="136" text-anchor="middle" class="s">useful for caches, sessions, rate limits and one-time codes</text>
</svg>
:::

### Step 9: Database namespaces

A Redis server holds several numbered **databases** (16 by default, numbered from 0), each with its own keys. They are a light way to separate data, for example testing versus development:

```text
redis 127.0.0.1:6379> SET greeting hello
redis 127.0.0.1:6379> SELECT 1
redis 127.0.0.1:6379[1]> GET greeting
(nil)
redis 127.0.0.1:6379[1]> SELECT 0
redis 127.0.0.1:6379> MOVE greeting 2
redis 127.0.0.1:6379> SELECT 2
redis 127.0.0.1:6379[2]> GET greeting
"hello"
```

Other useful key commands: `RENAME`, `TYPE` (what kind of value is this?), `DEL`, `FLUSHDB` (empty the current database), `FLUSHALL` (empty all of them).

### Day 1 homework, solved

**Find:** the complete command list at redis.io/commands. Each command's page states its **time complexity** in Big-O notation: `GET` is O(1), `LRANGE` is O(S+N), `ZADD` is O(log N), `SINTER` is O(N×M) in the worst case. Knowing these tells you which commands are safe on huge keys.

**1. Increment a value inside a transaction**, from a driver (Ruby with redis-rb):

```ruby
require 'redis'
redis = Redis.new(host: '127.0.0.1', port: 6379)
redis.set('count', 1)
result = redis.multi do |tx|
  tx.incr('count')
  tx.incr('count')
end
puts result.inspect        # [2, 3]
```

**2. A producer and a consumer on a blocking list:**

```ruby
# consumer.rb: waits forever (timeout 0) for messages
require 'redis'
redis = Redis.new
loop do
  _list, message = redis.brpop('messages', timeout: 0)
  puts "received: #{message}"
end
```

```ruby
# producer.rb
require 'redis'
redis = Redis.new
5.times { |i| redis.lpush('messages', "message #{i}"); sleep 1 }
```

Run the consumer in one terminal and the producer in another: each message prints as it arrives.

## Day 2 · Advanced usage and distribution

### Step 1: The protocol, and pipelining

Redis speaks a simple **text protocol** over TCP, so you can talk to it with `telnet` or `nc`:

```bash
telnet localhost 6379
SET test hello
+OK
GET test
$5
hello
SADD stest 1 99
:2
SMEMBERS stest
*2
$1
1
$2
99
```

The first character of each reply says its type: `+` a status, `-` an error, `:` an integer, `$` a string (followed by its length), `*` a list of replies (followed by the count).

Because commands are just lines of text, a client can send **many commands at once** without waiting for each reply. That is **pipelining**:

```bash
(echo -en "PING\r\nPING\r\nPING\r\n"; sleep 1) | nc localhost 6379
+PONG
+PONG
+PONG
```

:::fig **Why pipelining is faster.** Without it, every command pays a full network round trip. With it, the client sends a batch and reads all the replies afterwards. When the network latency is much bigger than Redis's processing time (it usually is), the speedup is dramatic.
<svg class="dg wide" viewBox="0 0 720 230">
<text x="170" y="20" text-anchor="middle" class="b">one at a time</text>
<rect x="20" y="34" width="70" height="180" rx="8" class="box"/><text x="55" y="128" text-anchor="middle" class="b">client</text>
<rect x="250" y="34" width="70" height="180" rx="8" class="bw"/><text x="285" y="128" text-anchor="middle" class="b">Redis</text>
<g><line x1="92" y1="50" x2="246" y2="64" class="ln" marker-end="url(#arr)"/><line x1="246" y1="74" x2="92" y2="88" class="ln dash" marker-end="url(#arr)"/>
<line x1="92" y1="104" x2="246" y2="118" class="ln" marker-end="url(#arr)"/><line x1="246" y1="128" x2="92" y2="142" class="ln dash" marker-end="url(#arr)"/>
<line x1="92" y1="158" x2="246" y2="172" class="ln" marker-end="url(#arr)"/><line x1="246" y1="182" x2="92" y2="196" class="ln dash" marker-end="url(#arr)"/></g>
<text x="170" y="226" text-anchor="middle" class="s">3 commands = 3 round trips</text>
<line x1="360" y1="20" x2="360" y2="220" class="ln2 dash"/>
<text x="545" y="20" text-anchor="middle" class="b">pipelined</text>
<rect x="400" y="34" width="70" height="180" rx="8" class="box"/><text x="435" y="128" text-anchor="middle" class="b">client</text>
<rect x="630" y="34" width="70" height="180" rx="8" class="bw"/><text x="665" y="128" text-anchor="middle" class="b">Redis</text>
<line x1="472" y1="50" x2="626" y2="64" class="lgr" marker-end="url(#arrg)"/><line x1="472" y1="58" x2="626" y2="72" class="lgr" marker-end="url(#arrg)"/><line x1="472" y1="66" x2="626" y2="80" class="lgr" marker-end="url(#arrg)"/>
<line x1="626" y1="96" x2="472" y2="110" class="lgr dash" marker-end="url(#arrg)"/><line x1="626" y1="104" x2="472" y2="118" class="lgr dash" marker-end="url(#arrg)"/><line x1="626" y1="112" x2="472" y2="126" class="lgr dash" marker-end="url(#arrg)"/>
<text x="545" y="226" text-anchor="middle" class="s">3 commands = about 1 round trip</text>
</svg>
:::

### Step 2: Publish-subscribe

Blocking lists deliver each message to **one** consumer. **Publish-subscribe** (pub/sub) delivers each message to **every** subscriber of a channel, like a radio broadcast.

```text
# terminal 1 and terminal 2: subscribe
redis 127.0.0.1:6379> SUBSCRIBE comments
Reading messages... (press Ctrl-C to quit)
1) "subscribe"
2) "comments"
3) (integer) 1

# terminal 3: publish
redis 127.0.0.1:6379> PUBLISH comments "Check out this shortcoded site! 7wks"
(integer) 2                  # the number of subscribers who received it

# terminals 1 and 2 both print:
1) "message"
2) "comments"
3) "Check out this shortcoded site! 7wks"
```

`UNSUBSCRIBE` stops listening; `PSUBSCRIBE news.*` subscribes to every channel matching a pattern.

:::fig **Queue versus pub/sub.** With a blocking list, each message is taken by exactly one worker: good for sharing work. With pub/sub, each message is copied to every current subscriber: good for broadcasting events. Pub/sub messages are not stored, so a subscriber that is offline misses them.
<svg class="dg wide" viewBox="0 0 720 220">
<text x="170" y="20" text-anchor="middle" class="b">list + BRPOP: one receiver</text>
<rect x="20" y="90" width="80" height="40" rx="8" class="box"/><text x="60" y="115" text-anchor="middle" class="s">producer</text>
<rect x="140" y="90" width="80" height="40" rx="8" class="bw"/><text x="180" y="115" text-anchor="middle" class="s mono">list</text>
<rect x="260" y="40" width="80" height="36" rx="8" class="bg"/><text x="300" y="63" text-anchor="middle" class="s">worker A ✓</text>
<rect x="260" y="92" width="80" height="36" rx="8" class="box"/><text x="300" y="115" text-anchor="middle" class="s">worker B</text>
<rect x="260" y="144" width="80" height="36" rx="8" class="box"/><text x="300" y="167" text-anchor="middle" class="s">worker C</text>
<line x1="100" y1="110" x2="138" y2="110" class="ln" marker-end="url(#arr)"/><line x1="220" y1="104" x2="258" y2="62" class="lgr" marker-end="url(#arrg)"/>
<line x1="360" y1="20" x2="360" y2="210" class="ln2 dash"/>
<text x="545" y="20" text-anchor="middle" class="b">PUBLISH: every subscriber</text>
<rect x="390" y="90" width="80" height="40" rx="8" class="box"/><text x="430" y="115" text-anchor="middle" class="s">publisher</text>
<rect x="510" y="90" width="80" height="40" rx="8" class="bw"/><text x="550" y="115" text-anchor="middle" class="s mono">channel</text>
<rect x="630" y="40" width="80" height="36" rx="8" class="bg"/><text x="670" y="63" text-anchor="middle" class="s">sub 1 ✓</text>
<rect x="630" y="92" width="80" height="36" rx="8" class="bg"/><text x="670" y="115" text-anchor="middle" class="s">sub 2 ✓</text>
<rect x="630" y="144" width="80" height="36" rx="8" class="bg"/><text x="670" y="167" text-anchor="middle" class="s">sub 3 ✓</text>
<line x1="470" y1="110" x2="508" y2="110" class="ln" marker-end="url(#arr)"/>
<line x1="590" y1="104" x2="628" y2="62" class="lgr" marker-end="url(#arrg)"/><line x1="590" y1="110" x2="628" y2="110" class="lgr" marker-end="url(#arrg)"/><line x1="590" y1="116" x2="628" y2="160" class="lgr" marker-end="url(#arrg)"/>
</svg>
:::

### Step 3: Server info and configuration

`INFO` reports the server's version, memory use, connected clients, persistence status, replication role, and statistics. Configuration lives in `redis.conf`, and the book walks through the most important settings.

#### Durability: snapshots and the append-only file

Redis offers two ways to save in-memory data to disk, and you choose how much speed to trade for safety:

| Option | How it works | Risk |
|---|---|---|
| **Snapshots (RDB)** | Every so often, write the whole dataset to `dump.rdb`. `save 900 1` means "if at least 1 key changed in 900 seconds, snapshot"; `save 60 10000` means "if 10,000 keys changed in 60 seconds". `SAVE` (blocking) or `BGSAVE` (in the background) snapshot on demand. | You lose everything since the last snapshot. |
| **Append-only file (AOF)** | `appendonly yes` logs every write command to a file, replayed on restart. | Depends on `appendfsync`. |
| `appendfsync always` | Flush the log to disk after **every** write. | Safest, slowest. |
| `appendfsync everysec` | Flush once per second (the usual choice). | Lose at most about one second. |
| `appendfsync no` | Let the operating system decide when to flush. | Fastest, least safe. |

:::fig **Speed versus durability in Redis.** Moving right, each write is safer and slower. The book's homework measures the difference: the same import with no persistence and with `appendfsync always`.
<svg class="dg wide" viewBox="0 0 720 170">
<line x1="40" y1="70" x2="680" y2="70" class="ln" marker-end="url(#arr)"/>
<text x="40" y="40" class="s">faster</text><text x="680" y="40" text-anchor="end" class="s">safer</text>
<circle cx="80" cy="70" r="9" class="fr"/><text x="80" y="102" text-anchor="middle" class="s b">no saving</text><text x="80" y="118" text-anchor="middle" class="s">pure cache</text>
<circle cx="230" cy="70" r="9" class="fw"/><text x="230" y="102" text-anchor="middle" class="s b">snapshots</text><text x="230" y="118" text-anchor="middle" class="s">lose minutes</text>
<circle cx="390" cy="70" r="9" class="fw"/><text x="390" y="102" text-anchor="middle" class="s b">AOF everysec</text><text x="390" y="118" text-anchor="middle" class="s">lose ~1 second</text>
<circle cx="550" cy="70" r="9" class="fg"/><text x="550" y="102" text-anchor="middle" class="s b">AOF always</text><text x="550" y="118" text-anchor="middle" class="s">lose ~nothing</text>
<circle cx="650" cy="70" r="9" class="fg"/><text x="650" y="102" text-anchor="middle" class="s b">+ replicas</text><text x="650" y="118" text-anchor="middle" class="s">survive a dead disk</text>
</svg>
:::

#### Security

Redis was designed for trusted networks. `requirepass` in `redis.conf` sets a password that clients send with `AUTH`. To stop anyone from running dangerous commands, the book shows `rename-command`, which renames a command to something unguessable (or to an empty string to disable it):

```text
rename-command FLUSHALL c283d93ac9528f986023793b411e4ba2
```

After that, `FLUSHALL` returns an error, and only someone who knows the new name can wipe the server.

#### Benchmarking

```bash
redis-benchmark -n 100000
# ====== PING (inline) ======
#   100000 requests completed in 3.05 seconds
#   50 parallel clients
#   3 bytes payload
#   keep alive: 1
# ...
# 32808.40 requests per second
# … then SET, GET, INCR, LPUSH, SADD, LRANGE and more
```

By default the benchmark sends 10,000 requests from 50 parallel clients; `-n` changes the number of requests. These are the book's 2012 laptop numbers; modern hardware does far more.

### Step 4: Master-slave replication

Redis can **replicate** a master to any number of **slaves** (read-only copies). Copy the config, change the port, and point it at the master:

```bash
cp redis.conf redis-s1.conf
# in redis-s1.conf:
#   port 6380
#   slaveof 127.0.0.1 6379
redis-server redis-s1.conf
```

```text
redis 127.0.0.1:6379> SADD meetings "StarTrek Pastry Chefs" "LARPers Intl."
redis 127.0.0.1:6380> SMEMBERS meetings
1) "StarTrek Pastry Chefs"
2) "LARPers Intl."
```

Replication gives you **read scaling** (spread reads over slaves) and **durability** (a second copy on another machine) without paying for `appendfsync always` on the master.

### Step 5: Loading lots of data, and sharding

The book loads a large file of **book titles keyed by ISBN** to compare techniques:

```ruby
# isbn.rb: one SET per line
require 'redis'
LIMIT = 1.0 / 0     # infinity in Ruby: no limit
$redis = Redis.new(:host => "127.0.0.1", :port => 6379)
$redis.flushall
count, start = 0, Time.now
File.open(ARGV[0]).each do |line|
  count += 1
  next if count == 1
  isbn, _, _, title = line.split("\t")
  next if isbn.empty? || title == "\n"
  $redis.set(isbn, title.strip)
  break if count >= LIMIT
end
puts "#{count} items in #{Time.now - start} seconds"
```

Three speedups, in order:

1. **Pipelining** (`isbn_pipelined.rb`): wrap batches of 10,000 SETs in `$redis.pipelined do … end`, so each batch is one network round trip.
2. **The hiredis driver**: a C library that parses Redis replies much faster than pure Ruby (`gem install hiredis`, then `Redis.new(:driver => :hiredis)`).
3. **Sharding across servers** (`isbn_cluster.rb`): the 2012 Redis had no built-in clustering, but the Ruby client could spread keys over several servers itself with `Redis::Distributed`, using consistent hashing (the same ring idea as Riak):

```ruby
require 'redis/distributed'
$redis = Redis::Distributed.new([
  "redis://localhost:6379/",
  "redis://localhost:6380/"
])
```

:::fig **Client-side sharding.** The Redis servers don't know about each other. The client library hashes each key to pick a server, so each server holds part of the data. Multi-key operations (like SINTER across servers) no longer work, because the keys may live on different machines.
<svg class="dg wide" viewBox="0 0 720 200">
<rect x="10" y="70" width="190" height="60" rx="10" class="box"/><text x="105" y="94" text-anchor="middle" class="b">Ruby client</text><text x="105" y="114" text-anchor="middle" class="s mono">Redis::Distributed</text>
<rect x="250" y="80" width="130" height="40" rx="8" class="bv"/><text x="315" y="105" text-anchor="middle" class="s">hash(key) → server</text>
<line x1="200" y1="100" x2="248" y2="100" class="ln" marker-end="url(#arr)"/>
<line x1="382" y1="92" x2="478" y2="52" class="ln" marker-end="url(#arr)"/><line x1="382" y1="108" x2="478" y2="148" class="ln" marker-end="url(#arr)"/>
<rect x="482" y="24" width="228" height="56" rx="10" class="bw"/><text x="596" y="48" text-anchor="middle" class="b">Redis :6379</text><text x="596" y="66" text-anchor="middle" class="s">ISBNs that hash here</text>
<rect x="482" y="120" width="228" height="56" rx="10" class="bw"/><text x="596" y="144" text-anchor="middle" class="b">Redis :6380</text><text x="596" y="162" text-anchor="middle" class="s">ISBNs that hash here</text>
</svg>
:::

### Step 6: Bloom filters and bits

The book's final Day 2 trick is a **Bloom filter** stored in Redis (you met Bloom filters in the HBase chapter): a compact way to answer "have I **definitely not** seen this before?" The `bloomfilter-rb` gem keeps its bit array in a Redis string, using two commands that treat a string as an array of bits:

```text
# toppings as bit positions: ketchup = 0, mustard = 1, onion = 2, lettuce = 3
redis 127.0.0.1:6379> SETBIT my_burger 1 1      # mustard
(integer) 0
redis 127.0.0.1:6379> SETBIT my_burger 2 1      # onion
(integer) 0
redis 127.0.0.1:6379> GETBIT my_burger 3        # lettuce?
(integer) 0
redis 127.0.0.1:6379> GETBIT my_burger 1        # mustard?
(integer) 1
```

:::fig **A string as a bit array.** The book's burger has mustard and onion, so bits 1 and 2 are set (the first four bits read 0110). SETBIT and GETBIT address single bits by position. One byte stores eight yes/no facts, so a million flags take only about 125 KB. Bloom filters, "has this user seen this item?" flags and daily activity tracking all use this trick.
<svg class="dg" viewBox="0 0 720 150">
<text x="20" y="30" class="b mono">my_burger</text>
<g class="mono">
<rect x="140" y="12" width="56" height="40" class="box"/><text x="168" y="38" text-anchor="middle">0</text>
<rect x="196" y="12" width="56" height="40" class="bw"/><text x="224" y="38" text-anchor="middle" class="b">1</text>
<rect x="252" y="12" width="56" height="40" class="bw"/><text x="280" y="38" text-anchor="middle" class="b">1</text>
<rect x="308" y="12" width="56" height="40" class="box"/><text x="336" y="38" text-anchor="middle">0</text>
<rect x="364" y="12" width="56" height="40" class="box"/><text x="392" y="38" text-anchor="middle">0</text>
<rect x="420" y="12" width="56" height="40" class="box"/><text x="448" y="38" text-anchor="middle">0</text>
<rect x="476" y="12" width="56" height="40" class="box"/><text x="504" y="38" text-anchor="middle">0</text>
<rect x="532" y="12" width="56" height="40" class="box"/><text x="560" y="38" text-anchor="middle">0</text>
</g>
<g class="s"><text x="168" y="72" text-anchor="middle">0</text><text x="224" y="72" text-anchor="middle">1</text><text x="280" y="72" text-anchor="middle">2</text><text x="336" y="72" text-anchor="middle">3</text><text x="392" y="72" text-anchor="middle">4</text><text x="448" y="72" text-anchor="middle">5</text><text x="504" y="72" text-anchor="middle">6</text><text x="560" y="72" text-anchor="middle">7</text></g>
<text x="168" y="100" text-anchor="middle" class="s">ketchup</text><text x="224" y="100" text-anchor="middle" class="s tw b">mustard</text><text x="280" y="100" text-anchor="middle" class="s tw b">onion</text><text x="336" y="100" text-anchor="middle" class="s">lettuce</text>
<text x="360" y="136" text-anchor="middle" class="s">bit position (one byte shown)</text>
</svg>
:::

The book's script, `isbn_bf.rb`, adds every word of every book title to a Redis-backed Bloom filter and prints only words it has **not** seen before. Because a Bloom filter never gives a false "not seen", each printed word really is new (a few genuinely new words may be skipped due to false positives).

```ruby
require 'bloomfilter-rb'
bloomfilter = BloomFilter::Redis.new(:size => 1000000)
bloomfilter.clear
# for each word in each title:
#   unless bloomfilter.include?(word) then puts word; bloomfilter.insert(word) end
```

### Day 2 homework, solved

**Find: messaging patterns.** Classic patterns (from *Enterprise Integration Patterns*) and how Redis does them: **point-to-point queue** (lists with `LPUSH` + `BRPOP`), **reliable queue** (`BRPOPLPUSH` into a "processing" list, removed when done), **publish-subscribe** (`PUBLISH`/`SUBSCRIBE`), **pattern subscriptions** (`PSUBSCRIBE`), **priority queue** (sorted set by priority, popped with `ZRANGE` + `ZREM` in a transaction), **delayed jobs** (sorted set scored by run-at time) and **request-reply** (the requester waits with BRPOP on a private reply list).

**Do 1. Compare durability settings.** Run the ISBN import twice, timing each:

```text
# run 1, in redis.conf: comment out every "save" line and set   appendonly no
# run 2: set   appendonly yes   and   appendfsync always
```

The `always` run is several times slower, because every single SET waits for a disk flush.

**Do 2. A URL shortener backed by Redis**, in Ruby with Sinatra. Writes go to the master and reads can go to a slave:

```ruby
require 'sinatra'
require 'redis'
MASTER = Redis.new(port: 6379)
REPLICA = Redis.new(port: 6380)       # started with: slaveof 127.0.0.1 6379

get '/' do
  '<form method="post" action="/"><input name="url"><button>Shorten</button></form>'
end

post '/' do
  code = MASTER.incr('url:next_id').to_s(36)       # 1, 2, … a, b, … 10, 11 …
  MASTER.set("url:#{code}", params[:url])
  "Short link: <a href='/#{code}'>/#{code}</a>"
end

get '/:code' do
  url = REPLICA.get("url:#{params[:code]}") || MASTER.get("url:#{params[:code]}")
  url ? redirect(url) : halt(404, 'Unknown link')
end
```

`INCR` guarantees a unique code even with many web servers, and base-36 keeps codes short. The fallback to the master handles a new link that has not yet reached the slave.

## Day 3 · Playing with other databases

Day 3 is the book's grand finale: a small **polyglot persistence** application where Redis, **CouchDB** and **Neo4J** each do what they do best. The data is from **Freebase**'s `group_membership` file: over 100,000 band members of more than 30,000 bands, with the roles each artist played (lead vocals, drums, keytar…).

### Step 1: Who does what

| Database | Role in the system |
|---|---|
| **CouchDB** | The **system of record** (SOR): the authoritative copy. One document per band, with its artists and their roles nested inside. Its Changes API keeps the other databases in sync. |
| **Neo4J** | The **relationship store**: bands, artists and roles as a graph, for questions like "which other bands did this band's members play in?" |
| **Redis** | The helper, in **three** jobs: a staging area while loading data into CouchDB, a **cache** for the Neo4J client, and a fast **lookup** for partial name searches (autocomplete). |

:::fig **The polyglot band service.** Data flows from the raw file through Redis into CouchDB, the system of record. A sync process follows CouchDB's Changes API and updates Neo4J and Redis. The web application reads from all three: Redis for search, CouchDB for band details, Neo4J for connections between bands.
<svg class="dg wide" viewBox="0 0 720 340">
<rect x="10" y="20" width="130" height="50" rx="8" class="box"/><text x="75" y="42" text-anchor="middle" class="b">group_</text><text x="75" y="58" text-anchor="middle" class="b">membership.tsv</text>
<line x1="142" y1="45" x2="196" y2="45" class="ln" marker-end="url(#arr)"/><text x="169" y="36" text-anchor="middle" class="s">1</text>
<rect x="200" y="20" width="150" height="50" rx="8" class="bw"/><text x="275" y="42" text-anchor="middle" class="b">Redis</text><text x="275" y="58" text-anchor="middle" class="s">band:* artist:* sets</text>
<line x1="352" y1="45" x2="426" y2="45" class="ln" marker-end="url(#arr)"/><text x="389" y="36" text-anchor="middle" class="s">2</text>
<rect x="430" y="10" width="170" height="70" rx="10" class="bg"/><text x="515" y="36" text-anchor="middle" class="b">CouchDB</text><text x="515" y="54" text-anchor="middle" class="s">system of record</text><text x="515" y="70" text-anchor="middle" class="s mono">bands/Skillet …</text>
<line x1="515" y1="82" x2="515" y2="128" class="lgr" marker-end="url(#arrg)"/><text x="525" y="110" class="s tg">3. _changes</text>
<rect x="430" y="132" width="170" height="50" rx="8" class="box"/><text x="515" y="154" text-anchor="middle" class="b mono">graph_sync.js</text><text x="515" y="172" text-anchor="middle" class="s">Node.js</text>
<line x1="430" y1="166" x2="356" y2="210" class="ln" marker-end="url(#arr)"/><line x1="600" y1="166" x2="640" y2="210" class="ln" marker-end="url(#arr)"/>
<rect x="200" y="212" width="150" height="56" rx="8" class="bw"/><text x="275" y="234" text-anchor="middle" class="b">Redis</text><text x="275" y="252" text-anchor="middle" class="s mono">band-name:* keys</text>
<rect x="560" y="212" width="150" height="56" rx="8" class="bp"/><text x="635" y="234" text-anchor="middle" class="b">Neo4J</text><text x="635" y="252" text-anchor="middle" class="s">bands–artists graph</text>
<rect x="250" y="292" width="300" height="40" rx="8" class="ba"/><text x="400" y="317" text-anchor="middle" class="b mono">band.js web app</text>
<line x1="300" y1="290" x2="285" y2="270" class="ln dash" marker-end="url(#arr)"/><text x="248" y="290" class="s">search</text>
<line x1="500" y1="290" x2="610" y2="270" class="ln dash" marker-end="url(#arr)"/><text x="566" y="296" class="s">related bands</text>
<path d="M410,290 C410,200 370,120 470,82" class="ln dash" marker-end="url(#arr)"/><text x="418" y="204" class="s">band details</text>
</svg>
:::

### Step 2: Populating Redis, then CouchDB

The first Node.js script, `pre_populate.js`, reads the TSV file line by line and builds sets in Redis:

```javascript
// for each line of the file: artist, band, roles
redis_client.sadd('band:' + band, artist);
roles.forEach(function(role) {
  redis_client.sadd('artist:' + band + ':' + artist, role);
});
```

So `band:Beatles` holds `{John Lennon, Paul McCartney, George Harrison, Ringo Starr}`, and `artist:Beatles:Ringo Starr` holds `{Drums}`.

Why not write straight to CouchDB? The file has **one line per band member**, so the same band appears on many lines. Writing each line to CouchDB would update the same band document over and over, and concurrent updates would keep hitting CouchDB's revision check (**update thrashing**, 409 Conflicts). Redis sets gather everything for a band in one fast pass; then `populate_couch.js` creates **one complete document per band**:

```javascript
redisClient.keys('band:*', function(error, bandKeys) {
  bandKeys.forEach(function(bandKey) {
    var bandName = bandKey.substring(5);          // strip "band:"
    redisClient.smembers(bandKey, function(error, artists) {
      // fetch every artist's roles in one MULTI batch, then
      // PUT http://localhost:5984/bands/<bandName> with:
      // { name: bandName, artists: [ { name: …, role: [ … ] }, … ] }
    });
  });
});
```

The resulting CouchDB document looks like:

```json
{
  "_id": "Skillet",
  "name": "Skillet",
  "artists": [
    { "name": "John Cooper", "role": ["Acoustic guitar", "Lead vocalist", "Bass"] },
    …
    { "name": "Korey Cooper", "role": ["backing vocals", "Synthesizer", "Guitar", "Keyboard instrument"] }
  ]
}
```

The catch the book mentions: Redis must hold the **whole dataset in RAM** during the import.

### Step 3: Keeping Neo4J and Redis in sync

`graph_sync.js` follows CouchDB's **Changes API** (Chapter 6). Because it starts from sequence 0, its first run also processes every existing band, so no separate Neo4J import is needed. For each changed band document it:

1. **Feeds Redis** with lookup keys:

```javascript
function feedBandToRedis(band) {
  redisClient.set('band-name:' + band.name, 1);
  band.artists.forEach(function(artist) {
    redisClient.set('artist-name:' + artist.name, 1);
    artist.role.forEach(function(role){
      redisClient.set('role-name:' + role, 1);
    });
  });
}
```

Now `KEYS band-name:Bea*` finds every band starting with "Bea": instant autocomplete.

2. **Feeds Neo4J** with nodes and relationships: one node per band, artist and role; `member` relationships from bands to artists and `plays` relationships from artists to roles. The book's `neo4j_caching_client.js` driver remembers in **Redis** which nodes already exist, so it does not have to ask Neo4J every time.

As long as `graph_sync.js` runs, any change to a band in CouchDB (a new member, a new role) appears in Neo4J and Redis within moments.

### Step 4: The web application

The last piece, `band.js`, is a small Node.js web server (using the `bricks` web framework and `mustache` templates) with three pages:

- **Search box** with autocomplete: `GET /search?term=Bea` asks Redis for `band-name:Bea*` keys.
- **Band page** `GET /band?name=Nirvana`: the members and their roles come from **CouchDB**; "other bands these members played in" comes from **Neo4J**:

```groovy
g.V.filter{it.name=="Nirvana"}.out("member").in("member").dedup.name
```

- **Artist page**: the artist's roles and bands, also from Neo4J.

:::deep Why not just use one database?
Each question in this app is easy for one database and awkward for the others. "Members of Nirvana" is one document read in CouchDB. "Bands sharing a member with Nirvana" is a two-hop traversal in Neo4J, but a scan over all documents in CouchDB. "Band names starting with Bea, right now, as the user types" needs microsecond lookups, which is Redis's specialty. Polyglot persistence pays the cost of running and syncing three systems to make each question cheap. Notice the design choice that keeps it manageable: **one** database is the source of truth, and the others are derived from it and can be rebuilt.
:::

### Going further: extra exercises

The book ends Day 3 without homework, since the whole day is a project. Here are three natural extensions, with solutions:

**1. Show the roles an artist played in each band** on the artist page. In Neo4J, store the roles on the `member` relationship (or as `plays` edges from a "membership" node) and query with Gremlin:

```groovy
g.V.filter{it.name=="Dave Grohl"}.outE("plays").transform{ [it.inV.name.next()] }
```

**2. Handle deletions.** When a band document is deleted in CouchDB, the `_changes` entry has `"deleted": true`. In `graph_sync.js`, check that flag and remove the band's `band-name:` key from Redis and its node (with its relationships) from Neo4J through the REST API (`DELETE /db/data/node/<id>` after deleting its relationships).

**3. Faster autocomplete without KEYS.** Store every band name in one **sorted set** with score 0 (so members sort alphabetically), then fetch a prefix range:

```text
ZADD band-names 0 "beach boys" 0 "beatles" 0 "beck"
ZRANGEBYLEX band-names "[bea" "[bea\xff" LIMIT 0 10
```

(`ZRANGEBYLEX` arrived in Redis 2.8.9. In 2012 the equivalent trick was to store every prefix of every name.)

## Wrap-up · Strengths and weaknesses

The book's summary: Redis is light, compact and good for an odd variety of tasks. Above all it is **fast, simple, and as durable as you choose**. It is rarely a stand-alone database, but it is a perfect companion in any polyglot system: transforming data, caching requests, or passing messages with its blocking commands.

### Strengths

- **Speed**, as with most key-value stores, and more.
- **Complex values**: lists, hashes, sets and sorted sets, each with its own server-side operations.
- **Tunable durability**, from "pure cache" to "flush on every write", with fine control in between.
- **Built-in master-slave replication**, for both safety and read-heavy workloads.

### Weaknesses

- **It lives in memory.** Some call that cheating: a database that never waits for the disk will be fast. Shut down before a snapshot and you lose data. Even with `appendfsync always`, expiry times can't be guaranteed to replay exactly.
- **The dataset must fit in RAM** (Redis was dropping its virtual-memory feature at the time).
- **No built-in clustering** in 2012: Redis Cluster was "in development", so sharding meant client-side tools like the Ruby driver's `Redis::Distributed`.

### Parting thoughts

Redis has more than 120 commands, most easy to understand from their names once you get used to the abbreviations (`INCRBY`, `ZCOUNT` for "sorted set count", `SCARD` for "set cardinality"). It was already part of many systems in 2012, such as the Resque job queue and session management in SocketStream. The authors' final advice: **whatever database you choose as your system of record, add Redis to the mix.**

:::modern Redis in 2026
- **Clustering and failover arrived.** **Redis Sentinel** (2.8) monitors a master and promotes a replica automatically when it fails. **Redis Cluster** (3.0, 2015) shards data across up to 1,000 nodes using **16,384 hash slots**, with replicas and failover built in, so client-side sharding is no longer needed.
- **New data types and features:** **Lua scripting** (`EVAL`, 2.6) for atomic custom operations; bit commands like `BITCOUNT`/`BITOP`; **HyperLogLog** (approximate counting); **geospatial** commands; **Streams** (5.0), a persistent, replayable log with consumer groups, which fixes pub/sub's "offline subscribers miss messages" problem; client-side caching, ACLs and TLS (6.0).
- **Modules** (4.0) added JSON documents, full-text and vector search, time series and **probabilistic structures including Bloom filters**, now bundled with Redis itself (Redis 8).
- **Renamed commands:** "slave" became **"replica"** (`REPLICAOF`, 5.0); `HMSET` is replaced by multi-field `HSET`; `SETEX` is usually written `SET key value EX 10`. Use `SCAN` instead of `KEYS` in production, because `KEYS` blocks the server while it walks every key.
- **Licensing and a fork.** In 2024 Redis moved from the BSD licence to source-available licences (RSAL/SSPL). In response, the Linux Foundation launched **Valkey**, an open-source fork backed by major cloud providers. In 2025 Redis 8 added the open-source AGPL as a licence option. Today you may run Redis, Valkey, or a managed service (Amazon ElastiCache/MemoryDB, Google Memorystore, Azure, Redis Cloud).
- **The Day 3 code** used 2012 Node.js libraries; modern Node uses promise-based clients (`node-redis` v4+, `ioredis`), `fetch`, and frameworks like Express.
:::

:::key Chapter 8 in a nutshell
- **Redis** is an in-memory key-value store whose values are **data structures**, manipulated atomically by server-side commands.
- **Day 1:** strings and counters (`SET`, `GET`, `INCR`), `MULTI`/`EXEC`, hashes (`HSET`, `HGET`), lists (`RPUSH`, `LPOP`, `RPOPLPUSH`, blocking `BRPOP` queues), sets (`SINTER`, `SDIFF`, `SUNION`), sorted sets (`ZADD`, `ZRANGEBYSCORE`, `ZUNIONSTORE … WEIGHTS`), expiry (`EXPIRE`, `TTL`), numbered databases.
- **Day 2:** the text protocol and pipelining; pub/sub; snapshots vs. append-only file and `appendfsync`; passwords and `rename-command`; master-slave replication; pipelined bulk loads, hiredis and client-side sharding; `SETBIT`/`GETBIT` and Bloom filters.
- **Day 3:** a polyglot app: CouchDB as the system of record, Neo4J for relationships, Redis for staging, caching and autocomplete, kept in sync with the Changes API.
- **Choose it** as a cache, queue, session store, leaderboard or real-time helper. **Not** as the only home of data you cannot afford to lose, or data larger than memory.
:::

@@quiz
Q: Why can a thousand clients run `INCR count` at the same moment without losing any increments?
- Redis locks the key for each client
+ Redis executes commands one at a time on a single thread, so each INCR is atomic
- Redis retries failed increments automatically
- INCR is queued and applied once a minute
? Redis processes one command at a time, so no command sees another half-finished. Server-side operations like INCR need no extra locking.

Q: Inside `MULTI` … `EXEC`, one queued command fails. What happens to the others?
- They are all rolled back
+ The others still run; Redis transactions guarantee isolation and order, not rollback
- Redis retries the failed command until it succeeds
- The whole server restarts
? MULTI/EXEC runs the batch together without interruption. It does not undo successful commands when another one fails.

Q: Which data type would you choose for a game leaderboard that must return the top 10 players by score?
- A list
- A hash
- A set
+ A sorted set
? Sorted sets keep members ordered by score. `ZREVRANGE leaderboard 0 9 WITHSCORES` returns the top 10 directly, and `ZINCRBY` updates scores atomically.

Q: What makes `RPOPLPUSH` useful for job queues?
- It is faster than LPOP
+ It moves an item from one list to another in a single atomic step, so a job is never lost between the two lists
- It deletes duplicate jobs
- It blocks until a job arrives
? A worker can move a job into an "in progress" list atomically. If the worker crashes, the job is still in that list and can be retried. (BRPOPLPUSH is the blocking version.)

Q: Given visits = {gog: 9, 7wks: 500} and votes = {gog: 0, 7wks: 2}, what is 7wks's score after this command?
C: ZUNIONSTORE importance 2 visits votes WEIGHTS 1 2 AGGREGATE SUM
- 502
+ 504
- 1004
- 1000
? Weighted sum: 500 × 1 + 2 × 2 = 504.

Q: What does `EXPIRE ice 10` do?
- Waits 10 seconds before setting the key
+ Makes Redis delete the key `ice` automatically after 10 seconds
- Keeps only the 10 most recent values of `ice`
- Blocks reads of `ice` for 10 seconds
? EXPIRE sets a time to live. TTL shows the seconds remaining, and PERSIST removes the expiry.

Q: Why does pipelining speed up bulk loads so much?
- It compresses the commands
- It skips writing to disk
+ The client sends many commands without waiting for each reply, so a batch costs about one network round trip instead of one per command
- It runs commands on several CPU cores
? Redis itself is very fast; network round trips dominate. Pipelining removes most of them.

Q: How does pub/sub differ from a blocking list?
+ A published message goes to every current subscriber; a list item is taken by exactly one consumer
- Pub/sub stores messages until they are read; lists don't
- Lists can only hold numbers
- There is no difference
? PUBLISH broadcasts to all subscribers (and nothing is stored for offline ones). A list with BRPOP delivers each item to one worker.

Q: Which durability setting loses at most about one second of writes in a crash, while staying fast?
- Snapshots only, every 15 minutes
+ `appendonly yes` with `appendfsync everysec`
- `appendfsync always`
- No persistence at all
? Flushing the append-only file once per second is the common compromise. `always` is safer but much slower; snapshots can lose minutes.

Q: In the Day 3 polyglot application, which database is the system of record?
- Redis
+ CouchDB
- Neo4J
- PostgreSQL
? CouchDB holds the authoritative band documents. Neo4J and Redis are derived from it through the Changes API and could be rebuilt.

Q: Why did the book load the band data into Redis before CouchDB?
- CouchDB cannot read TSV files
+ The file has one line per band member; gathering members in Redis sets first allows one complete document per band, avoiding repeated updates and revision conflicts in CouchDB
- Redis compresses the data
- Neo4J requires it
? Writing each line directly would update the same band document many times, causing update thrashing against CouchDB's revision checks.

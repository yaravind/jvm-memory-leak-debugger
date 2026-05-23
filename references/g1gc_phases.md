# G1 GC Phase Guide

The skill focuses on leak evidence rather than tuning first. These G1 signals
are the most important when reading generated reports.

| Signal | Meaning | Typical interpretation |
| --- | --- | --- |
| Young GC | Evacuates live objects from young regions | Normal unless pauses grow with live set |
| Concurrent Mark Cycle | Finds live old-generation objects | Frequent aborts can indicate heavy allocation pressure |
| To-space exhausted | G1 could not evacuate live objects into free regions | Strong precursor to Full GC cascades |
| Full GC | Stop-the-world compaction of the heap | Repeated Full GCs that free little memory indicate near-total retention |
| Humongous regions | Large objects allocated directly into old regions | Can fragment heap or reveal oversized buffers |
| Live-set drift | Old/live heap rises across cycles | Suggests retained objects are accumulating |

High-confidence leak shape:

1. Old/live heap grows steadily.
2. Young collections begin reporting To-space exhaustion.
3. Full GCs repeat.
4. Full GCs reclaim little or no heap.
5. The heap dump timestamp falls inside or immediately after the storm.

Mitigation order:

1. Reduce the retained live set by fixing the object graph.
2. Bound batching, caches, maps, queues, builders, and request accumulation.
3. Increase heap only as a temporary safety margin while the retention source is
   being fixed.

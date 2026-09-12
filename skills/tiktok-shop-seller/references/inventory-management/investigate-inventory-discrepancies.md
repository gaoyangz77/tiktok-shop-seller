# Investigate inventory discrepancies

1. Define the two values being compared: source, timestamp, shop, product/SKU,
   warehouse, unit and quantity type.
2. Re-read live platform stock and relevant analysis. For FBT use exposed inventory
   records, goods and inbound-order queries to investigate movements.
3. Check reservations, asynchronous receipts, returns, warehouse mappings and stale
   snapshots before concluding there is an error. Do not combine different ledgers
   as though they measure the same quantity.
4. If evidence is incomplete, report the gap and request the warehouse/source record.
   A 403, unsupported region or incomplete page is not zero stock.
5. Correct platform inventory only if the merchant authorizes exact quantities
   supported by a trustworthy physical/warehouse source. Never copy a stale local
   number to the platform solely to make them match.
6. Verify the current quantity and explain what was established versus hypothesized.

Keep investigation notes only if requested, with source/timestamp. They are not
the authoritative ongoing inventory record.

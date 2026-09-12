# Assess stock and replenishment

Goal: identify genuine availability risks, not create a local stock ledger.

1. Confirm products, variants, warehouses and requested horizon.
2. Read current stock/analysis, sales performance and available warehouse information.
   Distinguish ordinary fulfillment from FBT. Use available FBT inventory/goods/
   inbound-order reads only where authorized.
3. Compare like-for-like units and time windows. Available, reserved, inbound and
   damaged quantities are not interchangeable. Missing data is unknown, not zero.
4. Use the merchant's actual lead-time and service targets when estimating risk.
   If they are absent, provide a scenario or ask; do not invent a replenishment policy.
5. Recommend actions with evidence and uncertainty. A recommendation is not an FBT
   inbound order or a warehouse instruction. Warehouse execution/FBT inbound writes
   are not assumed MCP capabilities.
6. Use `ecom_update_inventory` only for a separately authorized exact SKU/warehouse
   correction grounded in authoritative physical/warehouse evidence. Check whether
   the API expects an absolute quantity or delta, and read back afterward.

FBT page tokens stay in session memory; fetch further pages only as needed.
Don't sum incomplete pages into a claimed full total. No automatic full-store sync.

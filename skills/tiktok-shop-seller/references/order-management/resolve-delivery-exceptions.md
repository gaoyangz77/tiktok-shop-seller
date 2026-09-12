# Resolve delivery exceptions

Shared by buyer customer service and creator/sample workflows. Goal: establish
what happened and take a supported, authorized remedy.

1. Identify the exact order/package and shop. For a creator sample, resolve the
   application/collaboration to a real shipping record; do not assume a buyer-order
   ID can be substituted for a sample shipment.
2. Fetch current order/package/tracking context using exposed shared tools.
   Inspect the latest carrier event, shipping address access where permitted,
   tracking number/provider and platform status.
3. Distinguish no pickup, transit delay, failed delivery, delivered-but-not-received,
   and incorrect tracking data. Ask for missing warehouse evidence when needed.
4. If a verified tracking correction is requested, use tracking validation and
   the order/package shipping-info update tools as appropriate. Do not invent a
   tracking number or rewrite it simply to make status appear delivered.
5. If a replacement is needed, first establish merchant approval, stock and the
   correct fulfillment route. **Actual warehouse dispatch, reshipment execution,
   split/merge packages and FBT inbound writes are not assumed available.**
   Without an exposed supported execution tool, report the warehouse/Seller Center
   handoff needed; do not claim that a replacement has shipped.
6. Return the findings/remedy status to the calling customer-service or Affiliate
   workflow, which owns the recipient-facing reply and its idempotency.

Verify any correction by re-reading. Do not confuse tracking validation with proof
of delivery or a shipping-label query with a newly dispatched parcel.

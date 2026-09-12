# Resolve listing issues

1. Identify affected products and read current status plus
   `ecom_get_product_diagnoses` where available.
2. Separate missing facts, content errors, platform restrictions and permissions.
   Ask for genuine missing evidence; do not fabricate compliance documents or claims.
3. Propose the smallest remedy. `ecom_diagnose_and_optimize_product` may change
   content/state; it is not a read-only substitute for diagnosis. Inspect its schema
   and obtain the authorization needed for the actual effect.
4. Apply an authorized correction through [revise listings](revise-listings.md).
5. Re-read status/diagnoses and distinguish submitted, under review, rejected and
   live. A task ID can stay in session memory. Check it only through an exposed
   supported capability; do not start polling indefinitely or persist a local pipeline.

Report unresolved platform requirements and permission/region errors explicitly.

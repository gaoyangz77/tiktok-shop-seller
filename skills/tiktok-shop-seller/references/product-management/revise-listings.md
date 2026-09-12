# Revise listings, prices or availability

1. Resolve exact shop/product/variants and fetch their current values.
2. Determine the narrow requested change: price, content, activation/deactivation,
   recovery, inventory or deletion. Read category rules when changing constrained
   attributes; route stock operations to inventory management.
3. Form a change preview with old/new values and affected IDs. Do not copy unchanged
   platform data into a permanent local file.
4. Prefer a supported partial edit for narrow content changes. A full edit can
   overwrite fields: construct it from a fresh complete read and preserve unrelated
   fields; stop if the required representation cannot be read safely.
5. For price changes verify currency and variant coverage. For status changes verify
   eligibility. Deletion is not deactivation; resolve any ambiguity before acting.
6. Execute using current schemas for `ecom_partial_edit_product`,
   `ecom_edit_product`, `ecom_update_product_price` or the appropriate status tool.
   Do not infer missing/omitted/null field semantics.
7. Read back changed fields and report individual failures. On uncertain responses
   reconcile current state before retrying; never assume batch operations are atomic.

A saved draft is a proposal tied to a read time/revision, not the current listing.
A concurrent platform edit requires re-reading and re-evaluating the proposal.

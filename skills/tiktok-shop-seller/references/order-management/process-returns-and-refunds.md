# Process returns and refunds

1. Resolve the order/items and current return/refund/cancellation request.
   Use exposed searches, records and rejection-reason queries as needed.
2. Read relevant price details to distinguish buyer payment, discounts, shipping,
   refund eligibility and already-refunded amounts. Preserve currency/units.
3. Apply merchant-approved limits and current platform eligibility. If the amount,
   affected items, reason or authority is unclear, ask before a money-moving action.
4. Use `ecom_approve_return` or `ecom_approve_refund` only for the authorized
   operation. Approving a return and issuing a refund are not interchangeable.
   A rejection-reasons query does not imply an exposed rejection mutation exists.
5. Check current status immediately before acting; another operator may have acted.
   After a timeout, reconcile request/refund records before retrying.
6. Verify the resulting state and communicate accurately through the caller's
   customer-service workflow. Accepted/submitted is not necessarily settled.

Do not implement a local refund ledger, promise unsupported remedies, or bypass a
missing MCP operation with an authenticated private API.

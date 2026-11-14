# Manage Product Knowledge

Goal: keep TK Copilot's published Product Knowledge accurate, so creators and
buyers get the merchant's own facts. Product Knowledge holds what the listing
does not: how to use the product, approved answers to common questions, and
creative examples that worked. It is read by the Affiliate workflow when
explaining products to creators.

## Read

- `ecom_get_product_knowledge` with no arguments lists records (summaries only:
  Markdown sections come back null; use the character counts to see which
  sections have content).
- Read one record by `id`, `merchantPid`, or `shopId` + `productId` together.
  Request only the `sections` you need (`USAGE_INSTRUCTIONS`, `QA`,
  `CREATIVE_CASES`).

## Write

1. Gather the merchant's material: manuals, approved Q&A, videos that worked.
   Local files in `knowledge/products/` are sources, not the published version.
2. Draft the change and show it to the merchant. Record only what the merchant
   stated or what the shop's own catalogue verifies. Never invent efficacy,
   safety, compatibility, ingredient or certification claims.
3. Re-read the record right before writing and pass its `revision` as
   `expectedRevision` to `ecom_set_product_knowledge`. Omit `id` to create a
   record (then `name` is required).
4. Omitted sections stay unchanged; an empty string clears a section. Keep every
   `media://…` reference exactly as it is. Images and videos can only be added in
   the TK Copilot app; this agent cannot upload them.
5. `PRODUCT_KNOWLEDGE_REVISION_STALE` means someone changed the record after your
   read and nothing was written. Re-read, re-apply the merchant's change on top of
   the current text, and write again. Never resend the old payload.

## Link to products

Use `bindProducts` / `unbindProducts`. When the merchant names Seller SKUs,
resolve them with `ecom_search_products` (all SKUs in one comma-separated
`sellerSku`, no `shopIds`, so every shop is searched) and bind each returned
shop and product. A product can belong to only one record; conflicts come back
in `linkFailures` with the other record's id. Report SKUs that matched nothing.

Read the final state, `unboundCount` and `linkFailures` from the result before
reporting success. After publishing, archive or clearly mark the local draft so
the published record stays the single authority.

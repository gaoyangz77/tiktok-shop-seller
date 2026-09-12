# Plan and run outreach

Goal: translate merchant intent into a backend campaign, not a local scheduling loop.

1. Read the brief in STORE.md or a selected local campaign draft: products, intended
   creator segment, sample budget, commission constraints, excluded claims and goals.
   Missing commercial decisions require merchant input; no category/region defaults.
2. Fetch live products, availability and relevant existing collaborations/campaign
   context exposed by the tools. Distinguish an aspirational budget from an
   authorized spend/commission limit.
3. Use `ecom_write_affiliate_campaign` for a supported create/update operation.
   Inspect its actual input and activation semantics first. Explain material changes
   and obtain the merchant's required approval; do not assume a write is draft-only.
   Use returned existing IDs when updating; don't create duplicate plans.
4. Let the backend perform its supported discovery, qualification and dispatch.
   Do not implement local polling or a second outreach queue. A request to plan
   does not authorize immediate mass messaging.
5. Use `affiliate_list_shop_open_collaborations` or
   `affiliate_list_shop_target_collaborations` for relevant current terms.
   Use manage operations only for requested changes; they can alter live offers.
6. Handle resulting creator work through
   [creator conversations](handle-creator-conversations.md).

Verify the returned plan/version/status and any supported follow-up reads.
Report configured versus active versus executed separately. A successful plan
write is not evidence that creators were reached.
Keep only merchant-owned brief/experiment intent locally, with the remote ID if
useful. Don't export the backend's candidate list or per-creator execution state.

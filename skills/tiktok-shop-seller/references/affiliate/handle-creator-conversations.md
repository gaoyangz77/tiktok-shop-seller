# Handle creator conversations

Goal: work from the backend's assembled relationship agenda and resolve a real
business decision without replaying its orchestration in the client.

## Context and decision

1. Read STORE.md for merchant-approved communication, sample and commercial limits.
2. Inspect `affiliate_get_work_items` with `input.dispatch: false` and appropriate
   filters/limit. Read the assembled agenda before fetching individual records.
3. Supplement only missing evidence using relationship, timeline, creator profile,
   contact state, product or sample tools. Distinguish creator ID, relationship ID,
   shop ID, product ID and sample record ID; they are not interchangeable.
4. If beginning a work item, fetch with `input.dispatch: true`. Carry the returned
   immutable agenda snapshot and boundary/revision fields exactly into the resolution
   input. Do not invent them, persist them as a local source of truth, or dispatch
   an entire queue just to inspect it.
5. Address the complete dispatched agenda. Use the product-explanation, sample or
   follow-up workflow as applicable. Do not ask unrelated subagents to impersonate
   internal staff or use Desktop inter-agent escalation tools.

## Execution paths: choose one

- **Dispatched work:** use `affiliate_resolve_work_item` for the terminal decision.
  Inspect the current schema for REQUEST_ACTION / NO_ACTION_NEEDED and supported
  typed actions. This backend workflow is not an agent-message relay.
  Supply the exact snapshot boundary. Resolve once logically; a final chat reply
  alone does not complete the work item. Do not blindly replay an uncertain resolve.
- **Direct, merchant-requested message outside a dispatched action:** use
  `affiliate_send_creator_message` with a stable idempotency key, verified
  relationship/shop and a supported channel.
- Never directly send/review and also request the same side effect through resolve.

For work-item messages the backend resolves the recipient route; do not invent
contact/account/provider IDs. Select the requested supported channel explicitly.
Platform-native cards must refer to actual local entity IDs for the destination
shop. Do not mix cards belonging to different shops or place them in email/WhatsApp.
Only use attachments if a supported staging/resource flow is actually available.

## Failure and completion

A stale snapshot/revision means re-read, then reconsider; do not simply substitute
fresh revision numbers into an old decision. When a concrete decision requires
merchant input, use the supported pending-review path if available and report it.
Do not label it resolved/executed or use NO_ACTION_NEEDED to hide a blocker.

A resolution receipt can mean the boundary was accepted or a proposal was queued,
not that a message was delivered. Check available delivery/relationship state and
report known status. If the needed status tool is not exposed, state that verification
is pending. Never create duplicate sends to compensate for limited observability.

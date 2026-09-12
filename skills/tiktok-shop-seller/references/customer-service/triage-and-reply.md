# Triage and reply

Goal: identify conversations needing attention and deliver an accurate, authorized
reply without duplicating another operator or the backend.

## Context

Read STORE.md for communication preferences and approved commitments. Fetch current
conversation context; use relevant published Product Knowledge or approved local
manual/FAQ only for non-listing facts.

Choose the smallest entry point:

- `ecom_get_customer_service_inbox`: backend-materialized filtered inbox,
  including cross-shop selection. Always bound the intended shop set.
- `ecom_get_pending_conversations`: backend pending-reply signals for one shop.
  Pending and unread are different; neither is proof the latest buyer message
  still needs a reply.
- `ecom_get_conversations`: general recent conversation browsing. Use a bounded
  limit; do not request all conversations by default.
- `ecom_search_cs_sessions`: precise lookup such as buyer nickname or start time.

## Execute

1. Select a bounded batch and inspect `ecom_get_conversation_messages` or
   `ecom_cs_get_conversation_details`. Check the latest sender, timestamps,
   unresolved question, and whether a reply was already sent.
2. Use backend context first. Fetch an order/product only if needed to answer;
   route delivery/refund questions to their shared workflows.
3. Decide: informational reply, an authorized remedy, a missing fact to ask for,
   or no response needed. Match the buyer's language; don't invent guarantees.
4. If asked to draft, stop at a draft. If authorized to reply, recheck latest
   messages/status and send using `ecom_send_customer_service_text_reply`,
   with a stable idempotency key.
5. Use `ecom_send_customer_service_card` only for a relevant, verified product,
   order or logistics entity. Allowed card categories are PRODUCT_CARD,
   ORDER_CARD and LOGISTICS_CARD; inspect live schema. Supply its own stable key.
   It does not require a Desktop Agent Session.
6. Create a conversation using `ecom_create_customer_service_conversation`
   only when needed, after checking an existing conversation and the recipient.
   It also needs a stable key.
7. Mark read or end a session only when justified by the workflow and merchant
   authorization. Reading, replying and closing are separate actions; do not close
   unresolved cases merely to clear a queue.

## Verify and recover

Check the returned message/conversation identifiers and current message state.
Report sent versus pending/unknown honestly. On uncertain delivery reconcile first;
do not resend with a new key. A platform error or forbidden shop is not an empty inbox.
Summarize handled counts and unresolved cases without saving chat transcripts locally.

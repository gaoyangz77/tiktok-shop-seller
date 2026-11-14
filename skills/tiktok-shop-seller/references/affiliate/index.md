# Affiliate

Choose the merchant outcome:

- New or revised outreach goals: [plan and run outreach](plan-and-run-outreach.md).
- Creator replies and backend work items: [handle creator conversations](handle-creator-conversations.md).
- Sample approval/rejection: [review sample applications](review-sample-applications.md).
- Product explanation and creative education: [explain products](explain-products-to-creators.md).
- Existing relationship or collaboration follow-up: [follow up](follow-up-collaborations.md).

Work items exist only for shops with the Affiliate service on; see
[turn on services](../foundations/getting-started.md#turn-on-services).
A shop (or its business developer) bound to a TK Copilot Desktop computer is
worked by that Desktop: over MCP its items are read-only and report
`agentEligibilityReason: AFFILIATE_DESKTOP_ASSIGNED`. Direct actions (messages,
sample reviews, collaboration changes) remain available for any shop.

Default to `affiliate_get_work_items` with `dispatch: false` for inspection.
Dispatch only when beginning authorized work. Shared delivery, stock and product
workflows remain separate references, not duplicated Affiliate instructions.

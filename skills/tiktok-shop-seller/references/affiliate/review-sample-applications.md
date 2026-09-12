# Review sample applications

Goal: make an authorized sample decision from current application and creator evidence.

1. Read merchant-approved sample budget, product restrictions and acceptance criteria.
2. Fetch the current sample through `affiliate_get_sample_application` or
   `affiliate_list_creator_sample_applications`. Check relationship/profile,
   collaboration context, current review status and required revisions.
3. Verify product/variant and inventory when necessary. Treat product-fit predictions
   as supporting evidence, not automatic eligibility or commercial authorization.
4. If dispatched, submit the supported review action through
   [work-item resolution](handle-creator-conversations.md).
   Otherwise use `affiliate_review_sample_application` for a direct authorized
   review, supplying current projection/review revisions.
5. Inspect the live schema to distinguish platform approval/rejection from a local
   soft rejection that lets an application expire. They have different effects.
   Do not claim a soft rejection was a platform rejection. Supply required reasons
   from actual allowed values rather than invented enums.
6. Re-read on revision conflicts or changed eligibility. An uncertain response is
   not permission to repeat an approval or invert the decision.

Verify review disposition and platform/action status separately. Approval is not
proof a sample was shipped. For a missing sample use
[delivery exceptions](../order-management/resolve-delivery-exceptions.md).
Keep backend sample state remote.

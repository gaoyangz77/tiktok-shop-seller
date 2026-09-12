# Publish a listing

Goal: create an authorized listing from merchant-supplied product facts.

1. Confirm shop, region and product/variants. Gather missing facts from the merchant;
   local manuals are supplementary evidence, not a substitute for required fields.
2. Discover publishing prerequisites, categories/recommendations, category rules,
   attributes and brands using current tools. Required fields are region/category
   dependent; do not use a hard-coded universal payload.
3. Select the actual warehouse if inventory is included. Never invent a warehouse,
   brand, certification, SKU or stock figure.
4. Prepare only the needed listing draft. If the merchant wants to retain it locally,
   use work/product-drafts with draft status and source evidence.
5. Upload authorized product images using the tool's live schema. The current
   `ecom_upload_product_image` adapter uses filename, mimetype and raw dataBase64;
   a local file path is not a remote upload. Check current size/type limits and
   avoid dumping large base64 data into conversational context.
6. Run the supported listing check; correct validation errors. Explain material
   listing content and launch settings within the merchant's approval boundary.
7. Call `ecom_create_product` only after required decisions are settled.
   Do not assume creation and activation have identical effects across regions.
8. Verify the returned product ID and current publication/review state. Creation
   acceptance does not guarantee a live listing. After uncertain creation, search
   for the matching result before considering another create.

Keep the platform as the listing authority. Archive/remove the active local draft
after verified publication; don't turn it into a continually maintained mirror.

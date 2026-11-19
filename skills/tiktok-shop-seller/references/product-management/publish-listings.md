# Publish a listing

Goal: create an authorized listing from merchant-supplied product facts.

1. Confirm shop, region and product/variants. Gather missing facts from the merchant;
   local manuals are supplementary evidence, not a substitute for required fields.
2. Discover publishing prerequisites, categories/recommendations, category rules,
   attributes and brands using current tools. Required fields are region/category
   dependent; do not use a hard-coded universal payload. If the prerequisite
   check fails on shop setup (for example the shipping or return warehouse),
   follow [shop setup the API cannot change](#shop-setup-the-api-cannot-change)
   before preparing the listing.
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

## Shop setup the API cannot change

TikTok's open API reads warehouses but cannot create them or change their
addresses, so no TK Copilot tool can fix a failed `PICKUP_WAREHOUSE` or
`RETURN_WAREHOUSE` check (or a similar shop-setup item). Say so plainly, then
offer the merchant two ways:

1. **They set it in Seller Center.** Give the exact place (US: Logistics →
   Warehouse & shipping → Warehouse settings) and what is needed: a shipping
   (pickup) warehouse and a return warehouse, each with contact name, phone and
   a full address that passes the platform's address check (USPS in the US).
2. **The agent fills it in for them,** only when all of these hold:
   - the host offers computer use or browser automation;
   - the merchant's Seller Center is already signed in, on this computer, in a
     browser the agent can operate. Shops run in another computer, a cloud
     phone, or an anti-detect/multi-account browser such as 紫鸟 or AdsPower
     are out of reach: use option 1 and do not try to open them;
   - the merchant agrees to this.

   Ask for the details first in one message: warehouse name, contact name,
   phone, full address with ZIP, and whether the return warehouse uses the same
   address. Open Seller Center in their signed-in browser and fill in the form.
   Before saving, show what will be saved and get a yes. Never enter TikTok
   passwords or verification codes; if a sign-in or verification page appears,
   let the merchant handle it. If the page does not match what you expect,
   stop and ask instead of guessing.

Either way, run the prerequisite check again afterwards and continue only when
it passes.

## After publishing

Keep the platform as the listing authority. Archive/remove the active local draft
after verified publication; don't turn it into a continually maintained mirror.

# Getting started

Goal: take a merchant from a fresh install to a first useful task, without the
TK Copilot Desktop app. Each step is a merchant decision; do not skip ahead.

1. [Sign in](#sign-in)
2. [Connect a TikTok Shop](#connect-a-tiktok-shop)
3. [Turn on the services the merchant wants](#turn-on-services)
4. [Plans and payment](#plans-and-payment)
5. [First task](#first-task)

## Sign in

Follow [connection and authentication](connection-and-authentication.md): ask
which line (Global or Mainland China) and whether they need a new account, then
connect and log in yourself; the merchant approves once and acts in the browser.
New merchants register on the TK Copilot website; existing website or Desktop
users sign in with the same account. In the new chat, confirm with one
`ecom_list_shops` call and go straight on to connecting a shop if the list is
empty. If the tools are missing because the merchant stayed in the old chat,
ask them to open a new one with a
[handoff message](connection-and-authentication.md#handoff-message); do not
work around it.

## Connect a TikTok Shop

Needed when `ecom_list_shops` returns no shop, or the merchant wants another one.

1. Ask which country the shop sells in. US shops use a dedicated application;
   other markets share a global one. Ask whether it is a cross-border seller
   account only if the merchant indicates so (`sellerType: CROSS_BORDER`);
   otherwise the default is local.
2. Call `ecom_start_shop_authorization` with that `market`. It returns
   `authorizationUrl` and `expiresAt`.
3. Open the link at once in the merchant's default browser when the host can
   (Codex on macOS: `open '<authorizationUrl>'`, with approval if the sandbox
   blocks it), and also show it as a clickable link in case nothing opened. The
   link is on the website of the line in use (`www.tkcopilot.com` or
   `www.tkjiang.cn`), works once, and must be opened within about five minutes;
   the TikTok sign-in that follows must finish within about ten minutes of the
   link being created. Tell the merchant to sign in to TikTok Shop on that page
   and approve now. Only the merchant's own browser may open it: never open it
   in a browser you control (computer use, browser automation) and never ask
   for TikTok credentials or codes.
4. If the merchant reports an expired or used link, or comes back later than
   that, call the tool again for a fresh one and open it the same way. Do not
   reuse an old link.
5. After the merchant says they finished, call `ecom_list_shops` and confirm the
   new shop by name and region. Historical data is synchronised in the
   background after authorization, so early reads may be incomplete; say so
   rather than reporting "no orders" or "no creators".
6. Do not stop at "connected". Call `ecom_get_billing_status` for the new shop,
   tell the merchant in plain words what is already allowed and until when (a
   new account may already have a customer-service trial), and ask which
   services to turn on now. Continue with [Turn on services](#turn-on-services)
   for the ones they choose.

## Turn on services

Services are per shop and off until the merchant turns them on. Use
`ecom_update_shop` with an explicit update mask, and confirm each change with
the merchant first.

- **Customer service** (`customerServiceSettings.enabled: true`): TK Copilot
  starts recording the shop's buyer conversations and syncs TikTok's customer
  service switch. Reply tools only work for recorded conversations. Do not set
  `csDeviceId`: it binds the shop to a Desktop computer, which takes the work
  away from this agent. Without Desktop, nothing replies automatically; the
  merchant asks this agent to work the inbox.
- **Affiliate** (`affiliateServiceSettings.enabled: true`): creator relationships,
  samples and work items are maintained for the shop. Do not set `deviceId` for
  the same reason. Ask the merchant for the minimum expected sales units a
  creator must be predicted to reach before a sample is approved, and set
  `affiliateServiceSettings.decisionThresholds.minExpectedSalesUnits`. TK
  Copilot never fills this in on its own; the Desktop app suggests `1`.
- **Inventory** (`wmsSettings.enabled`) only when the merchant uses a connected
  warehouse service.

Re-read the shop with `ecom_get_shop` after the update and report what is on.

## Plans and payment

Merchants using this Skill have the same subscriptions and trials as Desktop
users. Call `ecom_get_billing_status` to see, per shop, whether customer
service, inventory, affiliate and analytics are allowed, why not (`code`), and
until when (`validUntil`).

- A tool error "Upgrade required: shop … is not entitled to … (…)" names the
  shop, product and reason. Read the billing status, explain it, and offer to
  start payment only if the merchant wants to.
- Customer service is the paid product. To pay, call
  `ecom_start_billing_subscription` with `planId`
  `ECOM_CUSTOMER_SERVICE_UNLIMITED_MONTHLY`, `scopeType: SHOP` and the shop id.
  Ask whether they pay by card in USD (`provider: STRIPE`, returns
  `payment.checkoutUrl`) or in CNY (`provider: LAKALA`, returns a QR payload).
  On the Mainland China line prefer LAKALA: after a Stripe payment the browser
  returns to a page on the global website, which may not open there.
  Leave `successUrl` and `cancelUrl` unset.
- Give the link or QR to the merchant to complete in their own browser or
  payment app. Never pay, enter card details, or open the link yourself.
- `ALREADY_ACTIVE` means nothing to pay. After the merchant says they paid,
  call `ecom_get_billing_status` again to confirm.
- `RIVONCLAW_AI_*` plans only power the Desktop app's hosted AI and are not
  needed here. The account-wide customer-service membership is arranged with
  TK Copilot directly and cannot be bought through this tool.

## First task

Suggest one concrete, read-first task that fits what was turned on, for example:

- "Show buyers waiting for a reply and draft answers for me to review" —
  [customer service](../customer-service/index.md).
- "Show creator work that needs a decision" — [affiliate](../affiliate/index.md).
- "Which products are close to running out of stock" —
  [stock and replenishment](../inventory-management/assess-stock-and-replenishment.md).

Offer to record the merchant's answers (preferred tone, refund and sample
limits) in `STORE.md` as described in
[workspace and data ownership](workspace-and-data-ownership.md).

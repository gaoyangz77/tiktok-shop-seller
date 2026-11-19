# Connect TK Copilot MCP

Use this for first connection, missing tools, or authentication problems.
Setup points the merchant's agent at a hosted service; it does not deploy a server.

Read the relevant section:

- [Install the Skill](#install-the-skill)
- [Add the MCP connection](#add-the-mcp-connection): choose the line, connect and log in, new chat
- [Find and approve tools in the host](#find-and-approve-tools-in-the-host)
- [Choose a login flow](#choose-a-login-flow)
  - [Website already signed in](#website-session-to-mcp)
  - [Desktop already signed in](#desktop-session-to-mcp)
  - [First-time account registration](#first-time-account-registration)
  - [Use the website or Desktop after MCP login](#use-website-or-desktop-after-mcp-login)
- [Session boundaries and recovery](#session-boundaries-and-recovery)
- [Diagnose connection and access](#diagnose-without-hiding-errors)

After the first login, continue with [getting started](getting-started.md).

## Install the Skill

The Skill is a plain folder: `skills/tiktok-shop-seller` from the public
repository or its release archive. Nothing has to be built or executed.

- WorkBuddy: import the folder or archive in its Skills UI and confirm the scope
  it reports.
- Codex: place the folder in a skills directory Codex reads, for example
  `<workspace>/.agents/skills/tiktok-shop-seller` for one project.
- Claude Code: place it at `<workspace>/.claude/skills/tiktok-shop-seller`
  (project) or `~/.claude/skills/tiktok-shop-seller` (user).
- Other agents: use the host's own Skill import; do not claim support until
  its flow is verified.

Prefer one project directory per merchant workspace. Do not change unrelated
global settings. Codex's built-in skill installer places Skills under
`~/.codex/skills`; that is fine.

Installing is not the end of the task. In the same turn, check whether a
`tkcopilot` connection exists and is logged in (`codex mcp list` in Codex) and,
if not, continue with [Add the MCP connection](#add-the-mcp-connection) without
waiting for the merchant to ask "what next". The merchant may know nothing about
MCP, configuration files or terminals.

## Add the MCP connection

The agent does every step itself. The merchant only answers one round of
questions (line and account), approves the host's permission prompt, and acts in
the browser. Never hand the
merchant a terminal command or a settings screen to fill in while the agent
can run the host's own command with approval. Report each result briefly in
plain words.

### 1. Choose the line

There is one remote Streamable HTTP endpoint with every tool, on two lines:

| Line | MCP URL | Website / consent |
| --- | --- | --- |
| Global | `https://api.rivonclaw.com/mcp` | `https://www.tkcopilot.com` |
| Mainland China | `https://api.tkjiang.cn/mcp` | `https://www.tkjiang.cn` |
| Staging (global only) | `https://api-stg.rivonclaw.com/mcp` | `https://stg.tkcopilot.com` |

Ask the merchant whether they are in mainland China without a VPN, or whether
their browser opens `https://www.tkcopilot.com`. In the same round, ask whether
they already have a TK Copilot account (website or Desktop) or need a new one;
the answer decides what you tell them before login (step 2). Use the Mainland China line if
they are in mainland China or cannot open it; otherwise use Global. A failed
network probe from the agent is not evidence: sandboxed agent shells (Codex by
default) cannot reach the internet at all, wherever the merchant is.

Each line has its own login. A token from one line does not work on the other;
switching lines means replacing the URL and logging in again. Do not configure
both lines at once. Older per-area URLs (`/mcp/shop-core`,
`/mcp/customer-service`, `/mcp/affiliate`) are retired and answer 410 with the
current URL; replace any configuration that still uses them.

### 2. Connect and log in in one step

Name the connection `tkcopilot`; OAuth scope `mcp:shop` (the server's default);
the OAuth resource is the MCP URL itself.

Before running anything, tell the merchant in one or two sentences what will
happen: the host asks permission to connect TK Copilot; then a browser page
opens where they choose **Allow Agent access**. The page has no account
switcher and may already show an account this browser signed in to earlier, so
say what to check, based on their answer:

- **New account:** if the page shows any signed-in account, do not choose
  Allow; sign out on the website, register with their own email, then come
  back to the page (or let the agent start login again).
- **Existing account:** check that the email on the page is the account they
  mean to use before choosing Allow; if not, sign out and sign in with it.

If they approved the wrong account anyway, log the host out
(`codex mcp logout tkcopilot`) and start login again after they switch accounts.

- **Codex:** run `codex mcp add tkcopilot --url <MCP URL>` yourself, requesting
  escalated permissions (it writes the user configuration and needs network;
  a sandboxed run fails). One approval covers the whole step: when the server
  supports OAuth, this command immediately starts login and opens the
  browser. It keeps running until the merchant finishes in the browser, so
  start it, then keep polling its output (a few minutes is normal) until it
  exits; do not kill it or start a second login meanwhile.
  - Already added but not logged in (`codex mcp list` shows `tkcopilot`
    without `OAuth`): run `codex mcp login tkcopilot --scopes mcp:shop` the same
    way.
  - Added with a wrong or retired URL: `codex mcp remove tkcopilot`, then add it
    again as above.
  - The merchant declines the permission prompt: stop, explain that the
    connection cannot be made without it, and ask whether to try again.
  - A project-only connection is possible in `<workspace>/.codex/config.toml`
    (`[mcp_servers.tkcopilot]`, `url`, `scopes = ["mcp:shop"]`), but the agent
    cannot write it from the sandbox and the project must be trusted; prefer
    the command above.
- **Claude Code:** `claude mcp add --transport http --scope project tkcopilot <MCP URL>`
  (writes `.mcp.json`); the merchant then authenticates `tkcopilot` with `/mcp`.
- **WorkBuddy:** Settings → MCP, add a remote HTTP server named `tkcopilot` with
  the MCP URL, or project file `.workbuddy/mcp.json`:
  `{"mcpServers": {"tkcopilot": {"type": "http", "url": "<MCP URL>"}}}`, then
  complete OAuth from the MCP settings screen. This flow has not yet been
  verified end to end.

Success is the host reporting the login finished (Codex prints a success line
and `codex mcp list` shows `OAuth`), not the browser page alone. Never paste
existing configuration contents into chat, and do not edit or remove other MCP
servers. Use staging only for a staging account.

### 3. New chat

New MCP tools never appear in the chat that added them. Tell the merchant, in
one sentence, to open a new chat and paste the handoff message you wrote for
them (below). Never make them write it themselves: a merchant left without one
types "继续" or "推进下一步", and the new chat has to rediscover everything. In
the new chat, follow [getting started](getting-started.md).

#### Handoff message

Whenever you ask the merchant to open a new chat, for any reason, end your reply
with a ready-to-paste message in a fenced code block so it copies in one click.
Write it in the merchant's language, as the merchant speaking, and keep it to
about six lines:

- the goal and the line in use (for example "国际线路");
- what is already done and confirmed, with the shop name and region when known;
- what is waiting on the merchant's decision, if anything;
- the one next step to take;
- "先用工具核对当前状态再动手" so the new chat re-reads live facts instead of
  trusting the message.

Leave out tokens, authorization or payment links, codes, buyer or creator
personal data and anything from `STORE.md` the new chat can read itself.
Example after connecting:

```text
我用 tiktok-shop-seller 运营 TikTok 店铺，TK Copilot 国际线路已连接并登录（新注册账号）。
还没有绑定店铺。下一步：帮我绑定美国站本土店。先用工具核对当前状态再动手。
```

Merchants often keep typing in the same chat anyway. When a request needs
`tkcopilot` tools and this chat has none (look the tool up once, as described
below), say in one sentence that the connection only shows up in a new chat and
ask them to open one, with a [handoff message](#handoff-message) for the task
they just asked for. Do not reach the tools any other way: no second host
process (for example `codex app-server`), no script that calls the MCP
endpoint, no reuse of stored tokens. Those paths skip the host's approval
prompts for tools that send, refund, edit or pay, and work in one host only.

## Find and approve tools in the host

- The catalogue is large (about 90 tools). Hosts may defer MCP tools instead of
  listing them directly. Codex places them in a deferred catalogue reached
  through its code-execution tool (search `ALL_TOOLS` by tool name, then call
  the match). Look the tool up by its name, for example `ecom_list_shops`;
  "no tool-search tool" does not mean the MCP tools are missing.
- Tools that can change state (sending, refunding, editing, starting payment or
  shop authorization, and `affiliate_get_work_items` because dispatch can begin
  work) ask the merchant for approval in Codex. Explain what the call will do
  and let the merchant approve it in the host. Never work around the prompt.
- If no `tkcopilot` tools are reachable at all, check the connection status in
  the host (`codex mcp list` shows `OAuth` once logged in) before concluding
  that a capability does not exist. Connected but absent in this chat means a
  new chat is needed ([step 3](#3-new-chat)), never a workaround.

## Choose a login flow

Within one environment, website, Desktop and MCP use the same TK Copilot account
and users table. They keep separate sessions and credentials. These flows reuse
an authenticated website session, or create one using a short-lived, single-use
Desktop handoff; they do not exchange an MCP token for a website/Desktop token.

Confirm the target environment, intended account and browser profile. Do not
repeat setup if the merchant only wants to use an already-working connection.
Each line pairs one website with one API (see the table above): Global uses
`https://www.tkcopilot.com`, Mainland China uses `https://www.tkjiang.cn`, staging
uses `https://stg.tkcopilot.com`. The consent page always opens on the website of
the line being configured; sign in there. Desktop must use the same environment
as the pending authorization.

### Website session to MCP

1. Start MCP login from the agent host using the command/UI above. It opens a
   fresh TK Copilot authorization request; do not send the merchant to a bare
   `/oauth/mcp/authorize` URL or invent its `request_id`.
2. Use the browser profile already signed into the intended website account.
   The page checks that session. If it is missing, sign in on the page with the
   existing account, or use the Desktop flow below.
3. Have the merchant check the displayed account and requesting agent, then
   choose **Allow Agent access** if intended. An existing website login does not
   automatically approve MCP access. If the account is wrong, stop and switch
   the website account through its normal UI, then restart MCP login.
4. The browser returns an authorization code to the agent host. The host exchanges
   it using PKCE and stores its own MCP credentials. Confirm the host reports a
   successful connection; an open consent page alone is not completion.

### Desktop session to MCP

1. Start MCP login from the agent host. If the website is not signed in, choose
   **Continue with Desktop** on the TK Copilot authorization page.
2. Allow the browser to open TK Copilot Desktop. The page generates a
   `tkcopilot://web-session` link carrying the pending authorization return path.
   Use that generated link; do not construct handoff tickets or call private auth
   GraphQL operations from the agent.
3. Desktop uses its existing account to request a single-use website login ticket
   and opens the website. If Desktop is not signed in, it asks for login first;
   restart from the agent if the pending authorization expires meanwhile.
4. The website consumes the ticket, creates its own browser session and returns
   to the original MCP consent page. Have the merchant confirm the account and
   choose **Allow Agent access**. Desktop login alone does not grant agent access.
5. Verify completion in the agent host as in the website flow.

Check that the installed Desktop supports **Continue with Desktop** and its
deep-link handler. Backend/Web deployment or merged Desktop source does not prove
the installed client has this feature. If the link is unhandled, opens the wrong
environment, or never returns, use ordinary website sign-in for MCP; verify an
appropriate Desktop release before suggesting an update. Do not export Desktop tokens.

### First-time account registration

1. Start MCP login from the agent host and choose registration on the trusted
   TK Copilot page if the merchant does not already have an account. Existing
   Desktop/website users should sign in, not create a second account.
2. Have the merchant enter their email, choose a password, and complete the
   displayed captcha/email-verification steps there. The current registration
   flow is email verification plus a chosen password, not passwordless login and
   not an emailed temporary password. Respect the displayed resend quota and errors.
3. Registration establishes a website session for the shared account. The merchant
   still confirms **Allow Agent access** to finish the separate MCP authorization.
   They can later use the same account on the website and Desktop, without migration
   or a second registration. Login does not itself authorize a TikTok Shop; confirm
   actual shop access separately when needed.

### Use website or Desktop after MCP login

**Website:** open the website for the same environment in the same browser profile
used for MCP consent. That profile normally already has a website session because
the merchant signed in there before authorizing MCP. Confirm the displayed account;
MCP login does not sign every browser/profile into the website.

**Desktop:**

1. Open Desktop's login dialog and choose **Sign in from your browser**
   / **在浏览器中登录**. Start from Desktop, not from a guessed
   `/account/desktop-login` URL: Desktop must create a fresh request and local callback.
2. In the opened browser, use the same profile as the earlier MCP consent. If that
   website session is still valid, no password entry is needed. Otherwise sign
   in with the existing account on the website.
3. Have the merchant verify the account and requesting device, then choose
   **Allow TK Copilot Desktop** only for the request they just initiated.
4. The browser returns a one-time code to Desktop's local callback. Desktop verifies
   the flow and exchanges the code using PKCE for its own session. Confirm that
   Desktop shows the intended account; the agent's MCP credentials remain separate.

If the installed client lacks browser sign-in, use its supported account login or
an appropriate released update. No MCP login tool currently grants a website or
Desktop session directly. If only the MCP token remains valid, it cannot replace
website authentication in this flow.

## Session boundaries and recovery

- Enter email/password/verification codes only in the trusted TK Copilot UI,
  never in agent chat, `STORE.md`, Skill files or configuration. Do not request
  pasted authorization codes, handoff links, cookies, JWTs or refresh tokens.
  Let each client store credentials through its normal secure mechanism.
- A different browser, profile, private window, expired cookie or website logout
  may require website sign-in again even while MCP still works. Desktop may open
  the system-default browser/profile instead of the one used by the agent; check
  the displayed identity and sign in there if necessary. Do not approve the wrong
  identity or try to recover website access from the agent's credential store.
- Never mix production and staging accounts, tickets, callbacks or endpoints.
  An installed production Desktop is not a staging login bridge. Complete staging
  website login directly if a matching Desktop environment is unavailable.
- For expired/used tickets, missing callback or incomplete authorization links,
  restart from the originating client (agent for MCP, Desktop for Desktop login).
  Do not reuse a captured link/code, manually exchange it, or repeatedly send email.
- Browser approval and application switching are merchant steps. A Skill cannot
  bypass host trust, auto-approve consent, or declare the destination logged in
  merely because the browser says approval succeeded. Check destination state.
- Keep revocation claims scoped: disconnecting an agent's MCP grant is not the
  same as logging out the website or Desktop, and website logout does not imply
  all MCP grants were revoked. Use the relevant client's supported account controls.

## Diagnose without hiding errors

- 410 `endpoint_retired`: the configuration uses a retired per-area URL. Replace
  it with the `/mcp` URL from the response, then log in again.
- 404 metadata/endpoint: route or deployment missing; stop login attempts and
  report the environment. Do not send repeated verification emails.
- 401 before login: expected, with a `resource_metadata` challenge pointing to
  `/.well-known/oauth-protected-resource/mcp` on the same host as the MCP URL. After login: let the host refresh
  or log in again.
- "Protected resource metadata resource mismatch": the configured URL is not
  one of the `/mcp` URLs in the table (for example a Desktop-only CN host). Fix the URL instead of overriding the resource.
- 403 or "Upgrade required": entitlement, shop authorization or region
  restriction; never treat as an empty shop, empty inbox or zero inventory.
  See [getting started](getting-started.md#plans-and-payment).
- Configured but tools absent right after a session starts: the tool list loads
  in the background. On the Mainland China line it can take 10–30 seconds; wait,
  then look the tool up again before changing configuration or logging in again.
- Still absent: check login state, trust and the host's deferred
  catalogue (above). A Skill reference cannot make an unavailable tool callable.
- After MCP login, if verifying shop access is requested: first call only
  `ecom_list_shops`, confirm the intended shop, then one task-relevant read.
  An empty list means no shop is connected yet; connect one as described in
  [getting started](getting-started.md#connect-a-tiktok-shop), not by creating
  another TK Copilot account. No send/refund/edit smoke tests without separate
  authorization.
- Report configuration, OAuth completion, destination account/session and shop
  access as separate results. For a website/Desktop-login-only request, stop once
  the requested session is verified; do not start store operations.

Official references:
[Codex configuration](https://learn.chatgpt.com/docs/config-file/config-reference),
[Claude Code MCP](https://code.claude.com/docs/en/mcp),
[WorkBuddy configuration](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/MCP-Guide),
[WorkBuddy Skill import](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market).

# TikTok Shop Seller Skill

用你自己的 Agent（WorkBuddy、Codex、Claude Code 等）运营 TikTok Shop，不需要下载
[TK Copilot](https://www.tkcopilot.com) 客户端。开源的是通用业务工作流；店铺数据、
后台编排和同步由 TK Copilot 托管的 MCP 服务提供。

只发布 **Skill**，不是插件、店铺模板或本地运行的后端。不包含 TK Copilot 私有
Expert、内部运营规则、训练资料或店铺数据。Skill 源码采用 MIT 许可；托管服务的
账号、权限与收费和 TK Copilot 客户端一致，另行约定。

## 给卖家的入口

对自己的 Agent 说一句就够了：

> 帮我装这个 skill：https://github.com/gaoyangz77/tiktok-shop-seller

接下来 Agent 会自己完成连接：问你一句是否在中国大陆，弹出一次权限请求让你批准，
然后打开浏览器让你注册或登录 TK Copilot 并点「Allow Agent access」。完成后按提示新开一个
聊天，说「绑店」即可。全程不需要命令行，也不需要自己填设置。

**给 Agent：** 装完 Skill 不要停在“已安装”。同一轮里接着按
[连接说明](skills/tiktok-shop-seller/references/foundations/connection-and-authentication.md#add-the-mcp-connection)
为卖家建立 `tkcopilot` 连接并登录（Codex 由你带权限运行 `codex mcp add`，它会直接拉起浏览器授权）。

首次安装后通常需要重新加载 Agent，并在浏览器里完成一次授权。Skill 不会绕过这些步骤。

## 安装

Skill 就是一个文件夹：`skills/tiktok-shop-seller`（也可从 Releases 下载压缩包）。
不需要 Python，也不需要运行任何脚本。

两条线路，选一条即可（每条线路单独登录）：

| 线路 | MCP 地址 | 官网 |
| --- | --- | --- |
| 国际 | `https://api.rivonclaw.com/mcp` | `https://www.tkcopilot.com` |
| 中国大陆 | `https://api.tkjiang.cn/mcp` | `https://www.tkjiang.cn` |

下表以国际线路为例，中国大陆把地址换成 `https://api.tkjiang.cn/mcp`：

| 宿主 | 安装 Skill | 添加 MCP 并登录 |
| --- | --- | --- |
| WorkBuddy | Skills 界面导入文件夹或压缩包 | 设置 → MCP 添加远程 HTTP 服务 `tkcopilot`，地址 `https://api.rivonclaw.com/mcp`，在该界面完成授权 |
| Codex | 放到 `<工作目录>/.agents/skills/tiktok-shop-seller` | `codex mcp add tkcopilot --url https://api.rivonclaw.com/mcp`（会直接拉起浏览器登录；已添加但未登录时用 `codex mcp login tkcopilot --scopes mcp:shop`） |
| Claude Code | 放到 `<工作目录>/.claude/skills/tiktok-shop-seller` | `claude mcp add --transport http --scope project tkcopilot https://api.rivonclaw.com/mcp`，在 Claude Code 里用 `/mcp` 登录 |

每条线路只需要这一条 MCP 连接，登录一次即可使用全部工具；新加的连接要重新开会话才会出现。
中国大陆线路跨境较慢，新会话开始后工具可能要 10–30 秒才加载完成，稍等再用即可。旧的 `/mcp/shop-core`、
`/mcp/customer-service`、`/mcp/affiliate` 地址已停用，请改成上面的地址。
WorkBuddy 的完整登录与调用流程尚未实测；Codex 已实测。
详见 [连接与登录](skills/tiktok-shop-seller/references/foundations/connection-and-authentication.md)。

登录后，Agent 会按 [上手流程](skills/tiktok-shop-seller/references/foundations/getting-started.md)
带你：绑定 TikTok 店铺 → 打开客服 / 达人服务 → 查看订阅 → 做第一件事。

## 不装客户端能做什么

- 能做：查看和回复买家消息、处理退货退款、处理达人消息与工作项、审样品、管理合作与推广计划、
  发布和修改商品、查库存与 FBT、看经营数据、维护产品知识、绑定店铺、查看订阅并拿到付款链接。
- 由你下指令时才做：没有客户端时不会 7×24 自动回复买家或自动处理达人；需要你让 Agent 去做。
  想要无人值守的自动运行，使用 TK Copilot 客户端。
- 已绑定客户端电脑的店铺：达人工作项由客户端处理，Agent 里只读；直接操作仍可用。
- 暂不支持：上传产品知识里的图片和视频（需在客户端里完成）。

Codex 会把较多的 MCP 工具放进按需加载的目录，并在发送、退款、修改、付款、绑店等会改变状态的
操作前请你批准，这是正常的安全提示。

## 工作流架构

```text
skills/tiktok-shop-seller/
├── SKILL.md
└── references/
    ├── foundations/              # 连接登录、上手流程、数据归属
    ├── customer-service/         # 买家回复、投诉与问题恢复
    ├── affiliate/                # 达人工作项、推广、样品、产品讲解
    ├── product-management/       # 发布、编辑、商品问题、产品知识
    ├── inventory-management/     # 库存风险与差异
    ├── order-management/         # 配送异常、退货退款
    └── store-performance/        # 经营复盘与下滑诊断
```

客服和达人是主要编排场景；商品、库存和订单是共享运营能力；经营分析提供决策支持。
按需要读取具体流程，不把所有 reference 一次加载。工作流与 MCP 工具多对多：
买家未收货与达人样品未收到，都复用同一配送异常流程。

## 官方更新与本地定制

- 官方 Skill 负责“怎么做”；你的 `STORE.md` 负责“这家店允许什么、目标是什么”。
- 私有资料放在自己的工作目录，不放进本仓库，不修改官方流程来填写店铺政策。
- 本地只保留平台没有的补充资料、原始素材和未发布草稿；已发布的产品知识以云端为准。
- 有 Git 需求可使用独立的私有仓库，不要 fork 本仓库来存店铺数据。

更新时重新下载或 `git pull --ff-only`，然后在宿主里重新导入或重新加载。
更多见 [工作目录与数据归属](skills/tiktok-shop-seller/references/foundations/workspace-and-data-ownership.md)。

## 测试

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

测试只检查 Skill 内容：链接可达、业务目录结构、安全与数据边界、上手流程的关键约束，
以及只使用单一 `/mcp` 地址。不调用任何真实店铺接口。

公开反馈请只提交脱敏信息，不上传订单、买家/达人消息、验证码、token 或完整配置。

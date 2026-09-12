# TikTok Shop Seller Skill

用你自己的 Agent 运营 TikTok Shop。开源通用业务工作流，通过
[TK Copilot](https://www.tkcopilot.com) 的 MCP 使用后端上下文与编排能力。

只发布 **Skill**，不是插件、店铺模板或本地运行的后端。
不包含 TK Copilot 私有 Expert、内部运营规则、训练资料或店铺数据。
Skill 源码采用 MIT 许可；托管 MCP 服务的可用性、账号权限与收费政策另行决定，
开源许可不等于承诺所有托管能力永久免费。

## 给卖家的入口

把下面这句话和本仓库链接交给自己的 Agent：

> 请安装这个仓库里的 tiktok-shop-seller Skill，只在我指定的店铺工作目录生效。
> 先检查当前 Agent 的安装方式，再配置 TK Copilot MCP，并引导我在浏览器完成登录。
> 不要把 token 写进聊天或仓库，也不要创建店铺数据镜像。

仓库链接：<https://github.com/gaoyangz77/tiktok-shop-seller>

首次安装仍可能需要宿主的项目信任确认、重载和浏览器授权。
Skill 不会绕过这些步骤，也不能自行给当前会话热加载 MCP 工具。
不熟悉 Git 的卖家不需要建立店铺 repo。

## 手动安装：Codex / Claude Code

需要 Python 3.11+。将本仓库下载或 clone 到一个长期保留的目录。
在仓库根目录执行，替换为自己的工作目录：

```sh
python3 skills/tiktok-shop-seller/scripts/install_skill.py --agent codex --project-dir /path/to/my-shop
python3 skills/tiktok-shop-seller/scripts/setup_mcp.py --agent codex --project-dir /path/to/my-shop --dry-run
python3 skills/tiktok-shop-seller/scripts/setup_mcp.py --agent codex --project-dir /path/to/my-shop
python3 skills/tiktok-shop-seller/scripts/doctor.py
```

Claude Code 将 `--agent codex` 换成 `--agent claude`。安装器使用目录软链接，
只影响指定项目，不修改全局配置。Windows 或不支持软链接的宿主可使用其 Skill 导入功能，
或把完整 `skills/tiktok-shop-seller` 文件夹复制到宿主认可的技能目录。

WorkBuddy 可从 Skills UI 导入该 Skill；配置脚本支持
`--agent workbuddy --project-dir /path/to/my-shop`。
实际 OAuth 兼容性需在对应版本中验证，不宣称所有 Agent 开箱即用。
详见 [连接、OAuth 与排错](skills/tiktok-shop-seller/references/foundations/connection-and-authentication.md)。

默认连接 production。测试环境为配置与 doctor 命令添加
`--environment staging`；不要混用两个环境的账号/凭证。
如已有同名配置，脚本会拒绝覆盖。切环境前请审查备份并手动移除/修改
三个 `tkcopilot_*` 配置项，再重新运行；不要删除其他 MCP 配置。

## 工作流架构

```text
skills/tiktok-shop-seller/
├── SKILL.md
├── scripts/                      # 项目级安装、配置与只读诊断
└── references/
    ├── customer-service/         # 买家回复、投诉与问题恢复
    ├── affiliate/                # 达人工作项、推广、样品、产品讲解
    ├── product-management/       # 发布、编辑、商品问题
    ├── inventory-management/     # 库存风险与差异
    ├── order-management/         # 配送异常、退货退款
    ├── store-performance/        # 经营复盘与下滑诊断
    └── foundations/              # 连接与数据边界
```

客服和 Affiliate 是主要编排场景；商品、库存和订单是共享运营能力；
经营分析提供跨领域决策支持。按需要读取具体流程，不把所有 reference 一次加载。
工作流与 MCP 多对多：买家未收货与达人样品未收到，都复用同一配送异常流程。
并不假定当前 MCP 已提供仓库重发、FBT 入库写操作或 Product Knowledge 发布接口。

## 官方更新与本地定制

- 官方 Skill 负责“怎么做”；商家的 STORE.md 负责“这家店允许什么、目标是什么”。
- 私有资料放在自己的工作目录，不放进本仓库，不修改官方流程来填写店铺政策。
- 本地仅保留平台没有的补充资料、原始素材和未发布草稿。
- 云端 Product Knowledge 已发布的内容不再维护一份可独立编辑的本地镜像。
- 有 Git 需求的商家可使用独立 private repo；不是本仓库的 fork，没有模板合并问题。

在干净的官方源码目录中 `git pull --ff-only`，审查更新并重载宿主。
软链接安装无需重新复制；导入/复制安装需重新导入。私有工作目录不受影响。
如果官方源码已有本地改动，先停下处理，不执行 reset/强制覆盖。
更多见 [工作目录与数据归属](skills/tiktok-shop-seller/references/foundations/workspace-and-data-ownership.md)。

## 安全与测试

配置器不保存 token、不发邮件、不登录、不运行店铺写操作；保留无关配置，
同名冲突时拒绝覆盖，现有配置变更前生成权限受限的备份。不要提交这些备份。
doctor 只检查公开授权元数据和未登录请求的 401 challenge；成功不代表已经登录，
也不代表用户具有某家店铺的访问权限。

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

测试覆盖配置保留/冲突/重复安装、OAuth canonical resource、诊断失败语义、
工作流链接与安全边界。不调用真实店铺写接口。
当前为早期版本：Codex 配置解析可本地验证；Claude Code / WorkBuddy 的
实际登录与业务调用仍需要对应客户端验收。托管部署不可用时请停在诊断步骤。

公开反馈请只提交脱敏信息，不上传订单、买家/达人消息、验证码、token 或完整配置。

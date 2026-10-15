# writing-doc

[English](README.md) · 简体中文

**AI 写了一大篇，读完还是不懂。**

<img src="assets/x-problem-zh-CN.png" width="600" alt="AI 写了一大篇，读完还是不懂。废话太多，重点太少。句句通顺，就是没有答案。全部看完，还是不知道怎么做。AI 生成了文字，却没有完成沟通。">

writing-doc 把 AI 输出变成目标读者看得懂、用得上、能照着行动的文档。

<img src="assets/x-solution-zh-CN.png" width="600" alt="让目标读者一眼看懂。把答案放在第一句。只保留读者需要的内容。让每一步都能照着做。writing-doc：把 AI 输出变成清楚、好懂、能行动的文档。">

## 安装

**v0.1.0 公开安装已验证。** skills 1.7.2 的默认分支与固定标签安装均在隔离项目中通过。详见[准确验证记录](docs/verification/v0.1.0.md)。

准备好 Node.js、npm 和 Git，在要使用技能的项目中运行：

```sh
npx skills add joevilcai666/writing-doc-skill --skill writing-doc
```

按提示选择你的 Agent。此命令读取仓库的默认分支。需要固定版本时，使用[版本固定方式](#固定版本)。

[看改写效果](#看改写效果) · [开始使用](#告诉它写给谁读完要做什么) · [其他安装方式](#其他安装方式) · [隐私](#隐私) · [验证状态](#目前验证到了哪一步)

## 看改写效果

一份启动指南可以把进程、配置和状态码解释一遍，却仍然没告诉开发者：到底先运行哪条命令？

writing-doc 先给读者要用的答案：

> 完成前置准备后，用这条命令在 4310 端口启动 Lantern API：
>
> `python -m lantern serve --port 4310`

[改写后的指南](demo/expected/SETUP_GUIDE.md)接着说明前置条件、三个步骤、成功时的 `HTTP 200` 响应，以及连接失败时的处理方法。命令、地址、版本和警告均保留。

对照[改写前全文](demo/source/AI_SETUP_GUIDE.md)与[改写后全文](demo/expected/SETUP_GUIDE.md)，或查看[示例说明](demo/README.md)。示例正文为英文。

Lantern API 是虚构服务。这个示例由人工编写，用于展示目标效果，不是实测 Agent 输出。仓库没有运行过这个服务。

## 告诉它写给谁，读完要做什么

安装后，让 Agent 使用 `writing-doc`。提供原文、目标读者，以及读者需要完成的任务。

```text
用 writing-doc 改写这份启动指南。读者是需要在本地启动服务的开发者。
先给启动命令，保留事实、命令、链接和警告，并说明如何判断启动成功。
```

只想要审阅意见时，直接说明：

```text
用 writing-doc 审阅这份 README。读者是第一次参与项目的贡献者。
指出会卡住他们的问题，并给出具体改法。只审阅，不修改文件。
```

技能保持你的语言。技能指令为中文，也支持英文文档请求。

## 适合那些“读懂后还要做事”的文档

| 文档 | 帮读者完成什么 |
| --- | --- |
| README | 快速知道项目能做什么，并完成第一个有用的任务。 |
| 操作指南、教程 | 准备好前置条件，照着步骤做，确认结果。 |
| API 文档 | 找到需要的调用，理解参数和返回结果。 |
| 技术方案、设计说明 | 理解决策、关键术语和必要细节。 |
| 已有技术文档 | 通过审阅找到障碍，或通过改写消除障碍。 |

writing-doc 把答案前移，删掉废话，补上完成任务所需的说明。技术事实和必要条件必须保留。

它不处理营销文案、文学创作，或只有格式转换的任务。它不会替你补造产品事实，也不能保证输出正确。Agent 能验证什么，取决于你提供的资料和可用工具。

## 其他安装方式

以下 Codex CLI 插件和 Claude Code 路径已通过公开安装验证。桌面选择器与模型行为尚未验证。同一个 Agent 选择一种方式即可，避免出现重复技能。

### Codex

Codex CLI 0.162.1 的插件路径已通过：

```sh
codex plugin marketplace add joevilcai666/writing-doc-skill --ref v0.1.0 --json
codex plugin add writing-doc@writing-doc-skill --json
codex plugin list --json
```

插件显示为已安装、已启用。安装后的 `SKILL.md` 与标签源码逐字节一致。

在 Codex 对话中使用内置 Skill Installer：

```text
$skill-installer install https://github.com/joevilcai666/writing-doc-skill/tree/v0.1.0/skills/writing-doc
```

这个独立的 Skill Installer 路径仍为 **Planned for v0.1.0 verification（待验证）**。此路径安装共享技能。安装后，在技能选择器中确认出现 `writing-doc`。若未出现，重启 Codex。具体机制见 [OpenAI 官方技能指南](https://learn.chatgpt.com/docs/build-skills#install-curated-skills-for-local-use)。

OpenAI 目录中的插件安装尚未验证。目前没有官方目录提交或上架记录。

### Claude Code

准备好 Git 和 Claude Code，在终端运行：

```sh
claude plugin marketplace add joevilcai666/writing-doc-skill
claude plugin install writing-doc@writing-doc-skill --scope local
```

这些命令在隔离配置中通过，客户端为 Claude Code 2.1.295。CLI 显示插件已启用，安装技能与源码一致。市场注册作用于你的用户账户。插件的 `local` 范围只对当前项目中的你生效。新建 Claude Code 会话，在 `/plugin` 中确认插件出现。

具体说明见 [Claude Code 官方安装指南](https://code.claude.com/docs/en/discover-plugins)。

### 固定版本

需要保持技能内容不变时，指定版本标签。前面的快速安装命令读取默认分支。

`skills` 使用带标签的完整路径：

```sh
npx skills add https://github.com/joevilcai666/writing-doc-skill/tree/v0.1.0/skills/writing-doc --skill writing-doc
```

Claude Code 的默认分支与固定标签二选一。替换已有市场注册前，先确认移除注册的影响。

`claude plugin marketplace remove writing-doc-skill` 可能卸载该市场的插件，并移除相应的启用配置。未指定 `--scope` 时，它会移除所有设置范围中的市场声明。这可能影响当前项目以外的已安装副本。

如果决定切换，先运行上述移除命令，再注册带标签的市场：

```sh
claude plugin marketplace add joevilcai666/writing-doc-skill#v0.1.0
```

注册带标签的市场后，按原来的范围重新安装所有受影响的副本。本地副本使用 `claude plugin install writing-doc@writing-doc-skill --scope local`。

Git 标签固定的是技能源码，不会固定安装器或 Agent 的版本。带标签的 `skills`、Codex CLI 和 Claude 市场安装均已通过。替换已有市场注册的过程尚未验证。

### 手动安装

准备好 Git，将指定版本克隆到一个新目录：

```sh
git clone --depth 1 --branch v0.1.0 https://github.com/joevilcai666/writing-doc-skill.git
```

将整个 `skills/writing-doc` 文件夹复制到客户端的技能目录。Codex 项目目录使用 `.agents/skills/writing-doc`。标签克隆和此文件夹复制已通过逐字节比较，客户端发现尚未验证。保留其中的 `SKILL.md`。如果目标位置已有同名文件夹，先比较内容，再决定是否替换。

其他客户端请使用其文档规定的 Agent Skills 目录。确认客户端列出 `writing-doc` 后，用一小段虚构文档试用。

## 卸载

根据原来的安装方式操作：

- Codex CLI 插件：运行 `codex plugin remove writing-doc@writing-doc-skill --json`。此命令移除已安装插件和本地插件缓存。Codex 0.162.1 的全新隔离试验已通过公开 v0.1.0 安装与卸载验证。
- `skills`：在原项目中运行 `npx skills remove writing-doc`，选择相同的 Agent 和范围。只有全局安装才加 `--global`。
- Claude Code：只卸载当前项目的本地副本时，使用 `claude plugin uninstall writing-doc@writing-doc-skill --scope local`。原安装范围不同，则替换范围。
- Codex Skill Installer 或手动复制：找到已安装的 `writing-doc` 文件夹，将它移出客户端技能目录。技能列表未刷新时，重启客户端。

Codex 市场移除是独立的可选操作。只有需要移除已配置的市场源时，才使用 `codex plugin marketplace remove writing-doc-skill --json`。插件移除保留市场注册。市场移除会影响该源的配置，以及后续从该源发现插件的能力。这个可选命令尚未验证。

需要移除整个 Claude 市场时，使用 `claude plugin marketplace remove writing-doc-skill`。它可能卸载该市场的插件，并移除相应的启用配置。未指定 `--scope` 时，它会移除所有设置范围中的市场声明。这可能影响当前项目以外的已安装副本。只做本地卸载时，优先使用上面带范围的插件卸载命令。市场移除的范围说明见 [Claude CLI 参考文档](https://code.claude.com/docs/en/plugins/cli-reference#plugin-marketplace-remove)。

其他卸载路径尚未通过公开验证：**Planned for v0.1.0 verification（待发布验证）**。卸载不会删除你用技能写出的文档。

## 隐私

本包不添加分析统计、遥测、远程服务或后台进程。技能本身不会上传文档，它为读取你所提供资料的 Agent 提供写作指令。

Agent、模型服务、工具和安装器各自适用自己的数据政策。第三方 `skills` CLI 说明其会收集匿名使用数据，可通过 `DISABLE_TELEMETRY=1` 关闭。详见其[遥测说明](https://github.com/vercel-labs/skills#telemetry)。

本包不修改 `AGENTS.md`、`CLAUDE.md` 或全局 Agent 指令。安装器可能更新自己的技能目录和客户端配置。公开示例只使用虚构资料。

## 目前验证到了哪一步

| 证据层级 | 当前状态 |
| --- | --- |
| 已实现（Implemented） | 共享技能、客户端清单、确认图片、虚构示例和本地检查已存在。 |
| 本地验证（Locally verified） | 准确发布提交通过 125 项测试、完整发布检查、全历史隐私扫描、技能验证器、真实隔离 Codex 安装和 Claude 严格验证。 |
| 公开验证（Publicly verified） | 匿名 main/tag 克隆、Release ZIP 与校验值、默认与固定版本的 `skills` 安装、Codex 固定版本插件安装与卸载、Claude 默认与固定版本插件安装均通过。安装技能与标签源码一致。 |
| 用户验收（User accepted） | 此包的实现尚无用户验收记录。 |

[v0.1.0 Release](https://github.com/joevilcai666/writing-doc-skill/releases/tag/v0.1.0) 已公开。Codex CLI 0.162.1 没有 `plugin validate` 命令，发布检查改用真实市场安装和逐字节比较。模型行为、读者理解、桌面发现和其他卸载路径尚未验证。详见[当前工作方式与限制](HOW_IT_WORKS.md)和[分发状态](docs/distribution.md)。这两份维护文档目前为英文。

## 让下一位读者少走一步弯路

遇到问题、客户端兼容性差异，或处理不好的文档任务，可以提交 [GitHub issue](https://github.com/joevilcai666/writing-doc-skill/issues)。请附最小虚构示例。

贡献前阅读 [CONTRIBUTING](CONTRIBUTING.md)，安全问题走 [SECURITY](SECURITY.md) 的私密渠道。本包使用 [MIT 许可证](LICENSE)。

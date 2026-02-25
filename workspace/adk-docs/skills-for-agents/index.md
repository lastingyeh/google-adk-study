# ADK 代理程式技能 (Skills)

> 🔔 `更新日期：2026-02-25`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/skills/

[`ADK 支援`: `Python v1.25.0` | `實驗性功能`]

代理程式***技能 (Skill)*** 是一個獨立的功能單元，ADK 代理程式可以用它來執行特定的任務。代理程式技能封裝了執行任務所需的指令、資源和工具，其基於 [Agent Skill 規範](https://agentskills.io/specification)。技能的結構允許其增量載入，以最小化對代理程式操作上下文視窗 (context window) 的影響。

實驗性功能

技能功能目前處於實驗階段，且存在一些 [已知限制](#已知限制)。我們歡迎您的 [回饋](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=skills)！

## 開始使用

使用 `SkillToolset` 類別在您的代理程式定義中包含一個或多個技能，然後將其新增至代理程式的工具清單中。您可以[在程式碼中定義技能](#在程式碼中定義技能)，或從檔案定義中載入技能，如下所示：

```python
import pathlib

from google.adk import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset

# 從目錄載入技能定義
weather_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "weather_skill"
)

# 建立包含載入技能的工具集
my_skill_toolset = skill_toolset.SkillToolset(
    skills=[weather_skill]
)

# 定義根代理程式並配置模型與工具
root_agent = Agent(
    model="gemini-2.5-flash",
    name="skill_user_agent",
    description="一個可以使用專門技能的代理程式。",
    instruction=(
        "你是一個很有幫助的助手，可以利用技能來執行任務。"
    ),
    tools=[
        my_skill_toolset,
    ],
)
```

有關包含技能的 ADK 代理程式完整程式碼範例（包含基於檔案和內嵌技能定義），請參閱程式碼範例 [skills-agent](../../python/agents/skills-agent/)。

## 定義技能

技能功能允許您建立技能指令和資源的模組化套件，代理程式可以根據需求載入。這種方法可以幫助您組織代理程式的功能，並透過僅在需要時載入指令來優化上下文視窗。技能的結構分為三個層次：

- **L1 (元數據 Metadata)：** 提供技能發現的元數據。此資訊定義在 `SKILL.md` 檔案的 frontmatter 區塊中，包含技能名稱和描述等屬性。
- **L2 (指令 Instructions)：** 包含技能的主要指令，在代理程式觸發技能時載入。此資訊定義在 `SKILL.md` 檔案的主體中。
- **L3 (資源 Resources)：** 包含額外的資源，如參考資料、資產和腳本，可根據需要載入。這些資源組織在以下目錄中：
  - `references/`：包含擴展指令、工作流程或指引的額外 Markdown 檔案。
  - `assets/`：資源材料，如資料庫綱要、API 文件、範本或範例。
  - `scripts/`：代理程式執行環境支援的可執行腳本。

### 使用檔案定義技能

以下目錄結構顯示了在 ADK 代理程式專案中包含技能的推薦方式。下圖所示的 `example-skill/` 目錄以及任何平行的技能目錄，都必須遵循 [Agent Skill 規範](https://agentskills.io/specification) 的檔案結構。只有 `SKILL.md` 檔案是必需的。

```text
my_agent/
    agent.py
    .env
    skills/
        example-skill/        # 技能目錄
            SKILL.md          # 主要指令 (必需)
            references/
                REFERENCE.md  # 詳細的 API 參考
                FORMS.md      # 表單填寫指南
                *.md          # 特定領域資訊
            assets/
                *.*           # 範本、圖片、資料
            scripts/
                *.py          # 工具腳本
```

不支援腳本執行

目前尚不支援腳本執行，這是一個 [已知限制](#已知限制)。

### 在程式碼中定義技能

在 ADK 代理程式中，您還可以使用 `Skill` 模型類別在代理程式的程式碼中定義技能，如下所示。這種技能定義方法使您能夠從 ADK 代理程式程式碼中動態修改技能。

```python
from google.adk.skills import models

# 使用 Skill 模型定義內嵌技能
greeting_skill = models.Skill(
    frontmatter=models.Frontmatter(
        name="greeting-skill",
        description=(
            "一個友好的問候技能，可以向特定的人打招呼。"
        ),
    ),
    instructions=(
        "步驟 1：閱讀 'references/hello_world.txt' 檔案以瞭解如何"
        " 向使用者問候。步驟 2：根據參考資料回傳問候語。"
    ),
    resources=models.Resources(
        references={
            "hello_world.txt": "你好！很高興你能來到這裡！",
            "example.md": "這是一個範例參考資料。",
        },
    ),
)
```

## 已知限制

技能功能目前處於實驗階段，包含以下限制：

- **腳本執行：** 技能功能目前不支援腳本執行 (`scripts/` 目錄)。

## 後續步驟

查看這些資源以建立具有技能的代理程式：

- ADK Skills 代理程式程式碼範例：[skills-agent](../../python/agents/skills-agent/)。
- Agent Skills [規範文件](https://agentskills.io/)

# 依賴注入應用

在高效能 Web API 的架構設計中，「依賴注入」（Dependency Injection, DI）不僅是減少重複代碼的工具，更是實踐「控制反轉」（Inversion of Control）的核心機制。作為一名架構師，我始終主張將資源管理（如資料庫連線、模型加載）與業務邏輯分離，這正是 Scott Meyers 在《Effective C++》中所強調的「模組化職責」在現代 Web 框架中的體現。

以下是針對 FastAPI 依賴注入在模型加載與驗證場景下的實戰指導。

---
## Part 1: 基礎實踐

### 情境 1：使用 `Depends` 消除重複的資源初始化代碼

**核心概念簡述**
傳統做法常在每個 Route Handler 中手動創建資料庫連線或初始化物件，這會導致代碼高度耦合且難以測試。FastAPI 的 DI 系統允許你定義一個「提供者」函數，並在需要時將其結果注入 Handler，實踐 DRY（Don't Repeat Yourself）原則。

**程式碼範例**

```python
# ❌ Bad: 在 Handler 內部手動管理資源，違反單一職責原則且難以維護
@app.get("/user/messages")
async def get_messages(user_id: int):
    db = DatabaseSession() # 手動創建連線
    try:
        messages = db.fetch_all(f"SELECT * FROM messages WHERE user_id={user_id}")
        return messages
    finally:
        db.close() # 必須記得手動關閉，否則造成資源洩漏

# ✅ Better: 使用 Depends 注入資料庫會話，由框架管理生命週期
async def get_db():
    db = DatabaseSession()
    try:
        yield db # 使用 yield 實現自動清理 (Teardown)
    finally:
        db.close()

@app.get("/user/messages")
async def get_messages(db: Annotated[DatabaseSession, Depends(get_db)]):
    # 直接使用被注入的 db，無需擔心連線關閉問題
    return db.fetch_messages()
```

**底層原理探討與權衡**
FastAPI 的依賴項在單次請求（Request Context）中具備快取機制。這意味著如果多個子函數依賴同一個 `get_db`，該函數只會執行一次，避免了重複建立連線的開銷。這種方式雖然增加了函數標籤的複雜度，但極大地提升了系統的健壯性。

---

## Part 2: 提升模型加載效能

### 情境 2：透過 DI 實踐模型預加載而非隨機加載

**核心概念簡述**
在大規模 GenAI 應用中，載入如 TinyLlama 等模型是非常耗時且阻塞 I/O 的操作。若在每個請求中才載入模型，用戶將面臨極長的等待時間。我們應利用 FastAPI 的 `lifespan` 預加載模型，並透過 DI 系統將單例模型注入 Handler。

**程式碼範例**

```python
# ❌ Bad: 在請求處理時才載入模型，導致效能瓶頸
@app.post("/generate")
async def generate_text(prompt: str):
    model = load_llm_model() # 每次請求都載入數 GB 的模型，極慢
    return model.predict(prompt)

# ✅ Better: 利用 lifespan 預加載並透過依賴注入共享單例模型
models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動時加載模型到全局字典
    models["llm"] = load_llm_model()
    yield
    # 關閉時清理資源
    models.clear()

def get_model():
    return models.get("llm")

@app.post("/generate")
async def generate_text(model: Annotated[Any, Depends(get_model)], prompt: str):
    # 使用已存在於記憶體中的模型實例，反應速度大幅提升
    return model.predict(prompt)
```

**適用場景：拇指法則（Rule of Thumb）**
*   **規則**：對於大型重量級模型（如 LLM、Stable Diffusion），務必使用 `lifespan` + DI 模式。
*   **例外**：若系統需要動態切換數十種不同的微型模型且 VRAM 有限，才考慮隨機加載策略。

---

## Part 3: 解耦業務邏輯與輸入驗證

### 情境 3：將複雜的輸入預處理與驗證移至依賴層

**核心概念簡述**
Route Handler 應該只負責「協調」，而不應包含複雜的字串解析或第三方抓取邏輯。透過將驗證邏輯封裝進 DI 函數中，可以保持控制器（Controller）的乾淨與可讀性。

**流程說明 (Mermaid)**

```mermaid
graph LR
    User[用戶請求] --> Router[API 路由]
    Router --> DI[依賴項: get_urls_content]
    DI -- 執行 Web Scraper --> Content[解析後的內文]
    Content --> Handler[Handler: 生成總結]
    Handler --> LLM[AI 模型預測]
    LLM --> Response[最終結果]
```

**程式碼範例**

```python
# ❌ Bad: 將解析網址內容的繁雜邏輯寫在 Handler 內
@app.post("/summarize")
async def summarize(prompt: str):
    urls = re.findall(r'https?://\S+', prompt)
    full_text = ""
    async with aiohttp.ClientSession() as session:
        for url in urls:
            async with session.get(url) as resp:
                full_text += await resp.text() # 邏輯散落在 Controller 中
    return ai_model.predict(full_text)

# ✅ Better: 將網址解析邏輯封裝為依賴項
async def get_urls_content(request: Request) -> str:
    body = await request.json()
    prompt = body.get("prompt", "")
    # 內部執行非阻塞抓取與 BeautifulSoup 解析
    content = await fetch_all_wikipedia_urls(prompt)
    return content

@app.post("/summarize")
async def summarize(content: Annotated[str, Depends(get_urls_content)]):
    # Controller 保持簡潔，只專注於模型調用
    return ai_model.predict(content)
```

---

## Part 4: 權限與安全性的層次化管理

### 情境 4：實踐階層式依賴圖（Hierarchical Dependency Graph）

**核心概念簡述**
權限檢查（Authorization Guards）不應硬編碼在邏輯中。FastAPI 允許依賴項依賴於另一個依賴項，形成一個有向無環圖（DAG），這在管理複雜的 RBAC（基於角色的存取控制）時極為有效。

**比較表：授權模型的 DI 實現**

| 模型名稱 | DI 實現方式 | 適用場景 |
| :--- | :--- | :--- |
| **RBAC** | `Depends(is_admin)` | 固定角色管理（管理員 vs 一般用戶） |
| **ABAC** | `Depends(check_pii_attribute)` | 根據數據屬性（如是否包含 PII）動態攔截 |
| **ReBAC** | `Depends(is_team_member)` | 根據用戶與資源的關係（如團隊成員）決定 |

**程式碼範例**

```python
# ✅ Better: 建立依賴圖，管理員權限檢查依賴於當前用戶獲取
async def get_current_user(token: str) -> User:
    user = db.fetch_user(token)
    if not user: raise HTTPException(401)
    return user

async def is_admin(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role != "ADMIN":
        raise HTTPException(403, detail="僅限管理員存取")
    return current_user

@app.post("/admin/re-index")
# 此 Handler 同時觸發了：身份驗證 -> 權限檢查 -> 執行邏輯
async def reindex_data(admin: Annotated[User, Depends(is_admin)]):
    return {"message": f"管理員 {admin.name} 已啟動重新索引"}
```

---

### 延伸思考

**1️⃣ 問題一**：如果依賴項發生異常，FastAPI 會如何處理？

**👆 回答**：FastAPI 會自動捕獲依賴項中拋出的 `HTTPException`，並直接返回響應給客戶端，而不會進入 Handler 執行邏輯。若使用 `yield` 模式，即使 Handler 執行失敗，`finally` 區塊仍會運行，確保資源（如資料庫連線）被釋放。

---

**2️⃣ 問題二**：使用 `Annotated` 有什麼優點？

**👆 回答**：根據官方建議，使用 `Annotated[Type, Depends()]` 優於舊式的 `param: Type = Depends()`。主要優點是提升了代碼對靜態類型檢查工具（如 mypy）的友好度，且能在同一個參數上附加多個元數據（如 `Annotated[str, Depends(), Field()]`）。

---

**3️⃣ 問題三**：DI 系統是否會造成顯著的效能開銷？

**👆 回答**：微乎其微。DI 的解析過程經過高度優化，且因具備請求內快取（Request Caching），重複的依賴計算會被避免。相比於其帶來的測試便利性與代碼解耦價值，這點開銷是可以忽略不計的。
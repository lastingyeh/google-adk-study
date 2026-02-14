# Concurrency vs. Parallelism: 核心原理與實戰

在現代軟體架構中，尤其是在 GenAI 和高效能運算領域，「併發 (Concurrency)」與「並行 (Parallelism)」是兩個基礎且關鍵的概念。本文件旨在深入探討這兩者的區別，並結合 Python 的特性，提供架構師在設計系統時的實戰準則。

---

## Part 1. 多執行緒與併發 (Multithreading & Concurrency)

在構建高效能分散式系統或 GenAI 服務時，區分「併發（Concurrency）」與「並行（Parallelism）」是架構師的基本功。併發是關於「處理」多項任務的架構設計（Structure），而並行則是「同時執行」多項任務（Execution）。

在 Python 的世界裡，多執行緒（Multithreading）處於一個尷尬但必要的地位。受限於全域解釋器鎖（GIL），執行緒通常只能實現併發而非並行。以下是針對多執行緒在現代異步背景下的實戰主題。

---

### 主題 1：僅將多執行緒用於「I/O 密集型」任務，而非「計算密集型」

**核心概念簡述**
Python 的 CPython 實作中存在 GIL，確保同一時間只有一個執行緒執行字節碼。對於 CPU 密集型任務（如加密或大量計算），多執行緒不僅無法提速，還會因執行緒切換開銷（Context Switch）而變慢。然而，在執行 I/O 操作（如網路請求、磁碟讀寫）時，GIL 會被釋放，這使得多執行緒成為處理「阻塞式 I/O 庫」的唯一救星。

**程式碼範例**

```python
# Bad: 在多執行緒中執行 CPU 密集型計算（如 Fibonacci），受限於 GIL，速度不升反降
import threading

def cpu_task():
    # 複雜計算...
    pass

threads = [threading.Thread(target=cpu_task) for _ in range(4)]
[t.start() for t in threads] # 並不會獲得 4 倍速

# Better: 將多執行緒用於 I/O 密集型任務，如呼叫不支持異步的舊式 requests 庫
import asyncio
import requests

async def main():
    # 使用 default executor 將阻塞調用委派給執行緒池，釋放主事件循環
    result = await asyncio.to_thread(requests.get, "https://api.example.com")
```

**底層原理探討與權衡**
多執行緒是作業系統管理的最小執行單元，共享行程（Process）的記憶體空間。雖然它比多行程輕量，但 context switch 的成本仍高於協程（Coroutines）。除非你必須使用不支援 `async` 的第三方庫（如 `requests` 或 `psycopg2`），否則應優先考慮原生協程。

---

### 主題 2：嚴格管理共享狀態，優先使用執行緒安全（Thread-safe）的同步原語

**核心概念簡述**
不同於協程在 `await` 點才切換，執行緒是「搶佔式多工（Preemptive Multitasking）」。作業系統可以在任何時間點中斷執行緒，這極易引發競爭條件（Race Condition）。在多執行緒環境下，修改任何共享變數（即使是簡單的 `i += 1`）都必須加鎖。

**程式碼範例**

```python
# Bad: 無保護地修改共享變數，會導致數據不一致 (Non-thread safe)
counter = 0
def increment():
    global counter
    counter += 1 # 非原子操作

# Better: 使用 Lock 確保臨界區（Critical Section）的原子性
from threading import Lock

counter = 0
counter_lock = Lock()

def safe_increment():
    global counter
    with counter_lock: # 自動 acquire 與 release
        counter += 1
```

**適用場景之「拇指法則」**
*   **規則**：只要資料會在多個執行緒間共享且可變（Mutable），就必須加鎖。
*   **例外**：如果使用 Python 內置的 `queue.Queue`，其內部已實作鎖機制，是執行緒安全的通訊管道。

---

### 主題 3：使用「執行緒池執行器（ThreadPoolExecutor）」管理資源，避免頻繁創建執行緒

**核心概念簡述**
頻繁地創建與銷毀執行緒是非常昂貴的作業系統開銷。架構師應預先配置一定數量的執行緒池，重複利用這些資源，並透過 `run_in_executor` 將其整合進異步架構中。

**程式碼範例**

```python
# Bad: 每次請求都手動創建執行緒，難以管理生命週期與異常
import threading

def handle_request():
    pass

t = threading.Thread(target=handle_request)
t.start()

# Better: 使用 ThreadPoolExecutor 並配合 asyncio 進行異步等待
from concurrent.futures import ThreadPoolExecutor
import asyncio

def blocking_io_call():
    # 模擬阻塞 I/O
    pass

executor = ThreadPoolExecutor(max_workers=10)

async def async_wrapper():
    loop = asyncio.get_running_loop()
    # 將阻塞任務丟入池中，並 await 其結果
    result = await loop.run_in_executor(executor, blocking_io_call)
```

**底層原理探討與權衡**
FastAPI 等框架內部會自動將 `def`（而非 `async def`）定義的路由函數丟進 thread pool 中執行，以防止阻塞主事件循環。這是一個折衷方案：你獲得了開發便利性，但犧牲了極高併發下的資源效率（執行緒上限通常為 40 左右）。

---

### 主題 4：警惕「重入性」與「死鎖」，在多鎖場景下保持獲取順序一致

**核心概念簡述**
當一個執行緒試圖獲取它已經持有的非重入鎖（Normal Lock）時，會發生自我死鎖。此外，若兩個執行緒互相等待對方手中的鎖，則會造成系統永久停擺（Deadlock）。

**程式碼範例**

```python
# Bad: 使用普通 Lock 可能導致遞迴調用時自我鎖死
from threading import Lock
lock = Lock()

def recursive_task(n):
    with lock:
        if n > 0: recursive_task(n - 1) # 這裡會死鎖

# Better: 針對遞迴場景使用 RLock (Reentrant Lock)
from threading import RLock
reentrant_lock = RLock()

def safe_recursive_task(n):
    with reentrant_lock: # 同一個執行緒可以多次進入
        if n > 0: safe_recursive_task(n - 1)
```

**底層原理探討與權衡**
處理死鎖的最優策略是「鴕鳥演算法」（忽略它，直到發生頻率高到需要重構）或者「鎖排序」（始終按固定順序獲取鎖 A -> 鎖 B）。

---

### 主題 5：在特定高效能庫（如 NumPy/hashlib）中大膽使用多執行緒進行運算

**核心概念簡述**
雖然前述提到 Python 程式碼受 GIL 限制，但許多 C 擴展庫在執行耗時運算時會釋放 GIL。例如 `hashlib` 的加密函數與 `NumPy` 的矩陣運算，能在多執行緒中實現「真正的並行」。

**適用場景之「拇指法則」**
*   **規則**：如果你使用的是底層由 C/C++/Fortran 實作的科學運算庫，多執行緒通常能有效利用多核 CPU。
*   **案例**：將 `NumPy` 矩陣按行切分到不同執行緒進行 `mean()` 運算，可顯著提升效能。

---

### 小結

多執行緒在 Python 中主要用於解決 I/O 密集型任務的併發問題。架構師必須嚴格管理共享狀態，並優先使用執行緒安全的同步原語。同時，利用執行緒池能有效降低系統開銷。對於 CPU 密集型任務，則應考慮多進程以突破 GIL 限制。


## Part 2. 多進程與並行 (Multiprocessing & Parallelism)

在 Python 併發編程的版圖中，「多進程（Multiprocessing）」是唯一能突破全域解釋器鎖（GIL）限制、達成真正的「並行（Parallelism）」的手段。身為架構師，我們必須明確區分何時該使用輕量級的協程（Coroutines），何時該動用重量級的多進程。

以下是針對多進程在並行架構中的實戰主題：

---

### 主題 1：優先將 CPU 密集型任務委派給多進程

**核心概念簡述**
Python 的 GIL 確保同一時間只有一個執行緒能執行 bytecode。對於像數學計算、圖像處理或大規模數據轉換等「計算密集型（CPU-bound）」任務，增加執行緒只會因競爭鎖而降低效率。多進程透過產生多個獨立的 Python 解釋器實例，讓每個進程擁有自己的 GIL，從而在多核心 CPU 上實現真正的並行。

**程式碼範例**

```python
# Bad: 在單執行緒或多執行緒中執行運算，受限於 GIL，無法利用多核
def heavy_computation(data):
    # 執行複雜的數值分析
    return sum(i * i for i in range(10**7))

data_list = [1, 2, 3] # 範例數據
results = [heavy_computation(d) for d in data_list]

# Better: 使用 ProcessPoolExecutor 達成並行運算
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor() as executor:
    # 每個任務會在獨立的進程中同時運行
    results = list(executor.map(heavy_computation, data_list))
```

**底層原理探討與權衡**
多進程的本質是硬體資源的垂直擴展。雖然並行能顯著縮短作業時間，但進程的建立與「上下文切換（Context Switching）」成本遠高於執行緒。如果任務本身執行時間極短（例如微秒級），進程間通訊的開銷（如序列化）可能會抵消並行的收益。

---

### 主題 2：在 AsyncIO 體系中利用 `run_in_executor` 防止事件循環阻塞

**核心概念簡述**
`asyncio` 的事件循環是單執行緒的，任何長耗時的計算都會導致整個循環「窒息」，無法響應其他 I/O 事件。架構上應將事件循環視為「調度員」，當遇到 CPU 密集型工作時，必須將其「外包」給多進程執行器（Process Pool Executor）。

**程式碼範例**

```python
# Bad: 在異步函式中直接執行 CPU 密集任務，鎖死 Event Loop
async def handle_request_bad(data):
    result = compute_pi_to_million_digits(data) # 阻塞點！
    return {"result": result}

# Better: 將計算任務派發至進程池
import asyncio
from concurrent.futures import ProcessPoolExecutor

def compute_pi_to_million_digits(data):
    # 模擬 CPU 密集任務
    return 3.14

executor = ProcessPoolExecutor()

async def handle_request_good(data):
    loop = asyncio.get_running_loop()
    # 將計算交給進程池，await 會釋放控制權讓 Loop 處理其他 I/O
    result = await loop.run_in_executor(executor, compute_pi_to_million_digits, data)
    return {"result": result}
```

**底層原理探討與權衡**
透過 `run_in_executor`，我們將「計算阻塞」轉化為「可等待的異步任務」。這種模式實現了 I/O 併發與 CPU 並行的完美結合。權衡點在於：進程池的大小應與 CPU 核心數匹配（通常為 `os.cpu_count()`），過度派發會引發劇烈的資源爭奪。

---

### 主題 3：優先使用訊息傳遞（Queues）而非共享記憶體

**核心概念簡述**
進程間的記憶體是完全隔離的。雖然 Python 提供了 `Value` 或 `Array` 等共享記憶體物件，但這些方法極其危險，容易引發「競爭條件（Race Condition）」且難以調試。更穩健的架構是使用 `multiprocessing.Queue`，它透過管道（Pipe）傳遞序列化後的物件，天然具備執行緒安全性。

**程式碼範例**

```python
# Bad: 使用共享記憶體，必須手動管理複雜的 Locks，容易出錯
from multiprocessing import Value, Lock
counter = Value('i', 0)
lock = Lock()

def increment():
    with lock:
        counter.value += 1

# Better: 使用 Queue 傳遞資料，解耦生產者與消費者
from multiprocessing import Queue

def process_item(item):
    pass

task_queue = Queue()
def worker(q):
    while True:
        item = q.get() # 阻塞式獲取任務
        if item is None: break
        process_item(item)
```

**底層原理探討與權衡**
`Queue` 內部使用了鎖與訊號量（Semaphores）來確保資料一致性，開發者無需處理底層同步細節。這種模式被稱為「以通訊來共享記憶體（Share memory by communicating）」，極大提升了系統的健壯性。缺點是大量的物件序列化（Pickle）會消耗額外的 CPU 與頻寬。

---

### 主題 4：適用場景之「拇指法則（Rule of Thumb）」

*   **何時使用多進程並行**：
    *   數學運算、數據加密、大型矩陣操作（如 NumPy 未釋放 GIL 時）。
    *   需要處理海量數據的 MapReduce 工作流。
    *   整合非異步友好的重量級 C 擴充程式庫。
*   **例外與警告**：
    *   **資料量過大**：若進程間傳遞的物件達到數 GB，Pickle 的開銷可能會拖垮效能，此時應考慮將資料預存在 Redis 或分佈式文件系統中。
    *   **交互頻繁**：如果子進程需要與主進程進行毫秒級的頻繁互動，進程間通訊的延遲將成為瓶頸，應優先考慮執行緒或重新設計演算法。

---

### 小結
多進程是解決 Python 並行問題的「重型裝甲」。架構師的職責是精準判斷任務的「束縛點（Bounding Factor）」：如果是 I/O-bound，請留在執行緒或協程；如果是 CPU-bound，請果斷將其切割並投射到多個進程中。記住：**真正的並行是拿記憶體與上下文開銷去換取計算時間的槓桿**。

## Part 3. GIL、併發與並行 (GIL, Concurrency & Parallelism)

在 Python 的異步 I/O 與併發模型中，「全域解釋器鎖 (Global Interpreter Lock, GIL)」是一個無法迴避的底層機制。身為架構師，我們必須明確區分「併發（Concurrency）」與「並行（Parallelism）」的物理邊界。根據來源資料，GIL 決定了我們如何選擇多執行緒、多行程或協程來優化系統效能。

以下是針對 GIL 在併發與並行脈絡下的實戰主題：

---

### 主題 1：認清 GIL 是「單行程內」並行 (Parallelism) 的物理障礙

**核心概念簡述**
GIL 是 CPython 為了確保執行緒安全（Thread-safety）而設計的一種互斥鎖，它防止多個執行緒同時執行 Python 字節碼。這意味著即便在多核心 CPU 上，一個 Python 行程在任何瞬間只能有一個執行緒在運行。因此，Python 的多執行緒只能達成「併發」（時間分片式的交錯執行），而無法達成計算意義上的「並行」。

**程式碼範例**

```python
# Bad: 期望透過多執行緒並行計算 CPU 密集任務
# 受限於 GIL，這會比單執行緒更慢（因為有執行緒切換開銷）
import threading
def cpu_heavy_task():
    sum(i * i for i in range(10**7))

t1 = threading.Thread(target=cpu_heavy_task)
t2 = threading.Thread(target=cpu_heavy_task)
t1.start(); t2.start() # 兩者爭奪同一個 GIL

# Better: 使用多行程 (Multiprocessing) 達成真正的並行
# 每個行程擁有獨立的 Python 解釋器與 GIL
from multiprocessing import Process
p1 = Process(target=cpu_heavy_task)
p2 = Process(target=cpu_heavy_task)
p1.start(); p2.start() # 在不同核心上同時運行
```

**底層原理探討與權衡**
GIL 存在的初衷是簡化 CPython 的記憶體管理，特別是針對「引用計數（Reference Counting）」的執行緒安全問題。雖然它限制了 CPU 密集型任務的擴展性，但它能保護開發者免於處理極其複雜的記憶體競爭問題。

---

### 主題 2：針對 I/O 密集型任務，利用「GIL 釋放」機制實作併發

**核心概念簡述**
雖然 GIL 限制了字節碼執行，但當 Python 執行 I/O 操作（如網路請求、磁碟讀寫）時，會調用底層作業系統的系統調用（System Calls），此時 Python 會「釋放」GIL。這使得多執行緒在處理「阻塞式 I/O」時依然具備優勢，因為多個執行緒可以同時等待不同的 I/O 事件完成。

**程式碼範例**

```python
# Bad: 在異步函式中誤用同步阻塞庫，雖有 GIL 釋放，但會鎖死 Event Loop
async def fetch_data_bad():
    import requests
    # 這裡雖然釋放了 GIL 給其他 Thread，但 Event Loop 被當前任務卡死
    return requests.get("https://api.com")

# Better: 使用 asyncio.to_thread 將阻塞 I/O 委派給執行緒池
# 這樣 GIL 被釋放後，Event Loop 仍能在主執行緒處理其他工作
async def fetch_data_correctly():
    import asyncio
    import requests
    # 透過預設執行緒池處理，讓 I/O 併發發生
    return await asyncio.to_thread(requests.get, "https://api.com")
```

**底層原理探討與權衡**
I/O 併發的效能來自於「等待」時間的重疊。雖然執行緒能解決阻塞庫的問題，但其開銷（Context Switch）仍大於協程。除非必須使用不支援 `async` 的第三方庫，否則應優先考慮以 `asyncio` 實作單執行緒併發，因為協程切換完全不涉及 OS 核心的上下文切換，效率更高。

---

### 主題 3：特定科學運算應考慮能自動釋放 GIL 的 C 擴展庫

**核心概念簡述**
並非所有的 CPU 密集工作在執行緒中都會受阻。許多高效能庫（如 NumPy 或 hashlib）是使用 C 語言編寫的，它們在執行密集的矩陣運算或雜湊計算時會主動釋放 GIL。在這種特殊場景下，多執行緒可以達成真正的並行。

**程式碼範例**

```python
# Better: 利用 NumPy 在執行緒中並行處理數據
# NumPy 內部的 C 代碼會釋放 GIL，讓多核心同時運算
import numpy as np
from concurrent.futures import ThreadPoolExecutor

large_matrix_chunks = [np.random.rand(1000, 1000) for _ in range(4)]

def compute_mean(data_chunk):
    return np.mean(data_chunk) # NumPy 運算期間 GIL 是釋放的

with ThreadPoolExecutor() as executor:
    results = list(executor.map(compute_mean, large_matrix_chunks))
```

**適用場景之「拇指法則」**
*   **規則**：若工作負載主要發生在釋放了 GIL 的 C/C++ 擴展中，使用多執行緒（Thread Pool）通常比多行程更節省記憶體。
*   **例外**：若運算邏輯中包含大量 Python 原生對象（如 List 遍歷、Dict 操作），則必須回歸多行程模型。

---

### 主題 4：在高性能服務架構中，以「多行程 + 多事件循環」組合繞過 GIL

**核心概念簡述**
對於需要極致吞吐量的服務，單個事件循環（Event Loop）受限於單執行緒的 CPU 瓶頸（即便 I/O 是非阻塞的）。來源資料建議採用「多行程」架構，在每個核心上啟動一個獨立的進程，每個進程運行一個獨立的事件循環。

**對比範例 (架構層級)**

*   **Bad**: 使用單個 FastAPI 實例處理所有流量，導致複雜的 JSON 解析或數據封裝（CPU 任務）成為 GIL 瓶頸。
*   **Better**: 透過 Gunicorn 配合 Uvicorn 啟動多個 Worker 行程。每個行程有自己的 GIL 與 Event Loop，實現真正的多核心負載均衡。

**權衡探討**
這種做法的代價是「內存開銷」。每個行程都會載入完整的應用程式、AI 模型副本與緩存。在資源受限的環境下，建議將「模型推理」外包給專用的外部推理伺服器（如 vLLM 或 BentoML），讓 FastAPI 僅作為輕量級的 I/O 調度層。

---

### 小結

**GIL 決定了 Python 併發工具的選擇路徑**。解決 I/O 瓶頸首選協程（AsyncIO）以節省資源；解決 CPU 瓶頸必須透過多行程（Multiprocessing）以獲取核心並行。架構師不應抱怨 GIL 的存在，而應透過精確的任務劃分與平台化（如 Vertex AI 或 BentoML）來規避其副作用。

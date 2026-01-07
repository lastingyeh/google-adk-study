import ast
import datetime
import json
import re


def validate_code_safety(code: str) -> list:
    """
    使用 AST（抽象語法樹）分析程式碼以偵測潛在的不安全操作。
    如果發現不安全的模式，會回傳錯誤訊息列表。
    這個函式主要用於靜態分析，防止惡意或危險的程式碼被執行。
    """
    errors = []

    # 排除不允許被匯入的模組
    unsafe_modules = {
        "os",
        "sys",
        "subprocess",
        "shutil",
        "pickle",
        "importlib",
        "socket",
        "http",
        "urllib",
        "requests",
    }

    # 排除不允許被呼叫的內建函式
    unsafe_functions = {"eval", "exec", "open", "compile", "__import__"}

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        # 如果程式碼有語法錯誤，直接回傳錯誤訊息
        return [f"產生的程式碼有語法錯誤: {e}"]

    for node in ast.walk(tree):
        # 檢查 import 語句
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in unsafe_modules:
                    errors.append(
                        f"安全性違規：不允許匯入受限制的模組 '{alias.name}'。"
                    )

        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in unsafe_modules:
                errors.append(
                    f"安全性違規：不允許從受限制的模組 '{node.module}' 匯入。"
                )

        # 檢查函式呼叫
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in unsafe_functions:
                    errors.append(
                        f"安全性違規：不允許使用受限制的函式 '{node.func.id}'。"
                    )

    return errors


def run_simulation(policy_code: str, metadata: list) -> list:
    violations = []
    # 若 policy_code 為空或尚未設定 API 金鑰，回傳設定錯誤
    if not policy_code or policy_code.startswith("# API key not configured"):
        violations.append({"policy": "設定錯誤", "violation": policy_code})
        return violations

    # 若 policy_code 以錯誤訊息開頭，回傳執行錯誤
    if policy_code.startswith("# Error:"):
        violations.append({"policy": "執行錯誤", "violation": policy_code})
        return violations

    # 1. 靜態安全性分析
    # 先檢查程式碼是否有潛在安全風險
    security_errors = validate_code_safety(policy_code)
    if security_errors:
        for err in security_errors:
            violations.append({"policy": "安全性違規", "violation": err})
        return violations

    # 2. 準備受限制的執行環境
    # 僅允許特定模組與內建函式
    safe_globals = {
        "__builtins__": {
            "abs": abs,  # 絕對值
            "all": all,  # 全部為真
            "any": any,  # 任一為真
            "bool": bool,  # 布林值
            "dict": dict,  # 字典
            "enumerate": enumerate,  # 列舉
            "filter": filter,  # 過濾
            "float": float,  # 浮點數
            "int": int,  # 整數
            "len": len,  # 長度
            "list": list,  # 清單
            "map": map,  # 對映
            "max": max,  # 最大值
            "min": min,  # 最小值
            "range": range,  # 範圍
            "set": set,  # 集合
            "sorted": sorted,  # 排序
            "str": str,  # 字串
            "sum": sum,  # 總和
            "tuple": tuple,  # 元組
            "zip": zip,  # 打包
            "isinstance": isinstance,  # 型別判斷
            "__import__": __import__,  # 匯入（受控）
        },
        "json": json,  # JSON 處理
        "re": re,  # 正則表達式
        "datetime": datetime,  # 日期時間
    }

    try:
        # 產生的 policy_code 必須定義一個名為 check_policy 的函式，
        # 並接受 metadata 作為參數。
        # 這裡在受限制的命名空間下執行程式碼。
        exec(policy_code, safe_globals)

        if "check_policy" in safe_globals:
            # 執行產生的 check_policy 函式，回傳違規清單
            check_policy_func = safe_globals["check_policy"]
            violations = check_policy_func(metadata)  # type: ignore[operator]
        else:
            violations.append(
                {
                    "policy": "執行錯誤",
                    "violation": "執行政策程式碼時發生錯誤：找不到 'check_policy' 函式。",
                }
            )
    except Exception as e:
        violations.append(
            {
                "policy": "執行錯誤",
                "violation": f"執行政策程式碼時發生錯誤：{e}",
            }
        )

    return violations

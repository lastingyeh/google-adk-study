# 啟用偵錯模式，執行指令時會顯示指令內容
set -x

# 定義執行單元測試的函式
run_unit_tests(){
    # 重點：執行此腳本前，請確認您目前位於 brand-search-optimization 目錄中
    # 並且已在 .env 檔案中設定 ENABLE_UNIT_TEST_MODE=1
    # 將目前目錄加入 PYTHONPATH，以便 Python 能夠找到專案模組
    export PYTHONPATH="$PYTHONPATH:."
    # 使用 pytest 執行 tests/ 目錄下的所有單元測試
    pytest tests/
}

# 呼叫函式以執行單元測試
run_unit_tests

# 以成功狀態碼 0 結束腳本，表示執行成功
exit 0
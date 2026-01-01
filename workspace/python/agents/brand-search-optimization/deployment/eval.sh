# 腳本除錯：顯示執行的指令
set -x

# 準備函式：設定執行環境
prepare(){
    # 建立一個空的 __init__.py 檔案，將當前目錄標示為一個 Python 套件
    touch __init__.py
    # 將當前目錄加入到 PYTHONPATH 環境變數中，讓 Python 直譯器可以找到模組
    export PYTHONPATH=:.
}

# 移除 selenium 函式：刪除 selenium 目錄
remove_selenium(){
    rm -rf selenium
}

# 執行評估函式
run_eval(){
    # 使用 adk 工具執行評估
    adk eval \
        brand_search_optimization \
        eval/data/eval_data1.evalset.json \
        --config_file_path eval/data/test_config.json
}

# 主函式
main(){
    echo "
    您必須在 brand-search-optimization 目錄下，然後執行
    # sh deployment/eval.sh
    "
    # 呼叫準備函式
    prepare
    # 呼叫移除 selenium 函式
    remove_selenium
    # 呼叫執行評估函式
    run_eval
}

# 執行主函式
main

# 正常退出腳本
exit 0

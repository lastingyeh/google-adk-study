# -x: 在執行指令前，會先顯示該指令及其參數。
# -e: 如果指令的返回碼不是 0，則立即退出腳本。
set -x
set -e

# 判斷此腳本所在的目錄
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# 假設專案根目錄是腳本目錄的上一層
ROOT_DIR=$(dirname "$SCRIPT_DIR")

# 安裝先決條件的函式
install_prereqs(){
    echo "--- 切換到根目錄 ($ROOT_DIR) 以安裝先決條件 ---"
    # 在子 shell 中執行 poetry install，會先切換目錄
    (cd "$ROOT_DIR" && poetry install)
    echo "--- 先決條件安裝完成 ---"
}

# 填入 BigQuery 資料的函式
populate_bq_data(){
    echo "--- 切換到根目錄 ($ROOT_DIR) 以填入 BigQuery 資料 ---"
    # 在子 shell 中從根目錄執行 python 腳本
    (cd "$ROOT_DIR" && python -m deployment.bq_populate_data)
    echo "--- BigQuery 資料填入完成 ---"
}

# 主函式
main(){
    # 執行安裝先決條件
    install_prereqs
    # 執行填入 BigQuery 資料
    populate_bq_data
}

# 執行主函式
main

# 正常退出腳本
exit 0

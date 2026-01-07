## 任務實作

### 任務列表

- [x] 任務一：執行測試
  - [x] 執行 `make test`
  - [x] 修正 `pyproject.toml` 中的相依性
  - [x] 建立 `PYRPOJECT.md` 文件輔助說明
- [x] 任務二：地端執行
  - [x] 將 `make debug-playground` 加入 `Makefile`
  - [x] 將 `make debug-backend` 加入 `Makefile`
  - [x] 執行 `make playground` 以測試地端執行
  - [x] 建立 `.vscode/launch.json` 以支援 VSCode 偵錯
- [x] 任務三：LINT 工具
  - [x] 在 `pyproject.toml` 中加入 LINT 工具相依性
  - [x] 增加 `LINT.md` 文件輔助說明
  - [x] 執行 LINT 工具並修正程式碼問題
- [x] 任務四：理解地端執行做了什麼
  - [x] 分析 `policy_as_code_agent/.adk/session.db` 建立原因，參考[文件連結](./CODE.md)
- [x] 任務五：建立完整 Docker Image 建置與推送流程
  - [x] 建立 `DOCKET.md` 文件輔助說明
  - [x] 更新 `Makefile` 以支援 Docker 映像建置、推送與本地測試
  - [x] 進行 Terraform 執行環境建置與銷毀測試
    - [x] 更新 `Makefile` 以支援 Terraform 環境建置與銷毀

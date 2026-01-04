# Go 安裝指南
> 更新日期：2026 年 1 月 4 日

## 建立新的 Go 模組

如果您正在開始一個新專案，您可以建立一個新的 Go 模組：

`go mod init example.com/my-agent`

### 安裝 ADK

若要將 ADK 新增至您的專案，請執行以下指令：

`go get google.golang.org/adk`

這會將 ADK 作為依賴項新增到您的 `go.mod` 檔案中。

（可選）透過檢查您的 `go.mod` 檔案中是否有名為 `google.golang.org/adk` 的條目來驗證您的安裝。

---

### 重點說明

*   `go mod init`：此指令會初始化一個新的 Go 模組。模組是 Go 管理依賴項的方式。`example.com/my-agent` 應該替換為您自己的模組路徑。
*   `go get`：此指令會擷取指定的套件並將其新增為專案的依賴項。
*   `go.mod`：這是 Go 模組的定義檔案，其中包含模組路徑、Go 版本以及所需的依賴項列表。

### 參考資源

*   [ADK Go Repository](https://github.com/google/adk-go)
*   [Go Modules 官方文件](https://go.dev/ref/mod)
*   [ADK for Go 套件](https://pkg.go.dev/google.golang.org/adk)
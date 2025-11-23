# 教學 23 快速參考卡

**列印此頁或加入書籤以便快速存取！**

---

## 🚀 快速開始（選擇您的路徑）

### 1. **我想現在立刻部署** ⚡
```bash
# 5 分鐘上線生產環境
adk deploy cloud_run --project YOUR_PROJECT --region us-central1
```
👉 接著：閱讀 [DEPLOYMENT_CHECKLIST.md](tutorial_implementation/tutorial23/DEPLOYMENT_CHECKLIST.md)

### 2. **我需要合規性 (FedRAMP)** 🔐
```bash
# Agent Engine 用於合規性
adk deploy agent_engine --project YOUR_PROJECT --region us-central1
```
👉 接著：閱讀 [SECURITY_VERIFICATION.md](tutorial_implementation/tutorial23/SECURITY_VERIFICATION.md)

### 3. **我有 Kubernetes** ⚙️
```bash
# 部署到 GKE
adk deploy gke
kubectl apply -f deployment.yaml
```
👉 接著：參閱 MIGRATION_GUIDE.md 以進行安全部署

### 4. **我需要自訂驗證** 🔑
```bash
# 使用教學 23 模式 + Cloud Run
cd tutorial_implementation/tutorial23
make demo
```
👉 接著：遵循 DEPLOYMENT_CHECKLIST.md

### 5. **我只是在學習** 📚
```bash
# 先在本地執行
adk api_server --port 8080
```
👉 接著：閱讀 docs/tutorial/23_production_deployment.md

---

## 💰 快速成本參考

| 平台 | 成本/月 | 設定時間 | 最適合 |
|----------|-----------|-----------|----------|
| **Local** | $0 | <1 分鐘 | 學習 |
| **Cloud Run** | $40-50 | 5 分鐘 | ✅ 大多數生產應用 |
| **Agent Engine** | ~$527 | 10 分鐘 | 合規性 (FedRAMP) |
| **GKE** | $200-500+ | 20+ 分鐘 | 進階控制 |

---

## 📋 部署前檢查清單

在您部署到任何地方之前：

- [ ] 環境變數已設定
- [ ] 秘密在 Secret Manager 中（不在程式碼中！）
- [ ] API 金鑰已輪替
- [ ] 健康端點在本地運作正常
- [ ] 日誌已設定
- [ ] 監控警報已設定

**完整檢查清單**：[DEPLOYMENT_CHECKLIST.md](tutorial_implementation/tutorial23/DEPLOYMENT_CHECKLIST.md)

---

## 🔐 部署後驗證

部署後：

1. **測試它是否運作**
   ```bash
   curl $SERVICE_URL/health
   ```

2. **驗證它是否安全**
   ```bash
   # 參閱 SECURITY_VERIFICATION.md 進行平台特定檢查
   ```

3. **檢查日誌**
   ```bash
   gcloud logging read "resource.service.name=agent" --limit 10
   ```

4. **監控指標**（Cloud Logging 儀表板）

---

## 🔄 在平台之間移動？

**完整指南**：[MIGRATION_GUIDE.md](tutorial_implementation/tutorial23/MIGRATION_GUIDE.md)

**常見路徑**：
- Local → Cloud Run (15 分鐘)
- Cloud Run → Agent Engine (30 分鐘)
- Cloud Run → GKE (60 分鐘)
- GKE → Cloud Run (15 分鐘)

---

## 💡 常見問題解答

**Q: 我應該選擇哪個平台？**
A: 請閱讀主教學中的[決策架構](docs/tutorial/23_production_deployment.md#-decision-framework-choose-your-platform)。

**Q: 內建伺服器安全嗎？**
A: 是的 - 安全性由平台（Cloud Run、Agent Engine、GKE）處理。請閱讀 [SECURITY_RESEARCH_SUMMARY.md](SECURITY_RESEARCH_SUMMARY.md)。

**Q: 費用是多少？**
A: 對於 Cloud Run 上的中小型應用程式，通常為 $40-50/月。詳情請參閱 [COST_BREAKDOWN.md](tutorial_implementation/tutorial23/COST_BREAKDOWN.md)。

**Q: 我以後可以遷移嗎？**
A: 是的！您的代理程式碼保持不變。請參閱 [MIGRATION_GUIDE.md](tutorial_implementation/tutorial23/MIGRATION_GUIDE.md)。

**Q: 我何時需要自訂伺服器？**
A: 僅在您需要自訂驗證或非常特定的模式時。對於大多數使用者：使用 Cloud Run + IAM。

---

## 📚 文件導覽

| 文件 | 目的 | 閱讀時間 |
|----------|---------|--------------|
| [主教學](docs/tutorial/23_production_deployment.md) | 所有平台概覽 | 15-20 分鐘 |
| [決策架構](docs/tutorial/23_production_deployment.md#-decision-framework) | 選擇您的平台 | 2 分鐘 |
| [SECURITY_VERIFICATION.md](tutorial_implementation/tutorial23/SECURITY_VERIFICATION.md) | 驗證您的部署是否安全 | 10 分鐘 |
| [DEPLOYMENT_CHECKLIST.md](tutorial_implementation/tutorial23/DEPLOYMENT_CHECKLIST.md) | 逐步驗證 | 20 分鐘 |
| [MIGRATION_GUIDE.md](tutorial_implementation/tutorial23/MIGRATION_GUIDE.md) | 在平台之間移動 | 30 分鐘 |
| [COST_BREAKDOWN.md](tutorial_implementation/tutorial23/COST_BREAKDOWN.md) | 預算規劃 | 15 分鐘 |

---

## 🧪 測試您的設定

```bash
# 執行所有測試
cd tutorial_implementation/tutorial23
make test

# 執行特定測試
pytest tests/test_agent.py -v

# 檢查覆蓋率
pytest tests/ --cov=production_agent
```

**預期結果**：40/40 測試通過 ✅

---

## 🆘 故障排除

**問題**：無法存取已部署的服務
**解決方案**：檢查 SECURITY_VERIFICATION.md → "Issue: Unauthenticated access allowed"

**問題**：已部署但沒有流量顯示
**解決方案**：檢查 DEPLOYMENT_CHECKLIST.md → "Post-deployment verification"

**問題**：想切換平台
**解決方案**：參閱 MIGRATION_GUIDE.md 以了解您的遷移路徑

**問題**：擔心安全性
**解決方案**：閱讀 SECURITY_RESEARCH_SUMMARY.md，然後遵循 SECURITY_VERIFICATION.md

---

## 🔗 所有資源

### 快速入門
- 🎯 [主教學](docs/tutorial/23_production_deployment.md)
- 📖 [README](tutorial_implementation/tutorial23/README.md)

### 部署與驗證
- ✅ [部署檢查清單](tutorial_implementation/tutorial23/DEPLOYMENT_CHECKLIST.md)
- 🔐 [安全性驗證](tutorial_implementation/tutorial23/SECURITY_VERIFICATION.md)

### 規劃與遷移
- 💰 [成本細目](tutorial_implementation/tutorial23/COST_BREAKDOWN.md)
- 🔄 [遷移指南](tutorial_implementation/tutorial23/MIGRATION_GUIDE.md)

### 安全性與最佳實務
- 📋 [安全性研究摘要](SECURITY_RESEARCH_SUMMARY.md)
- 🔍 [詳細安全性分析](SECURITY_ANALYSIS_ALL_DEPLOYMENT_OPTIONS.md)
- 📖 [FastAPI 最佳實務](tutorial_implementation/tutorial23/FASTAPI_BEST_PRACTICES.md)

### 實作
- 💻 [程式碼](tutorial_implementation/tutorial23/)
- 🧪 [測試](tutorial_implementation/tutorial23/tests/)

---

## ⏱️ 時間估算

| 任務 | 時間 | 難度 |
|------|------|------------|
| 閱讀決策架構 | 2 分鐘 | 簡單 |
| 部署到 Cloud Run | 5 分鐘 | 簡單 |
| 部署到 Agent Engine | 10 分鐘 | 簡單 |
| 部署到 GKE | 20+ 分鐘 | 中等 |
| 安全性驗證 | 10 分鐘 | 簡單 |
| 預算規劃 | 10 分鐘 | 簡單 |
| 平台遷移 | 15-60 分鐘 | 中等 |

---

## ✅ 成功指標

**當發生以下情況時，您已準備好進入生產環境**：
- ✅ 部署檢查清單已完成
- ✅ 健康端點有回應
- ✅ 日誌出現在 Cloud Logging 中
- ✅ 安全性驗證通過
- ✅ 監控/警報已設定
- ✅ 成本監控已設定

---

**需要協助嗎？** 請查看上方的相關指南，或重新閱讀[主教學](docs/tutorial/23_production_deployment.md)。

**發現問題？** 本教學已通過測試 (40/40 測試通過) - 如果某些功能無法運作，請檢查故障排除部分。

**準備部署了嗎？** 從上方的快速開始選擇您的平台！🚀

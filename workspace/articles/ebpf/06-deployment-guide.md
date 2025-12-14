## 🧑‍💻 Terraform: 建立 GKE 叢集與必要資源

存成 `main.tf` 或依模組拆分：

```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

resource "google_container_cluster" "gke_cluster" {
  name               = var.cluster_name
  location           = var.zone
  remove_default_node_pool = true
  initial_node_count = 1

  network    = var.vpc
  subnetwork = var.subnet

  # Enable Dataplane V2 for eBPF datapath (GKE support)
  enable_dataplane_v2 = true

  node_config {
    machine_type = "e2-standard-4"
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
  }
}

resource "google_container_node_pool" "primary_nodes" {
  cluster  = google_container_cluster.gke_cluster.name
  location = var.zone
  name     = "primary-pool"

  node_config {
    machine_type = "e2-standard-4"
    oauth_scopes = ["cloud-platform"]
  }

  initial_node_count = 3
}
```

👉 這裡透過變數管理參數，如 `project_id`, `region`, `zone`, `vpc`, `subnet`, `cluster_name` 等。
GKE 的 `enable_dataplane_v2 = true` 能啟用基於 eBPF datapath network support。

---

## 📦 Kubernetes Provider（Terraform）

建立 `terraform.tfvars` 之後，可在 TF 中加入 Helm Provider：

```hcl
provider "kubernetes" {
  host                   = google_container_cluster.gke_cluster.endpoint
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(google_container_cluster.gke_cluster.master_auth.0.cluster_ca_certificate)
}

provider "helm" {
  kubernetes {
    host                   = google_container_cluster.gke_cluster.endpoint
    token                  = data.google_client_config.default.access_token
    cluster_ca_certificate = base64decode(google_container_cluster.gke_cluster.master_auth.0.cluster_ca_certificate)
  }
}
```

---

## 🛟 Helm Chart: 安裝 Cilium + Tetragon

> **前置條件**：先確保 GKE 叢集已建好，並 Terraform 已初始化 Helm 設定。

---

### 1) 安裝 **Cilium**

```hcl
resource "helm_release" "cilium" {
  name       = "cilium"
  repository = "https://helm.cilium.io/"
  chart      = "cilium"
  namespace  = "kube-system"
  version    = "1.15.0" # 可根據需求調整

  values = [
    <<EOF
# 支援 Dataplane V2 (eBPF) 並啟用基本 Network Policy
global:
  cni:
    enabled: true

datapath:
  enableBPF: true

# NetworkPolicy & 日誌
security:
  enableEnvoyMetrics: true

hubble:
  enabled: true
  metrics:
    - dns
    - drop
    - tcp
    - http
EOF
  ]
}
```

**說明**：Cilium 會作為 eBPF CNI 安裝在 GKE，並可啟用 Hubble 來收集網路可觀測性。
進一步的網路控管策略仍可用 Kubernetes NetworkPolicy + CiliumExtensions。

---

### 2) 安裝 **Tetragon（eBPF Security）**

Tetragon 是基於 eBPF 的 Kubernetes-aware 安全觀測/執行工具，能追蹤進程執行、系統調用等行為。([Tetragon][2])

```hcl
resource "helm_release" "tetragon" {
  name       = "tetragon"
  repository = "https://helm.cilium.io/"
  chart      = "tetragon"
  namespace  = "kube-system"
  version    = "1.6.0"

  values = [
    <<EOF
# 如果需要，可以調整 Host 參數
tetragon:
  enabled: true
# 可自訂 policy
# 更多配置可參考官方文檔示例
EOF
  ]
}
```

---

## 🧾 範例 Kubernetes TracingPolicy（基本安全策略）

以下是一個 **TracingPolicy** 範例，示範如何利用 Tetragon 的 CRD 來監控並封鎖敏感行為（如訪問敏感文件）：

> **檔案名**：`tetragon-file-monitor-policy.yaml`

```yaml
apiVersion: cilium.io/v1alpha1
kind: TracingPolicy
metadata:
  name: file-monitor-enforce
spec:
  events:
  - type: "process"
    process:
      matchArguments:
      - index: 0
        type: string
  file:
    path:
      prefix: "/etc/shadow"
  action:
    kill: {}
```

這個策略 **在 Kernel 層攔截讀 `/etc/shadow` 的行為並 kill 該 process**。可延伸到更多事件（例如 execve, network connect 等）。([Is It Observable][3])

---

## 🔧 安裝 Policy via Terraform

```hcl
resource "kubernetes_manifest" "file_monitor_policy" {
  manifest = yamldecode(file("${path.module}/tetragon-file-monitor-policy.yaml"))
}
```

---

## 📊 連接到 Observability 與 Alert

建議配合 Logging / Monitoring：

```hcl
resource "google_logging_metric" "tetragon_logs" {
  name   = "tetragon_events"
  filter = "resource.type = \"k8s_container\" AND labels.k8s-pod/tetragon"
}
```

這樣 Tetragon 的事件會被導到 Cloud Logging，後續可以建 Alert、Dashboard。

---

## 🚀 後續擴充方向

| 擴充項目                  | 說明                               |
| ------------------------- | ---------------------------------- |
| OPA Gatekeeper / Policies | 加強策略治理 framework             |
| GitOps（ArgoCD / Flux）   | 將 Helm 與 Policy 管理納入生命週期 |
| Integrate SIEM            | Cloud Logging → BigQuery → SIEM    |
| AI Security Copilot       | 透過 RAG/LLM 自動分析安全事件      |

---

## 📌 小結

這份範本包含：

✔ Terraform 建立 GKE 叢集並啟用 eBPF datapath
✔ Helm 安裝 Cilium + Tetragon（並開啟 eBPF Runtime Security）([Tetragon][2])
✔ Kubernetes TracingPolicy 样例（敏感行為攔截）
✔ Terraform 導入 Policy 與 Logging 集成

---
## 參考

[1]: https://en.wikipedia.org/wiki/Cilium_%28computing%29?utm_source=chatgpt.com "Cilium (computing)"
[2]: https://tetragon.io/docs/getting-started/install-k8s/?utm_source=chatgpt.com "Quick Kubernetes Install"
[3]: https://isitobservable.io/observability/kubernetes/master-kubernetes-security-with-tetragon?utm_source=chatgpt.com "Master Kubernetes Security with Tetragon"

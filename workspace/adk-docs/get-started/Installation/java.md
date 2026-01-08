# Java 安裝指南

🔔 `更新日期：2026 年 1 月 4 日`

您可以使用 maven 或 gradle 來新增 `google-adk` 和 `google-adk-dev` 套件。

`google-adk` 是核心的 Java ADK 函式庫。Java ADK 還附帶一個可插拔的 SpringBoot 伺服器範例，讓您可以順暢地執行您的代理程式。這個可選的套件包含在 `google-adk-dev` 中。

## 重點說明
- **`google-adk`**: 這是 Java ADK 的核心，提供了建構代理程式所需的基本功能。
- **`google-adk-dev`**: 這是一個選用套件，包含一個 SpringBoot 伺服器，可用於在本機執行和偵錯您的代理程式。

如果您使用 maven，請將以下內容新增到您的 `pom.xml` 中：

`pom.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <groupId>com.example.agent</groupId>
  <artifactId>adk-agents</artifactId>
  <version>1.0-SNAPSHOT</version>
  <!-- 指定您將使用的 Java 版本 -->
  <properties>
    <maven.compiler.source>17</maven.compiler.source>
    <maven.compiler.target>17</maven.compiler.target>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>

  <dependencies>
    <!-- ADK 核心依賴 -->
    <dependency>
      <groupId>com.google.adk</groupId>
      <artifactId>google-adk</artifactId>
      <version>0.5.0</version>
    </dependency>
    <!-- 用於偵錯代理程式的 ADK 開發 Web UI -->
    <dependency>
      <groupId>com.google.adk</groupId>
      <artifactId>google-adk-dev</artifactId>
      <version>0.5.0</version>
    </dependency>
  </dependencies>
</project>
```

這裡有一個[完整的 pom.xml](https://github.com/google/adk-docs/tree/main/examples/java/cloud-run/pom.xml) 檔案可供參考。

如果您使用 gradle，請將依賴項新增到您的 build.gradle 中：

build.gradle

```groovy
dependencies {
    implementation 'com.google.adk:google-adk:0.2.0'
    implementation 'com.google.adk:google-adk-dev:0.2.0'
}
```

您還應該設定 Gradle 將 `-parameters` 參數傳遞給 `javac`。（或者，使用 `@Schema(name = "...")`）。

## 參考資源
- [ADK Java Repository](https://github.com/google/adk-java)
- [Maven 官方文件](https://maven.apache.org/guides/)
- [Gradle 官方文件](https://docs.gradle.org/current/userguide/userguide.html)
# 設定串流行為

> 🔔 `更新日期：2026-01-30`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/streaming/configuration/

[`ADK 支援`: `Python v0.5.0` | `Experimental`]

您可以為即時（串流）代理程式設定一些配置。

這是透過 [RunConfig](https://github.com/google/adk-python/blob/main/src/google/adk/agents/run_config.py) 進行設定的。您應該在調用 [Runner.run_live(...)](https://github.com/google/adk-python/blob/main/src/google/adk/runners.py) 時使用 RunConfig。

例如，如果您想設定語音配置，可以利用 `speech_config`。

```python
# 初始化語音配置，指定預設語音名稱為 'Aoede'
voice_config = genai_types.VoiceConfig(
    prebuilt_voice_config=genai_types.PrebuiltVoiceConfigDict(
        voice_name='Aoede'
    )
)
# 將語音配置封裝到語音設定中
speech_config = genai_types.SpeechConfig(voice_config=voice_config)
# 建立執行配置並傳入語音設定
run_config = RunConfig(speech_config=speech_config)

# 在執行即時代理程式時傳入執行配置
runner.run_live(
    ...,
    run_config=run_config,
)
```

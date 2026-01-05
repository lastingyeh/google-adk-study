<details>
<summary>範例說明</summary>

> Python

```python
from google.adk.agents import LlmAgent

story_generator = LlmAgent(
    name="StoryGenerator",
    model="gemini-2.0-flash",
    instruction="""請寫一個關於貓的短篇故事，重點主題是：{topic}。"""
)
# 若 session.state['topic'] 為 "友情"，LLM 接收到的指令將是：
# "請寫一個關於貓的短篇故事，重點主題是：友情。"
```

> typescript

```typescript
import { LlmAgent } from '@google/adk';

const storyGenerator = new LlmAgent({
  name: 'StoryGenerator',
  model: 'gemini-2.5-flash',
  instruction: '請寫一個關於貓的短篇故事，重點主題是：{topic}。',
});
```

> go

```go
func main() {
ctx := context.Background()
sessionService := session.InMemoryService()

// 1. Initialize a session with a 'topic' in its state.
_, err := sessionService.Create(ctx, &session.CreateRequest{
    AppName:   appName,
    UserID:    userID,
    SessionID: sessionID,
    State: map[string]any{
        "topic": "friendship",
    },
})
if err != nil {
    log.Fatalf("Failed to create session: %v", err)
}

// 2. Create an agent with an instruction that uses a {topic} placeholder.
//    The ADK will automatically inject the value of "topic" from the
//    session state into the instruction before calling the LLM.
model, err := gemini.NewModel(ctx, modelID, nil)
if err != nil {
    log.Fatalf("Failed to create Gemini model: %v", err)
}
storyGenerator, err := llmagent.New(llmagent.Config{
    Name:        "StoryGenerator",
    Model:       model,
    Instruction: "Write a short story about a cat, focusing on the theme: {topic}.",
})
if err != nil {
    log.Fatalf("Failed to create agent: %v", err)
}

r, err := runner.New(runner.Config{
    AppName:        appName,
    Agent:          agent.Agent(storyGenerator),
    SessionService: sessionService,
})
if err != nil {
    log.Fatalf("Failed to create runner: %v", err)
}
```

</details>
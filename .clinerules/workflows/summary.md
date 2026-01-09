任務：
- 將內容逐字完整翻譯為繁體中文
- 若原文包含程式碼區塊，請遵循以下指示：
  - 當內容範例如以下，其他語言亦同：
    ```
      === "Python"

      ```py
      # Simplified view of Runner's main loop logic
      def run(new_query, ...) -> Generator[Event]:
          # 1. Append new_query to session event history (via SessionService)
          session_service.append_event(session, Event(author='user', content=new_query))

          # 2. Kick off event loop by calling the agent
          agent_event_generator = agent_to_run.run_async(context)

          async for event in agent_event_generator:
              # 3. Process the generated event and commit changes
              session_service.append_event(session, event) # Commits state/artifact deltas etc.
              # memory_service.update_memory(...) # If applicable
              # artifact_service might have already been called via context during agent run

              # 4. Yield event for upstream processing (e.g., UI rendering)
              yield event
              # Runner implicitly signals agent generator can continue after yielding
        ```
      ```
  - 使用參考範本實現 `templates/codes-template.md` 中的格式
  - 在翻譯程式碼區塊時，請保留程式碼的語法和結構不變並加入註解
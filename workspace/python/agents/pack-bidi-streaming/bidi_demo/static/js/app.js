/**
 * app.js: ADK（Agent Development Kit，代理開發套件）雙向串流演示應用的 JS 程式碼。
 * 本檔案負責處理 WebSocket 連線、使用者介面更新、音訊/影像擷取及與伺服器的互動。
 */

/**
 * WebSocket 處理
 */

// 使用 WebSocket 連線伺服器
const userId = "demo-user"; // 預設使用者 ID
const sessionId = "demo-session-" + Math.random().toString(36).substring(7); // 隨機產生會話 ID
let websocket = null;
let is_audio = false;

// 獲取 RunConfig（執行配置）選項的核取方塊元素
const enableProactivityCheckbox = document.getElementById("enableProactivity"); // 主動性開關
const enableAffectiveDialogCheckbox = document.getElementById("enableAffectiveDialog"); // 情感對話開關

// 當 RunConfig 選項變更時重新連線 WebSocket
function handleRunConfigChange() {
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    addSystemMessage("正在使用更新後的設定重新連線...");
    addConsoleEntry('outgoing', '由於設定變更正在重新連線', {
      proactivity: enableProactivityCheckbox.checked,
      affective_dialog: enableAffectiveDialogCheckbox.checked
    }, '🔄', 'system');
    websocket.close(); // 關閉目前連線，觸發 onclose 進行重新連線
    // connectWebsocket() 將由延遲後的 onclose 處理程序呼叫
  }
}

// 為 RunConfig 核取方塊添加變更監聽器
enableProactivityCheckbox.addEventListener("change", handleRunConfigChange);
enableAffectiveDialogCheckbox.addEventListener("change", handleRunConfigChange);

// 建立帶有 RunConfig 選項作為查詢參數的 WebSocket URL
function getWebSocketUrl() {
  // HTTPS 頁面使用 wss://，HTTP 使用 ws:// (localhost 開發)
  const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const baseUrl = wsProtocol + "//" + window.location.host + "/ws/" + userId + "/" + sessionId;
  const params = new URLSearchParams();

  // 如果勾選，添加主動性 (proactivity) 選項
  if (enableProactivityCheckbox && enableProactivityCheckbox.checked) {
    params.append("proactivity", "true");
  }

  // 如果勾選，添加情感對話 (affective dialog) 選項
  if (enableAffectiveDialogCheckbox && enableAffectiveDialogCheckbox.checked) {
    params.append("affective_dialog", "true");
  }

  const queryString = params.toString();
  return queryString ? baseUrl + "?" + queryString : baseUrl;
}

// 獲取 DOM 元素
const messageForm = document.getElementById("messageForm"); // 訊息表單
const messageInput = document.getElementById("message"); // 訊息輸入框
const messagesDiv = document.getElementById("messages"); // 訊息顯示區域
const statusIndicator = document.getElementById("statusIndicator"); // 狀態指示燈
const statusText = document.getElementById("statusText"); // 狀態文字
const consoleContent = document.getElementById("consoleContent"); // 控制台內容
const clearConsoleBtn = document.getElementById("clearConsole"); // 清除控制台按鈕
const showAudioEventsCheckbox = document.getElementById("showAudioEvents"); // 顯示音訊事件開關

// 狀態追蹤變數
let currentMessageId = null;
let currentBubbleElement = null;
let currentInputTranscriptionId = null;
let currentInputTranscriptionElement = null;
let currentOutputTranscriptionId = null;
let currentOutputTranscriptionElement = null;
let inputTranscriptionFinished = false; // 追蹤此輪輸入轉錄 (Transcription) 是否完成

// 清理中日韓 (CJK) 字元之間空格的輔助函數
// 移除日語/中文/韓語字元之間的空格，同時保留拉丁文字周圍的空格
function cleanCJKSpaces(text) {
  // CJK Unicode 範圍：平假名、片假名、漢字、CJK 統一表意文字、全角形式
  const cjkPattern = /[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf\uff00-\uffef]/;

  // 移除兩個 CJK 字元之間的空格
  return text.replace(/(\S)\s+(?=\S)/g, (match, char1) => {
    // 獲取空格之後的字元
    const nextCharMatch = text.match(new RegExp(char1 + '\\s+(.)', 'g'));
    if (nextCharMatch && nextCharMatch.length > 0) {
      const char2 = nextCharMatch[0].slice(-1);
      // 如果兩個字元都是 CJK，則移除空格
      if (cjkPattern.test(char1) && cjkPattern.test(char2)) {
        return char1;
      }
    }
    return match;
  });
}

// 控制台日誌功能
function formatTimestamp() {
  const now = new Date();
  return now.toLocaleTimeString('zh-TW', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit', fractionalSecondDigits: 3 });
}

/**
 * 在介面控制台中添加一條記錄
 * @param {string} type - 類型 ('outgoing', 'incoming', 'error')
 * @param {string} content - 顯示內容
 * @param {object} data - 詳細 JSON 數據
 * @param {string} emoji - 圖示
 * @param {string} author - 來源 ('user', 'agent', 'system')
 * @param {boolean} isAudio - 是否為音訊事件
 */
function addConsoleEntry(type, content, data = null, emoji = null, author = null, isAudio = false) {
  // 如果未勾選核取方塊，則跳過音訊事件
  if (isAudio && !showAudioEventsCheckbox.checked) {
    return;
  }

  const entry = document.createElement("div");
  entry.className = `console-entry ${type}`;

  const header = document.createElement("div");
  header.className = "console-entry-header";

  const leftSection = document.createElement("div");
  leftSection.className = "console-entry-left";

  // 如果有提供則添加表情符號圖示
  if (emoji) {
    const emojiIcon = document.createElement("span");
    emojiIcon.className = "console-entry-emoji";
    emojiIcon.textContent = emoji;
    leftSection.appendChild(emojiIcon);
  }

  // 添加展開/摺疊圖示
  const expandIcon = document.createElement("span");
  expandIcon.className = "console-expand-icon";
  expandIcon.textContent = data ? "▶" : "";

  const typeLabel = document.createElement("span");
  typeLabel.className = "console-entry-type";
  typeLabel.textContent = type === 'outgoing' ? '↑ 上游 (Upstream)' : type === 'incoming' ? '↓ 下游 (Downstream)' : '⚠ 錯誤';

  leftSection.appendChild(expandIcon);
  leftSection.appendChild(typeLabel);

  // 如果有提供則添加作者徽章
  if (author) {
    const authorBadge = document.createElement("span");
    authorBadge.className = "console-entry-author";
    authorBadge.textContent = author;
    authorBadge.setAttribute('data-author', author);
    leftSection.appendChild(authorBadge);
  }

  const timestamp = document.createElement("span");
  timestamp.className = "console-entry-timestamp";
  timestamp.textContent = formatTimestamp();

  header.appendChild(leftSection);
  header.appendChild(timestamp);

  const contentDiv = document.createElement("div");
  contentDiv.className = "console-entry-content";
  contentDiv.textContent = content;

  entry.appendChild(header);
  entry.appendChild(contentDiv);

  // JSON 詳細資訊 (預設隱藏)
  let jsonDiv = null;
  if (data) {
    jsonDiv = document.createElement("div");
    jsonDiv.className = "console-entry-json collapsed";
    const pre = document.createElement("pre");
    pre.textContent = JSON.stringify(data, null, 2);
    jsonDiv.appendChild(pre);
    entry.appendChild(jsonDiv);

    // 如果有數據，使條目可點擊
    entry.classList.add("expandable");

    // 點擊時切換展開/摺疊
    entry.addEventListener("click", () => {
      const isExpanded = !jsonDiv.classList.contains("collapsed");

      if (isExpanded) {
        // 摺疊
        jsonDiv.classList.add("collapsed");
        expandIcon.textContent = "▶";
        entry.classList.remove("expanded");
      } else {
        // 展開
        jsonDiv.classList.remove("collapsed");
        expandIcon.textContent = "▼";
        entry.classList.add("expanded");
      }
    });
  }

  consoleContent.appendChild(entry);
  consoleContent.scrollTop = consoleContent.scrollHeight;
}

function clearConsole() {
  consoleContent.innerHTML = '';
}

// 清除控制台按鈕處理程序
clearConsoleBtn.addEventListener('click', clearConsole);

// 更新連線狀態 UI
function updateConnectionStatus(connected) {
  if (connected) {
    statusIndicator.classList.remove("disconnected");
    statusText.textContent = "已連線";
  } else {
    statusIndicator.classList.add("disconnected");
    statusText.textContent = "連線已斷開";
  }
}

// 建立訊息對話泡泡元素
function createMessageBubble(text, isUser, isPartial = false) {
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${isUser ? "user" : "agent"}`;

  const bubbleDiv = document.createElement("div");
  bubbleDiv.className = "bubble";

  const textP = document.createElement("p");
  textP.className = "bubble-text";
  textP.textContent = text;

  // 為部分訊息添加輸入中指標
  if (isPartial && !isUser) {
    const typingSpan = document.createElement("span");
    typingSpan.className = "typing-indicator";
    textP.appendChild(typingSpan);
  }

  bubbleDiv.appendChild(textP);
  messageDiv.appendChild(bubbleDiv);

  return messageDiv;
}

// 建立圖像訊息對話泡泡元素
function createImageBubble(imageDataUrl, isUser) {
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${isUser ? "user" : "agent"}`;

  const bubbleDiv = document.createElement("div");
  bubbleDiv.className = "bubble image-bubble";

  const img = document.createElement("img");
  img.src = imageDataUrl;
  img.className = "bubble-image";
  img.alt = "擷取的圖像";

  bubbleDiv.appendChild(img);
  messageDiv.appendChild(bubbleDiv);

  return messageDiv;
}

// 更新現有訊息泡泡文本
function updateMessageBubble(element, text, isPartial = false) {
  const textElement = element.querySelector(".bubble-text");

  // 移除現有的輸入中指標
  const existingIndicator = textElement.querySelector(".typing-indicator");
  if (existingIndicator) {
    existingIndicator.remove();
  }

  textElement.textContent = text;

  // 為部分訊息添加輸入中指標
  if (isPartial) {
    const typingSpan = document.createElement("span");
    typingSpan.className = "typing-indicator";
    textElement.appendChild(typingSpan);
  }
}

// 添加系統訊息
function addSystemMessage(text) {
  const messageDiv = document.createElement("div");
  messageDiv.className = "system-message";
  messageDiv.textContent = text;
  messagesDiv.appendChild(messageDiv);
  scrollToBottom();
}

// 捲動到訊息底部
function scrollToBottom() {
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// 淨化事件數據以供控制台顯示 (將大型音訊數據替換為摘要)
function sanitizeEventForDisplay(event) {
  // 深拷貝事件物件
  const sanitized = JSON.parse(JSON.stringify(event));

  // 檢查 content.parts 中是否有音訊數據
  if (sanitized.content && sanitized.content.parts) {
    sanitized.content.parts = sanitized.content.parts.map(part => {
      if (part.inlineData && part.inlineData.data) {
        // 計算位元組大小 (base64 字串長度 / 4 * 3，約略)
        const byteSize = Math.floor(part.inlineData.data.length * 0.75);
        return {
          ...part,
          inlineData: {
            ...part.inlineData,
            data: `(${byteSize.toLocaleString()} 位元組)`
          }
        };
      }
      return part;
    });
  }

  return sanitized;
}

// WebSocket 處理程序
function connectWebsocket() {
  // 連線 websocket
  const ws_url = getWebSocketUrl();
  websocket = new WebSocket(ws_url);

  // 處理連線開啟
  websocket.onopen = function () {
    console.log("WebSocket 連線已開啟。");
    updateConnectionStatus(true);
    addSystemMessage("已連線至 ADK 串流伺服器");

    // 記錄到控制台
    addConsoleEntry('incoming', 'WebSocket 已連線', {
      userId: userId,
      sessionId: sessionId,
      url: ws_url
    }, '🔌', 'system');

    // 啟用傳送按鈕
    document.getElementById("sendButton").disabled = false;
    addSubmitHandler();
  };

  // 處理傳入訊息
  websocket.onmessage = function (event) {
    // 解析傳入的 ADK 事件
    const adkEvent = JSON.parse(event.data);
    console.log("[AGENT TO CLIENT] ", adkEvent);

    // 記錄到控制台面板
    let eventSummary = '事件 (Event)';
    let eventEmoji = '📨'; // 預設表情符號
    const author = adkEvent.author || 'system';

    // 根據事件類型更新摘要和圖示
    if (adkEvent.turnComplete) {
      eventSummary = '對話輪結束 (Turn Complete)';
      eventEmoji = '✅';
    } else if (adkEvent.interrupted) {
      eventSummary = '被中斷 (Interrupted)';
      eventEmoji = '⏸️';
    } else if (adkEvent.inputTranscription) {
      // 在摘要中顯示轉錄文本
      const transcriptionText = adkEvent.inputTranscription.text || '';
      const truncated = transcriptionText.length > 60
        ? transcriptionText.substring(0, 60) + '...'
        : transcriptionText;
      eventSummary = `輸入轉錄 (Input Transcription): "${truncated}"`;
      eventEmoji = '📝';
    } else if (adkEvent.outputTranscription) {
      // 在摘要中顯示轉錄文本
      const transcriptionText = adkEvent.outputTranscription.text || '';
      const truncated = transcriptionText.length > 60
        ? transcriptionText.substring(0, 60) + '...'
        : transcriptionText;
      eventSummary = `輸出轉錄 (Output Transcription): "${truncated}"`;
      eventEmoji = '📝';
    } else if (adkEvent.usageMetadata) {
      // 顯示 Token 使用資訊
      const usage = adkEvent.usageMetadata;
      const promptTokens = usage.promptTokenCount || 0;
      const responseTokens = usage.candidatesTokenCount || 0;
      const totalTokens = usage.totalTokenCount || 0;
      eventSummary = `Token 使用量: 總計 ${totalTokens.toLocaleString()} (${promptTokens.toLocaleString()} 提示 + ${responseTokens.toLocaleString()} 回應)`;
      eventEmoji = '📊';
    } else if (adkEvent.content && adkEvent.content.parts) {
      const hasText = adkEvent.content.parts.some(p => p.text);
      const hasAudio = adkEvent.content.parts.some(p => p.inlineData);
      const hasExecutableCode = adkEvent.content.parts.some(p => p.executableCode);
      const hasCodeExecutionResult = adkEvent.content.parts.some(p => p.codeExecutionResult);

      if (hasExecutableCode) {
        // 顯示可執行程式碼
        const codePart = adkEvent.content.parts.find(p => p.executableCode);
        if (codePart && codePart.executableCode) {
          const code = codePart.executableCode.code || '';
          const language = codePart.executableCode.language || '未知';
          const truncated = code.length > 60
            ? code.substring(0, 60).replace(/\n/g, ' ') + '...'
            : code.replace(/\n/g, ' ');
          eventSummary = `可執行程式碼 (${language}): ${truncated}`;
          eventEmoji = '💻';
        }
      }

      if (hasCodeExecutionResult) {
        // 顯示程式碼執行結果
        const resultPart = adkEvent.content.parts.find(p => p.codeExecutionResult);
        if (resultPart && resultPart.codeExecutionResult) {
          const outcome = resultPart.codeExecutionResult.outcome || '未知';
          const output = resultPart.codeExecutionResult.output || '';
          const truncatedOutput = output.length > 60
            ? output.substring(0, 60).replace(/\n/g, ' ') + '...'
            : output.replace(/\n/g, ' ');
          eventSummary = `程式碼執行結果 (${outcome}): ${truncatedOutput}`;
          eventEmoji = outcome === 'OUTCOME_OK' ? '✅' : '❌';
        }
      }

      if (hasText) {
        // 在摘要中顯示文字預覽
        const textPart = adkEvent.content.parts.find(p => p.text);
        if (textPart && textPart.text) {
          const text = textPart.text;
          const truncated = text.length > 80
            ? text.substring(0, 80) + '...'
            : text;
          eventSummary = `文字: "${truncated}"`;
          eventEmoji = '💭';
        } else {
          eventSummary = '文字回應';
          eventEmoji = '💭';
        }
      }

      if (hasAudio) {
        // 提取音訊資訊用於摘要
        const audioPart = adkEvent.content.parts.find(p => p.inlineData);
        if (audioPart && audioPart.inlineData) {
          const mimeType = audioPart.inlineData.mimeType || '未知';
          const dataLength = audioPart.inlineData.data ? audioPart.inlineData.data.length : 0;
          // Base64 字串長度 / 4 * 3 給出近似位元組
          const byteSize = Math.floor(dataLength * 0.75);
          eventSummary = `音訊回應: ${mimeType} (${byteSize.toLocaleString()} 位元組)`;
          eventEmoji = '🔊';
        } else {
          eventSummary = '音訊回應';
          eventEmoji = '🔊';
        }

        // 記錄帶有 isAudio 標記的音訊事件 (由核取方塊過濾)
        const sanitizedEvent = sanitizeEventForDisplay(adkEvent);
        addConsoleEntry('incoming', eventSummary, sanitizedEvent, eventEmoji, author, true);
      }
    }

    // 建立用於控制台顯示的淨化版本 (將大型音訊數據替換為摘要)
    // 如果上面已經作為音訊事件記錄，則跳過
    const isAudioOnlyEvent = adkEvent.content && adkEvent.content.parts &&
      adkEvent.content.parts.some(p => p.inlineData) &&
      !adkEvent.content.parts.some(p => p.text);
    if (!isAudioOnlyEvent) {
      const sanitizedEvent = sanitizeEventForDisplay(adkEvent);
      addConsoleEntry('incoming', eventSummary, sanitizedEvent, eventEmoji, author);
    }

    // 處理對話輪結束事件
    if (adkEvent.turnComplete === true) {
      // 從目前訊息中移除輸入中指標
      if (currentBubbleElement) {
        const textElement = currentBubbleElement.querySelector(".bubble-text");
        const typingIndicator = textElement.querySelector(".typing-indicator");
        if (typingIndicator) {
          typingIndicator.remove();
        }
      }
      // 從目前輸出轉錄中移除輸入中指標
      if (currentOutputTranscriptionElement) {
        const textElement = currentOutputTranscriptionElement.querySelector(".bubble-text");
        const typingIndicator = textElement.querySelector(".typing-indicator");
        if (typingIndicator) {
          typingIndicator.remove();
        }
      }
      currentMessageId = null;
      currentBubbleElement = null;
      currentOutputTranscriptionId = null;
      currentOutputTranscriptionElement = null;
      inputTranscriptionFinished = false; // 為下一輪重置
      return;
    }

    // 處理被中斷事件
    if (adkEvent.interrupted === true) {
      // 如果音訊正在播放則停止
      if (audioPlayerNode) {
        audioPlayerNode.port.postMessage({ command: "endOfAudio" });
      }

      // 保留部分訊息但標記為被中斷
      if (currentBubbleElement) {
        const textElement = currentBubbleElement.querySelector(".bubble-text");

        // 移除輸入中指標
        const typingIndicator = textElement.querySelector(".typing-indicator");
        if (typingIndicator) {
          typingIndicator.remove();
        }

        // 添加被中斷標記
        currentBubbleElement.classList.add("interrupted");
      }

      // 保留部分輸出轉錄但標記為被中斷
      if (currentOutputTranscriptionElement) {
        const textElement = currentOutputTranscriptionElement.querySelector(".bubble-text");

        // 移除輸入中指標
        const typingIndicator = textElement.querySelector(".typing-indicator");
        if (typingIndicator) {
          typingIndicator.remove();
        }

        // 添加被中斷標記
        currentOutputTranscriptionElement.classList.add("interrupted");
      }

      // 重置狀態以便新內容建立新泡泡
      currentMessageId = null;
      currentBubbleElement = null;
      currentOutputTranscriptionId = null;
      currentOutputTranscriptionElement = null;
      inputTranscriptionFinished = false; // 為下一輪重置
      return;
    }

    // 處理輸入轉錄 (使用者說出的話)
    if (adkEvent.inputTranscription && adkEvent.inputTranscription.text) {
      const transcriptionText = adkEvent.inputTranscription.text;
      const isFinished = adkEvent.inputTranscription.finished;

      if (transcriptionText) {
        // 忽略在我們完成此輪之後才抵達的延遲轉錄
        if (inputTranscriptionFinished) {
          return;
        }

        if (currentInputTranscriptionId == null) {
          // 建立新轉錄泡泡
          currentInputTranscriptionId = Math.random().toString(36).substring(7);
          // 清理 CJK 字元之間的空格
          const cleanedText = cleanCJKSpaces(transcriptionText);
          currentInputTranscriptionElement = createMessageBubble(cleanedText, true, !isFinished);
          currentInputTranscriptionElement.id = currentInputTranscriptionId;

          // 添加特殊類別以指示它是轉錄
          currentInputTranscriptionElement.classList.add("transcription");

          messagesDiv.appendChild(currentInputTranscriptionElement);
        } else {
          // 僅在模型尚未開始回應時更新現有轉錄泡泡
          // 這可以防止延遲的部分轉錄覆蓋已完成的轉錄
          if (currentOutputTranscriptionId == null && currentMessageId == null) {
            if (isFinished) {
              // 最終轉錄包含完整文本，完全替換
              const cleanedText = cleanCJKSpaces(transcriptionText);
              updateMessageBubble(currentInputTranscriptionElement, cleanedText, false);
            } else {
              // 部分轉錄 - 附加到現有文本
              const existingText = currentInputTranscriptionElement.querySelector(".bubble-text").textContent;
              // 移除 "..." (如果存在)
              const cleanText = existingText.replace(/\.\.\.$/, '');
              // 更新前清理 CJK 字元之間的空格
              const accumulatedText = cleanCJKSpaces(cleanText + transcriptionText);
              updateMessageBubble(currentInputTranscriptionElement, accumulatedText, true);
            }
          }
        }

        // 如果轉錄已完成，重置狀態並標記為完成
        if (isFinished) {
          currentInputTranscriptionId = null;
          currentInputTranscriptionElement = null;
          inputTranscriptionFinished = true; // 防止延遲事件產生重複泡泡
        }

        scrollToBottom();
      }
    }

    // 處理輸出轉錄 (模型說出的話)
    if (adkEvent.outputTranscription && adkEvent.outputTranscription.text) {
      const transcriptionText = adkEvent.outputTranscription.text;
      const isFinished = adkEvent.outputTranscription.finished;

      if (transcriptionText) {
        // 當伺服器開始回應時，完成任何作用中的輸入轉錄
        if (currentInputTranscriptionId != null && currentOutputTranscriptionId == null) {
          // 這是第一個輸出轉錄 - 完成輸入轉錄
          const textElement = currentInputTranscriptionElement.querySelector(".bubble-text");
          const typingIndicator = textElement.querySelector(".typing-indicator");
          if (typingIndicator) {
            typingIndicator.remove();
          }
          // 重置輸入轉錄狀態，以便下次使用者輸入建立新氣球
          currentInputTranscriptionId = null;
          currentInputTranscriptionElement = null;
          inputTranscriptionFinished = true; // 防止延遲事件產生重複泡泡
        }

        if (currentOutputTranscriptionId == null) {
          // 為代理建立新轉錄泡泡
          currentOutputTranscriptionId = Math.random().toString(36).substring(7);
          currentOutputTranscriptionElement = createMessageBubble(transcriptionText, false, !isFinished);
          currentOutputTranscriptionElement.id = currentOutputTranscriptionId;

          // 添加特殊類別以指示它是轉錄
          currentOutputTranscriptionElement.classList.add("transcription");

          messagesDiv.appendChild(currentOutputTranscriptionElement);
        } else {
          // 更新現有轉錄泡泡
          if (isFinished) {
            // 最終轉錄包含完整文本，完全替換
            updateMessageBubble(currentOutputTranscriptionElement, transcriptionText, false);
          } else {
            // 部分轉錄 - 附加到現有文本
            const existingText = currentOutputTranscriptionElement.querySelector(".bubble-text").textContent;
            // 移除 "..." (如果存在)
            const cleanText = existingText.replace(/\.\.\.$/, '');
            updateMessageBubble(currentOutputTranscriptionElement, cleanText + transcriptionText, true);
          }
        }

        // 如果轉錄已完成，重置狀態
        if (isFinished) {
          currentOutputTranscriptionId = null;
          currentOutputTranscriptionElement = null;
        }

        scrollToBottom();
      }
    }

    // 處理內容事件 (文字或音訊)
    if (adkEvent.content && adkEvent.content.parts) {
      const parts = adkEvent.content.parts;

      // 當伺服器開始以內容回應時，完成任何作用中的輸入轉錄
      if (currentInputTranscriptionId != null && currentMessageId == null && currentOutputTranscriptionId == null) {
        // 這是第一個內容事件 - 完成輸入轉錄
        const textElement = currentInputTranscriptionElement.querySelector(".bubble-text");
        const typingIndicator = textElement.querySelector(".typing-indicator");
        if (typingIndicator) {
          typingIndicator.remove();
        }
        // 重置輸入轉錄狀態，以便下次使用者輸入建立新氣球
        currentInputTranscriptionId = null;
        currentInputTranscriptionElement = null;
        inputTranscriptionFinished = true; // 防止延遲事件產生重複泡泡
      }

      for (const part of parts) {
        // 處理內嵌數據 (音訊)
        if (part.inlineData) {
          const mimeType = part.inlineData.mimeType;
          const data = part.inlineData.data;

          if (mimeType && mimeType.startsWith("audio/pcm") && audioPlayerNode) {
            audioPlayerNode.port.postMessage(base64ToArray(data));
          }
        }

        // 處理文字
        if (part.text) {
          // 為新一輪對話添加新訊息泡泡
          if (currentMessageId == null) {
            currentMessageId = Math.random().toString(36).substring(7);
            currentBubbleElement = createMessageBubble(part.text, false, true);
            currentBubbleElement.id = currentMessageId;
            messagesDiv.appendChild(currentBubbleElement);
          } else {
            // 使用累計文本更新現有訊息泡泡
            const existingText = currentBubbleElement.querySelector(".bubble-text").textContent;
            // 移除 "..." (如果存在)
            const cleanText = existingText.replace(/\.\.\.$/, '');
            updateMessageBubble(currentBubbleElement, cleanText + part.text, true);
          }

          // 捲動到 messagesDiv 底部
          scrollToBottom();
        }
      }
    }
  };

  // 處理連線關閉
  websocket.onclose = function () {
    console.log("WebSocket 連線已關閉。");
    updateConnectionStatus(false);
    document.getElementById("sendButton").disabled = true;
    addSystemMessage("連線已斷開。將在 5 秒後重新連線...");

    // 記錄到控制台
    addConsoleEntry('error', 'WebSocket 已斷開連線', {
      status: '連線已關閉',
      reconnecting: true,
      reconnectDelay: '5 秒'
    }, '🔌', 'system');

    setTimeout(function () {
      console.log("正在重新連線...");

      // 將重新連線嘗試記錄到控制台
      addConsoleEntry('outgoing', '正在重新連線至 ADK 伺服器...', {
        userId: userId,
        sessionId: sessionId
      }, '🔄', 'system');

      connectWebsocket();
    }, 5000);
  };

  websocket.onerror = function (e) {
    console.log("WebSocket 錯誤：", e);
    updateConnectionStatus(false);

    // 記錄到控制台
    addConsoleEntry('error', 'WebSocket 錯誤', {
      error: e.type,
      message: '發生連線錯誤'
    }, '⚠️', 'system');
  };
}
connectWebsocket();

// 為表單添加提交處理程序
function addSubmitHandler() {
  messageForm.onsubmit = function (e) {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (message) {
      // 添加使用者訊息泡泡
      const userBubble = createMessageBubble(message, true, false);
      messagesDiv.appendChild(userBubble);
      scrollToBottom();

      // 清除輸入
      messageInput.value = "";

      // 傳送訊息至伺服器
      sendMessage(message);
      console.log("[CLIENT TO AGENT] " + message);
    }
    return false;
  };
}

// 將訊息作為 JSON 傳送至伺服器
function sendMessage(message) {
  if (websocket && websocket.readyState == WebSocket.OPEN) {
    const jsonMessage = JSON.stringify({
      type: "text",
      text: message
    });
    websocket.send(jsonMessage);

    // 記錄到控制台面板
    addConsoleEntry('outgoing', '使用者訊息：' + message, null, '💬', 'user');
  }
}

/**
 * 將 Base64 數據解碼為 Array
 * 處理標準 base64 和 base64url 編碼
 * @param {string} base64 - 編碼字串
 */
function base64ToArray(base64) {
  // 將 base64url 轉換為標準 base64
  // 替換 URL 安全字元：- 換成 +，_ 換成 /
  let standardBase64 = base64.replace(/-/g, '+').replace(/_/g, '/');

  // 必要時添加填充
  while (standardBase64.length % 4) {
    standardBase64 += '=';
  }

  const binaryString = window.atob(standardBase64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
}

/**
 * 相機處理
 */

const cameraButton = document.getElementById("cameraButton"); // 相機按鈕
const cameraModal = document.getElementById("cameraModal"); // 相機彈窗
const cameraPreview = document.getElementById("cameraPreview"); // 相機預覽
const closeCameraModal = document.getElementById("closeCameraModal"); // 關閉彈窗按鈕
const cancelCamera = document.getElementById("cancelCamera"); // 取消按鈕
const captureImageBtn = document.getElementById("captureImage"); // 擷取圖像按鈕

let cameraStream = null;

// 開啟相機預覽並開始預覽
async function openCameraPreview() {
  try {
    // 請求存取使用者的網路攝影機
    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 768 },
        height: { ideal: 768 },
        facingMode: 'user'
      }
    });

    // 將串流設定到視訊元素
    cameraPreview.srcObject = cameraStream;

    // 顯示彈窗
    cameraModal.classList.add('show');

  } catch (error) {
    console.error('存取相機時發生錯誤：', error);
    addSystemMessage(`無法存取相機：${error.message}`);

    // 記錄到控制台
    addConsoleEntry('error', '相機存取失敗', {
      error: error.message,
      name: error.name
    }, '⚠️', 'system');
  }
}

// 關閉相機預覽並停止預覽
function closeCameraPreview() {
  // 停止相機串流
  if (cameraStream) {
    cameraStream.getTracks().forEach(track => track.stop());
    cameraStream = null;
  }

  // 清除視訊來源
  cameraPreview.srcObject = null;

  // 隱藏彈窗
  cameraModal.classList.remove('show');
}

// 從即時預覽中擷取圖像
function captureImageFromPreview() {
  if (!cameraStream) {
    addSystemMessage('沒有可用的相機串流');
    return;
  }

  try {
    // 建立畫布以擷取影格
    const canvas = document.createElement('canvas');
    canvas.width = cameraPreview.videoWidth;
    canvas.height = cameraPreview.videoHeight;
    const context = canvas.getContext('2d');

    // 將目前視訊影格繪製到畫布
    context.drawImage(cameraPreview, 0, 0, canvas.width, canvas.height);

    // 將畫布轉換為用於顯示的 data URL
    const imageDataUrl = canvas.toDataURL('image/jpeg', 0.85);

    // 在對話中顯示擷取的圖像
    const imageBubble = createImageBubble(imageDataUrl, true);
    messagesDiv.appendChild(imageBubble);
    scrollToBottom();

    // 將畫布轉換為用於傳送至伺服器的 blob
    canvas.toBlob((blob) => {
      // 將 blob 轉換為用於傳送至伺服器的 base64
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64data = reader.result.split(',')[1]; // 移除 data:image/jpeg;base64, 前綴
        sendImage(base64data);
      };
      reader.readAsDataURL(blob);

      // 記錄到控制台
      addConsoleEntry('outgoing', `圖像已擷取：${blob.size} 位元組 (JPEG)`, {
        size: blob.size,
        type: 'image/jpeg',
        dimensions: `${canvas.width}x${canvas.height}`
      }, '📷', 'user');
    }, 'image/jpeg', 0.85);

    // 關閉相機預覽彈窗
    closeCameraPreview();

  } catch (error) {
    console.error('擷取圖像時發生錯誤：', error);
    addSystemMessage(`無法擷取圖像：${error.message}`);

    // 記錄到控制台
    addConsoleEntry('error', '圖像擷取失敗', {
      error: error.message,
      name: error.name
    }, '⚠️', 'system');
  }
}

// 傳送圖像至伺服器
function sendImage(base64Image) {
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    const jsonMessage = JSON.stringify({
      type: "image",
      data: base64Image,
      mimeType: "image/jpeg"
    });
    websocket.send(jsonMessage);
    console.log("[CLIENT TO AGENT] 已傳送圖像");
  }
}

// 事件監聽器
cameraButton.addEventListener("click", openCameraPreview);
closeCameraModal.addEventListener("click", closeCameraPreview);
cancelCamera.addEventListener("click", closeCameraPreview);
captureImageBtn.addEventListener("click", captureImageFromPreview);

// 點擊彈窗外部時關閉
cameraModal.addEventListener("click", (event) => {
  if (event.target === cameraModal) {
    closeCameraPreview();
  }
});

/**
 * 音訊處理
 */

let audioPlayerNode;
let audioPlayerContext;
let audioRecorderNode;
let audioRecorderContext;
let micStream;

// 匯入音訊 worklets (音訊工作處理緒)
import { startAudioPlayerWorklet } from "./audio-player.js";
import { startAudioRecorderWorklet } from "./audio-recorder.js";

// 開始音訊功能
function startAudio() {
  // 開始音訊輸出 (播放器)
  startAudioPlayerWorklet().then(([node, ctx]) => {
    audioPlayerNode = node;
    audioPlayerContext = ctx;
  });
  // 開始音訊輸入 (錄製器)
  startAudioRecorderWorklet(audioRecorderHandler).then(
    ([node, ctx, stream]) => {
      audioRecorderNode = node;
      audioRecorderContext = ctx;
      micStream = stream;
    }
  );
}

// 僅在使用者點擊按鈕時才開始音訊
// (由於 Web Audio API 的手勢要求，必須由使用者觸發才能啟動音訊上下文)
const startAudioButton = document.getElementById("startAudioButton");
startAudioButton.addEventListener("click", () => {
  startAudioButton.disabled = true;
  startAudio();
  is_audio = true;
  addSystemMessage("音訊模式已啟用 - 您現在可以對代理說話");

  // 記錄到控制台
  addConsoleEntry('outgoing', '音訊模式已啟用', {
    status: '音訊 worklets 已啟動',
    message: '麥克風作用中 - 音訊輸入將傳送至代理'
  }, '🎤', 'system');
});

/**
 * 音訊錄製器處理程序
 * 將 PCM 數據發送到伺服器
 */
function audioRecorderHandler(pcmData) {
  if (websocket && websocket.readyState === WebSocket.OPEN && is_audio) {
    // 將音訊作為二進位 WebSocket 影格傳送 (比 base64 JSON 更有效率)
    websocket.send(pcmData);
    console.log("[CLIENT TO AGENT] 已傳送音訊區塊： %s 位元組", pcmData.byteLength);

    // 記錄到控制台面板 (選填，頻繁的音訊區塊可能會很吵)
    // addConsoleEntry('outgoing', `音訊區塊： ${pcmData.byteLength} 位元組`);
  }
}

/**
 * 重點摘要
 * - **核心概念**：本檔案是雙向串流演示應用的前端核心，負責管理 WebSocket 通訊與使用者介面。
 * - **關鍵技術**：
 *   - WebSocket：實現與伺服器的即時雙向通訊。
 *   - Web Audio API & AudioWorklet：處理 PCM 音訊的串流輸入與輸出。
 *   - MediaDevices API：存取使用者相機進行圖像擷取。
 *   - Base64 編解碼：處理圖像與音訊數據的傳輸格式。
 * - **重要結論**：系統透過異步事件驅動架構，支援文字、音訊與影像的多模態互動，並提供即時的轉錄顯示與中斷處理。
 * - **行動項目**：
 *   - 確保瀏覽器支援音訊工作處理緒 (AudioWorklet)。
 *   - 部署時需使用 HTTPS 以確保相機與麥克風權限可正常獲取。
 */

/**
 * 系統流程圖
 * ```mermaid
 * sequenceDiagram
 *     participant U as 使用者 (User)
 *     participant UI as 前端介面 (App.js)
 *     participant WS as WebSocket 伺服器
 *     participant A as AI 代理 (Agent)
 *
 *     U->>UI: 開啟網頁並點擊啟動音訊
 *     UI->>WS: 建立連線 (包含 RunConfig 選項)
 *     WS-->>UI: 確認連線成功
 *
 *     rect rgb(240, 240, 240)
 *     Note over U, A: 文字互動流程
 *     U->>UI: 輸入文字並送出
 *     UI->>WS: 傳送 JSON 文字訊息
 *     WS->>A: 轉發至 AI 代理
 *     A-->>WS: 串流回傳文字/音訊
 *     WS-->>UI: 傳送 ADK 事件 (Content/Transcription)
 *     UI->>U: 更新對話泡泡與播放音訊
 *     end
 *
 *     rect rgb(220, 240, 255)
 *     Note over U, A: 音訊互動流程
 *     U->>UI: 對麥克風說話
 *     UI->>WS: 傳送 PCM 二進位數據
 *     WS->>A: 進行即時轉錄與處理
 *     A-->>WS: 即時語音與轉錄
 *     WS-->>UI: 傳送轉錄事件 (Input/Output Transcription)
 *     UI->>U: 顯示即時轉錄內容
 *     end
 * ```
 */

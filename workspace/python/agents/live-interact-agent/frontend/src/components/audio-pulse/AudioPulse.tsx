import "./audio-pulse.scss";
import React from "react";
import { useEffect, useRef } from "react";
import c from "classnames";

// Define the number of bars in the visualizer
// 定義視覺化效果中的線條數量
const lineCount = 3;

export type AudioPulseProps = {
  active: boolean; // Is the pulse animation active // 脈衝動畫是否處於活動狀態
  volume: number;  // Current volume level (0-1) // 當前音量級別 (0-1)
  hover?: boolean; // Is the element being hovered // 元素是否處於懸停狀態
};

/**
 * AudioPulse component renders a simple audio visualizer.
 * AudioPulse 組件渲染一個簡單的音訊視覺化效果。
 */
export default function AudioPulse({ active, volume, hover }: AudioPulseProps) {
  // Ref to store references to the visualizer bar elements
  // 用於儲存視覺化線條元素參考的 Ref
  const lines = useRef<HTMLDivElement[]>([]);

  useEffect(() => {
    let timeout: number | null = null;

    // Function to update the height of the bars based on volume
    // 根據音量更新線條高度的函數
    const update = () => {
      lines.current.forEach(
        (line, i) =>
        (line.style.height = `${Math.min(
          24,
          4 + volume * (i === 1 ? 400 : 60), // Center bar reacts more strongly // 中間的線條反應更強烈
        )}px`),
      );
      // Schedule the next update
      // 排程下一次更新
      timeout = window.setTimeout(update, 100);
    };

    update();

    // Clean up timeout on unmount
    // 在組件卸載時清除計時器
    return () => clearTimeout((timeout as number)!);
  }, [volume]);

  return (
    <div className={c("audioPulse", { active, hover })}>
      {Array(lineCount)
        .fill(null)
        .map((_, i) => (
          <div
            key={i}
            ref={(el) => (lines.current[i] = el!)}
            style={{ animationDelay: `${i * 133}ms` }} // Staggered animation delay // 交錯的動畫延遲
          />
        ))}
    </div>
  );
}

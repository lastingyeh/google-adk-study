import { create } from "zustand";
import { StreamingLog } from "../multimodal-live-types";

interface StoreLoggerState {
  maxLogs: number; // Maximum number of logs to keep // 保留的最大日誌數量
  logs: StreamingLog[]; // Array of logs // 日誌陣列
  log: (streamingLog: StreamingLog) => void; // Function to add a log // 添加日誌的函數
  clearLogs: () => void; // Function to clear all logs // 清除所有日誌的函數
}

/**
 * Zustand store for managing application logs.
 * 用於管理應用程式日誌的 Zustand store。
 */
export const useLoggerStore = create<StoreLoggerState>((set, get) => ({
  maxLogs: 500,
  logs: [], //mockLogs,
  log: ({ date, type, message }: StreamingLog) => {
    set((state) => {
      const prevLog = state.logs.at(-1);
      // Group identical sequential logs by incrementing count
      // 透過增加計數來將相同的連續日誌分組
      if (prevLog && prevLog.type === type && prevLog.message === message) {
        return {
          logs: [
            ...state.logs.slice(0, -1),
            {
              date,
              type,
              message,
              count: prevLog.count ? prevLog.count + 1 : 1,
            } as StreamingLog,
          ],
        };
      }
      // Add new log and respect maxLogs limit
      // 添加新日誌並遵守 maxLogs 限制
      return {
        logs: [
          ...state.logs.slice(-(get().maxLogs - 1)),
          {
            date,
            type,
            message,
          } as StreamingLog,
        ],
      };
    });
  },

  clearLogs: () => {
    console.log("clear log");
    set({ logs: [] });
  },
  setMaxLogs: (n: number) => set({ maxLogs: n }),
}));

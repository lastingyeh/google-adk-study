import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  Dispatch,
  SetStateAction,
} from "react";
import { MultimodalLiveClient } from "../utils/multimodal-live-client";
import { AudioStreamer } from "../utils/audio-streamer";
import { audioContext } from "../utils/utils";
import VolMeterWorket from "../utils/worklets/vol-meter";

export type UseLiveAPIResults = {
  client: MultimodalLiveClient;
  connected: boolean;
  connect: () => Promise<void>;
  disconnect: () => Promise<void>;
  volume: number;
};

export type UseLiveAPIProps = {
  url?: string;
  userId?: string;
  onRunIdChange?: Dispatch<SetStateAction<string>>;
};

/**
 * Hook to manage the Multimodal Live API connection.
 * 用於管理多模態即時 API 連接的 Hook。
 */
export function useLiveAPI({
  url,
  userId,
}: UseLiveAPIProps): UseLiveAPIResults {
  const client = useMemo(
    () => new MultimodalLiveClient({ url, userId }),
    [url, userId],
  );
  const audioStreamerRef = useRef<AudioStreamer | null>(null);

  const [connected, setConnected] = useState(false);
  const [volume, setVolume] = useState(0);

  // register audio for streaming server -> speakers
  // 註冊音訊串流：伺服器 -> 揚聲器
  useEffect(() => {
    if (!audioStreamerRef.current) {
      audioContext({ id: "audio-out" }).then((audioCtx: AudioContext) => {
        audioStreamerRef.current = new AudioStreamer(audioCtx);
        audioStreamerRef.current
          .addWorklet<any>("vumeter-out", VolMeterWorket, (ev: any) => {
            setVolume(ev.data.volume);
          })
          .then(() => {
            // Successfully added worklet
            // 成功添加 worklet
          });
      });
    }
  }, [audioStreamerRef]);

  useEffect(() => {
    const onClose = () => {
      setConnected(false);
    };

    const onSetupComplete = () => {
      setConnected(true);
    };

    const stopAudioStreamer = () => audioStreamerRef.current?.stop();

    const onAudio = (data: ArrayBuffer) =>
      audioStreamerRef.current?.addPCM16(new Uint8Array(data));

    client
      .on("close", onClose)
      .on("setupcomplete", onSetupComplete)
      .on("interrupted", stopAudioStreamer)
      .on("audio", onAudio);

    return () => {
      client
        .off("close", onClose)
        .off("setupcomplete", onSetupComplete)
        .off("interrupted", stopAudioStreamer)
        .off("audio", onAudio);
    };
  }, [client]);

  const connect = useCallback(async () => {
    client.disconnect();
    await client.connect();
    // Don't set connected here - wait for setupcomplete event
    // 不要在這裡設置 connected - 等待 setupcomplete 事件
  }, [client]);

  const disconnect = useCallback(async () => {
    client.disconnect();
    setConnected(false);
  }, [setConnected, client]);

  return {
    client,
    connected,
    connect,
    disconnect,
    volume,
  };
}

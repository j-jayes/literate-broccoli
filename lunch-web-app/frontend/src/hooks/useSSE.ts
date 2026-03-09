import { useEffect, useRef } from "react";
import type { LunchSession } from "../types";

export function useSSE(
  sessionId: string | undefined,
  onUpdate: (data: LunchSession) => void
) {
  const onUpdateRef = useRef(onUpdate);
  onUpdateRef.current = onUpdate;

  useEffect(() => {
    if (!sessionId) return;
    const es = new EventSource(`/api/sessions/${sessionId}/events`);
    es.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        onUpdateRef.current(data);
      } catch {
        // ignore parse errors
      }
    };
    es.onerror = () => {
      // EventSource auto-reconnects
    };
    return () => es.close();
  }, [sessionId]);
}

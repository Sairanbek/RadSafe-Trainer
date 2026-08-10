import { useEffect, useRef, useState } from "react";

const EXAM_TIME = 75 * 60;

export function Timer({ secondsLeft, onExpire }: { secondsLeft: number; onExpire?: () => void }) {
  const [left, setLeft] = useState(secondsLeft);
  const expiredRef = useRef(false);

  useEffect(() => {
    setLeft(secondsLeft);
    expiredRef.current = false;

    const endsAt = Date.now() + secondsLeft * 1000;
    const id = setInterval(() => {
      const remaining = Math.max(0, Math.round((endsAt - Date.now()) / 1000));
      setLeft(remaining);
      if (remaining <= 0 && !expiredRef.current) {
        expiredRef.current = true;
        onExpire?.();
      }
    }, 1000);

    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [secondsLeft]);

  const minutes = Math.floor(left / 60);
  const seconds = left % 60;
  const percent = Math.max(0, Math.min(100, (left / EXAM_TIME) * 100));
  const low = left <= 5 * 60;

  return (
    <div>
      <div className="timer-bar-track">
        <div className={`timer-bar-fill${low ? " low" : ""}`} style={{ width: `${percent}%` }} />
      </div>
      <div className="timer-label">
        ⏱ Осталось: {String(minutes).padStart(2, "0")}:{String(seconds).padStart(2, "0")}
      </div>
    </div>
  );
}

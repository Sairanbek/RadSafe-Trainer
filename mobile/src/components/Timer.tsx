import { useEffect, useRef, useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import { colors } from "../theme";

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
  }, [secondsLeft, onExpire]);

  const minutes = Math.floor(left / 60);
  const seconds = left % 60;
  const percent = Math.max(0, Math.min(100, (left / EXAM_TIME) * 100));
  const low = left <= 5 * 60;

  return (
    <View>
      <View style={styles.track}>
        <View style={[styles.fill, { width: `${percent}%`, backgroundColor: low ? colors.danger : colors.accent }]} />
      </View>
      <Text style={styles.label}>
        ⏱ Осталось: {String(minutes).padStart(2, "0")}:{String(seconds).padStart(2, "0")}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  track: {
    height: 6,
    borderRadius: 999,
    backgroundColor: colors.bgElevated,
    overflow: "hidden",
  },
  fill: {
    height: "100%",
  },
  label: {
    marginTop: 6,
    fontSize: 13,
    color: colors.textDim,
  },
});

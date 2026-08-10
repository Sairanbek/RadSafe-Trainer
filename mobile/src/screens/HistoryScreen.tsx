import { useEffect, useState } from "react";
import { ActivityIndicator, StyleSheet, Text, View } from "react-native";
import { Screen } from "../components/Screen";
import { api, ApiError } from "../api/client";
import type { HistoryRow, Mode } from "../api/types";
import { Card, ErrorText } from "../components/UI";
import { colors } from "../theme";
import type { TabScreenProps } from "../navigation/types";

const MODE_LABELS: Record<Mode, string> = {
  training: "Тренировка",
  exam: "Аттестация",
  mistakes: "Мои ошибки",
  learning: "Обучение",
};

export function HistoryScreen(_props: TabScreenProps<"History">) {
  const [rows, setRows] = useState<HistoryRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<HistoryRow[]>("/api/history")
      .then(setRows)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Не удалось загрузить историю"));
  }, []);

  return (
    <Screen title="История">
      {error && (
        <Card>
          <ErrorText>{error}</ErrorText>
        </Card>
      )}
      {!rows && !error && <ActivityIndicator color={colors.accent} style={styles.spinner} />}
      {rows && rows.length === 0 && <Text style={styles.emptyMsg}>История пуста — пройдите первый тест</Text>}
      {rows &&
        rows.map((r) => (
          <Card key={r.id}>
            <View style={styles.rowBetween}>
              <Text style={styles.mode}>{MODE_LABELS[r.mode]}</Text>
              <View style={[styles.tag, r.percent >= 70 ? styles.tagPass : styles.tagFail]}>
                <Text style={r.percent >= 70 ? styles.tagPassText : styles.tagFailText}>{r.percent}%</Text>
              </View>
            </View>
            <Text style={styles.section}>{r.section}</Text>
            <Text style={styles.meta}>
              {r.date} · {r.correct}/{r.total} правильных
            </Text>
          </Card>
        ))}
    </Screen>
  );
}

const styles = StyleSheet.create({
  spinner: { marginTop: 40 },
  emptyMsg: { color: colors.textDim, textAlign: "center", marginTop: 40 },
  rowBetween: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  mode: { color: colors.text, fontSize: 14.5, fontWeight: "600" },
  tag: { paddingHorizontal: 12, paddingVertical: 4, borderRadius: 999 },
  tagPass: { backgroundColor: colors.successBg },
  tagFail: { backgroundColor: colors.dangerBg },
  tagPassText: { color: colors.success, fontWeight: "700", fontSize: 12.5 },
  tagFailText: { color: colors.danger, fontWeight: "700", fontSize: 12.5 },
  section: { color: colors.textDim, fontSize: 13.5, marginTop: 6 },
  meta: { color: colors.textDim, fontSize: 12, marginTop: 4 },
});

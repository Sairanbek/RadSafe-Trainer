import { StyleSheet, Text, View } from "react-native";
import { Screen } from "../components/Screen";
import { Card, PrimaryButton } from "../components/UI";
import { colors } from "../theme";
import type { Mode } from "../api/types";
import type { RootScreenProps } from "../navigation/types";

const MODE_LABELS: Record<Mode, string> = {
  training: "Тренировка",
  exam: "Аттестация",
  mistakes: "Мои ошибки",
  learning: "Обучение",
};

export function SummaryScreen({ navigation, route }: RootScreenProps<"Summary">) {
  const { summary, mode } = route.params;

  return (
    <Screen title="Результат" showBack>
      <Text style={styles.modeLabel}>{MODE_LABELS[mode]}</Text>

      <Card style={styles.verdictCard}>
        <Text style={styles.percent}>{summary.percent}%</Text>
        <View style={[styles.verdictTag, summary.passed ? styles.pass : styles.fail]}>
          <Text style={summary.passed ? styles.passText : styles.failText}>
            {summary.passed ? "✅ Сдал" : "❌ Не сдал"}
          </Text>
        </View>
      </Card>

      <Card style={styles.rows}>
        <Row label="Отвечено" value={`${summary.asked} из ${summary.total}`} />
        {summary.unanswered > 0 && <Row label="Не отвечено (время вышло)" value={String(summary.unanswered)} />}
        <Row label="Правильных" value={String(summary.correct)} />
        <Row label="Ошибок" value={String(summary.wrong)} last />
        <Row label="Порог сдачи" value={`${summary.threshold}%`} last />
      </Card>

      <PrimaryButton title="🏠 Главное меню" onPress={() => navigation.popToTop()} />
    </Screen>
  );
}

function Row({ label, value, last }: { label: string; value: string; last?: boolean }) {
  return (
    <View style={[styles.row, last && styles.rowLast]}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={styles.rowValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  modeLabel: { fontSize: 13, color: colors.textDim },
  verdictCard: { alignItems: "center", paddingVertical: 28 },
  percent: { fontSize: 52, fontWeight: "800", color: colors.accent },
  verdictTag: { marginTop: 10, paddingHorizontal: 16, paddingVertical: 6, borderRadius: 999 },
  pass: { backgroundColor: colors.successBg },
  fail: { backgroundColor: colors.dangerBg },
  passText: { color: colors.success, fontWeight: "700", fontSize: 13.5 },
  failText: { color: colors.danger, fontWeight: "700", fontSize: 13.5 },
  rows: { gap: 0 },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  rowLast: { borderBottomWidth: 0 },
  rowLabel: { color: colors.text, fontSize: 14.5 },
  rowValue: { color: colors.text, fontSize: 14.5, fontWeight: "600" },
});

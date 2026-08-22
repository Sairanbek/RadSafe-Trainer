import { useEffect, useState } from "react";
import { ActivityIndicator, StyleSheet, Text, View } from "react-native";
import { Screen } from "../components/Screen";
import { api, ApiError } from "../api/client";
import { useModule } from "../context/ModuleContext";
import type { StatsResponse } from "../api/types";
import { Card, ErrorText } from "../components/UI";
import { colors } from "../theme";
import type { TabScreenProps } from "../navigation/types";

export function StatsScreen(_props: TabScreenProps<"Stats">) {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { module } = useModule();

  useEffect(() => {
    setStats(null);
    api
      .get<StatsResponse>(`/api/stats?module=${encodeURIComponent(module)}`)
      .then(setStats)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Не удалось загрузить статистику"));
  }, [module]);

  return (
    <Screen title="Статистика">
      {error && (
        <Card>
          <ErrorText>{error}</ErrorText>
        </Card>
      )}
      {!stats && !error && <ActivityIndicator color={colors.accent} style={styles.spinner} />}
      {stats && (
        <>
          <View style={styles.statGrid}>
            <Card style={styles.statTile}>
              <Text style={styles.statValue}>{stats.tests_count}</Text>
              <Text style={styles.statLabel}>Пройдено тестов</Text>
            </Card>
            <Card style={styles.statTile}>
              <Text style={styles.statValue}>{stats.average_percent}%</Text>
              <Text style={styles.statLabel}>Средний результат</Text>
            </Card>
          </View>

          {stats.sections.length === 0 ? (
            <Text style={styles.emptyMsg}>Пока нет данных — пройдите первый тест</Text>
          ) : (
            stats.sections.map((s) => (
              <Card key={s.section}>
                <View style={styles.rowBetween}>
                  <Text style={styles.sectionName}>{s.section}</Text>
                  <Text style={styles.sectionCount}>
                    {s.correct}/{s.asked} · {s.percent}%
                  </Text>
                </View>
                <View style={styles.track}>
                  <View style={[styles.fill, { width: `${s.percent}%` }]} />
                </View>
              </Card>
            ))
          )}
        </>
      )}
    </Screen>
  );
}

const styles = StyleSheet.create({
  spinner: { marginTop: 40 },
  statGrid: { flexDirection: "row", gap: 12 },
  statTile: { flex: 1, paddingVertical: 14, paddingHorizontal: 16 },
  statValue: { fontSize: 26, fontWeight: "800", color: colors.accent },
  statLabel: { fontSize: 12, color: colors.textDim, marginTop: 2 },
  emptyMsg: { color: colors.textDim, textAlign: "center", marginTop: 40 },
  rowBetween: { flexDirection: "row", justifyContent: "space-between", marginBottom: 8 },
  sectionName: { color: colors.text, fontSize: 14, flexShrink: 1, marginRight: 8 },
  sectionCount: { color: colors.textDim, fontSize: 12.5 },
  track: { height: 6, borderRadius: 999, backgroundColor: colors.bgElevated, overflow: "hidden" },
  fill: { height: "100%", backgroundColor: colors.accent },
});

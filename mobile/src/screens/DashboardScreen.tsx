import { useCallback, useEffect, useState } from "react";
import { useFocusEffect } from "@react-navigation/native";
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { Screen } from "../components/Screen";
import { useAuth } from "../context/AuthContext";
import { useModule } from "../context/ModuleContext";
import { api, ApiError } from "../api/client";
import type { StartTestResponse, StatsResponse } from "../api/types";
import { Card } from "../components/UI";
import { colors, radius } from "../theme";
import type { TabScreenProps } from "../navigation/types";

export function DashboardScreen({ navigation }: TabScreenProps<"Dashboard">) {
  const { refreshMe, logout } = useAuth();
  const { module, setModule, modules } = useModule();
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [mistakes, setMistakes] = useState<number | null>(null);

  useFocusEffect(
    useCallback(() => {
      refreshMe();
    }, [refreshMe]),
  );

  // Счётчики считаем по текущему направлению: /api/auth/me отдаёт суммы по
  // всем сразу, и они расходились бы с тем, что даёт режим «Мои ошибки».
  useEffect(() => {
    const q = `?module=${encodeURIComponent(module)}`;
    api.get<StatsResponse>(`/api/stats${q}`).then(setStats).catch(() => setStats(null));
    api
      .get<{ count: number }>(`/api/mistakes/count${q}`)
      .then((r) => setMistakes(r.count))
      .catch(() => setMistakes(null));
  }, [module, busy]);

  async function startDirect(mode: "exam" | "mistakes") {
    setBusy(true);
    setNotice(null);
    try {
      const res = await api.post<StartTestResponse>("/api/tests/start", { mode, module });
      if (!res.session_id || !res.question) {
        setNotice(res.message ?? "Вопросы не найдены");
        return;
      }
      navigation.navigate("Test", { sessionId: res.session_id, start: res });
    } catch (err) {
      setNotice(err instanceof ApiError ? err.message : "Не удалось начать тест");
    } finally {
      setBusy(false);
      refreshMe();
    }
  }

  return (
    <Screen
      title="RST — RadSafe Trainer"
      right={
        <TouchableOpacity onPress={logout}>
          <Text style={styles.logoutIcon}>⏻</Text>
        </TouchableOpacity>
      }
    >
      {modules.length > 1 && (
        <View style={styles.moduleSwitch}>
          <Text style={styles.moduleLabel}>Направление подготовки</Text>
          <View style={styles.moduleChips}>
            {modules.map((m) => {
              const active = m.name === module;
              return (
                <TouchableOpacity
                  key={m.name}
                  style={[styles.moduleChip, active && styles.moduleChipActive]}
                  onPress={() => setModule(m.name)}
                >
                  <Text style={[styles.moduleChipText, active && styles.moduleChipTextActive]}>
                    {m.name}
                  </Text>
                  <Text style={styles.moduleChipCount}>{m.count}</Text>
                </TouchableOpacity>
              );
            })}
          </View>
        </View>
      )}

      <View style={styles.statGrid}>
        <Card style={styles.statTile}>
          <Text style={styles.statValue}>{stats?.tests_count ?? 0}</Text>
          <Text style={styles.statLabel}>Пройдено тестов</Text>
        </Card>
        <Card style={styles.statTile}>
          <Text style={styles.statValue}>{stats?.average_percent ?? 0}%</Text>
          <Text style={styles.statLabel}>Средний результат</Text>
        </Card>
      </View>

      {notice && (
        <Card>
          <Text style={{ color: colors.text }}>{notice}</Text>
        </Card>
      )}

      <View style={styles.modeList}>
        <ModeButton
          emoji="📝"
          title="Тренировка"
          subtitle="По разделам, без ограничения времени"
          onPress={() => navigation.navigate("Sections", { mode: "training" })}
        />
        <ModeButton
          emoji="☢"
          title="Аттестация"
          subtitle="50 вопросов, 75 минут"
          disabled={busy}
          onPress={() => startDirect("exam")}
        />
        <ModeButton
          emoji="🔁"
          title="Мои ошибки"
          subtitle={`${mistakes ?? 0} вопрос(ов) на повторении`}
          disabled={busy}
          onPress={() => startDirect("mistakes")}
        />
        <ModeButton
          emoji="📖"
          title="Обучение"
          subtitle="Правильный ответ виден сразу, без баллов"
          onPress={() => navigation.navigate("Sections", { mode: "learning" })}
        />
      </View>
    </Screen>
  );
}

function ModeButton({
  emoji,
  title,
  subtitle,
  onPress,
  disabled,
}: {
  emoji: string;
  title: string;
  subtitle: string;
  onPress: () => void;
  disabled?: boolean;
}) {
  return (
    <TouchableOpacity style={[styles.modeBtn, disabled && styles.modeBtnDisabled]} onPress={onPress} disabled={disabled}>
      <Text style={styles.modeEmoji}>{emoji}</Text>
      <View style={styles.modeTextWrap}>
        <Text style={styles.modeTitle}>{title}</Text>
        <Text style={styles.modeSubtitle}>{subtitle}</Text>
      </View>
      <Text style={styles.chevron}>›</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  logoutIcon: { fontSize: 20, color: colors.textDim },
  statGrid: { flexDirection: "row", gap: 12 },
  statTile: { flex: 1, paddingVertical: 14, paddingHorizontal: 16 },
  statValue: { fontSize: 26, fontWeight: "800", color: colors.accent },
  statLabel: { fontSize: 12, color: colors.textDim, marginTop: 2 },
  moduleSwitch: { marginBottom: 14 },
  moduleLabel: { fontSize: 12, color: colors.textDim, marginBottom: 6 },
  moduleChips: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  moduleChip: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    paddingVertical: 7,
    paddingHorizontal: 12,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 999,
    backgroundColor: colors.bgCard,
  },
  moduleChipActive: { backgroundColor: colors.accentDim, borderColor: colors.accent },
  moduleChipText: { fontSize: 13, color: colors.text },
  moduleChipTextActive: { fontWeight: "700" },
  moduleChipCount: { fontSize: 11, color: colors.textDim },
  modeList: { gap: 10 },
  modeBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: 14,
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius,
    padding: 16,
  },
  modeBtnDisabled: { opacity: 0.5 },
  modeEmoji: { fontSize: 24, width: 32, textAlign: "center" },
  modeTextWrap: { flex: 1 },
  modeTitle: { fontWeight: "700", fontSize: 15, color: colors.text },
  modeSubtitle: { fontSize: 12.5, color: colors.textDim, marginTop: 2 },
  chevron: { color: colors.textDim, fontSize: 18 },
});

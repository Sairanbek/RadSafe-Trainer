import { useCallback, useState } from "react";
import { useFocusEffect } from "@react-navigation/native";
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { Screen } from "../components/Screen";
import { useAuth } from "../context/AuthContext";
import { api, ApiError } from "../api/client";
import type { StartTestResponse } from "../api/types";
import { Card } from "../components/UI";
import { colors, radius } from "../theme";
import type { TabScreenProps } from "../navigation/types";

export function DashboardScreen({ navigation }: TabScreenProps<"Dashboard">) {
  const { user, refreshMe, logout } = useAuth();
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useFocusEffect(
    useCallback(() => {
      refreshMe();
    }, [refreshMe]),
  );

  async function startDirect(mode: "exam" | "mistakes") {
    setBusy(true);
    setNotice(null);
    try {
      const res = await api.post<StartTestResponse>("/api/tests/start", { mode });
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
      <View style={styles.statGrid}>
        <Card style={styles.statTile}>
          <Text style={styles.statValue}>{user?.tests_count ?? 0}</Text>
          <Text style={styles.statLabel}>Пройдено тестов</Text>
        </Card>
        <Card style={styles.statTile}>
          <Text style={styles.statValue}>{user?.average_percent ?? 0}%</Text>
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
          subtitle={`${user?.mistakes_count ?? 0} вопрос(ов) на повторении`}
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

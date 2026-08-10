import { useEffect, useState } from "react";
import { ActivityIndicator, StyleSheet } from "react-native";
import { Screen } from "../components/Screen";
import { api, ApiError } from "../api/client";
import type { Section, StartTestResponse, Subsection } from "../api/types";
import { Card, ErrorText, ListItem } from "../components/UI";
import { colors } from "../theme";
import type { RootScreenProps } from "../navigation/types";

export function SectionsScreen({ navigation, route }: RootScreenProps<"Sections">) {
  const mode = route.params?.mode ?? "training";
  const [sections, setSections] = useState<Section[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busySection, setBusySection] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<Section[]>("/api/sections")
      .then(setSections)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Не удалось загрузить разделы"));
  }, []);

  async function startTraining(section: string) {
    setBusySection(section);
    try {
      const res = await api.post<StartTestResponse>("/api/tests/start", { mode, section });
      if (!res.session_id || !res.question) {
        setError(res.message ?? "Вопросы не найдены");
        return;
      }
      navigation.replace("Test", { sessionId: res.session_id, start: res });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось начать тренировку");
    } finally {
      setBusySection(null);
    }
  }

  async function handlePick(section: string) {
    setBusySection(section);
    setError(null);
    try {
      const subs = await api.get<Subsection[]>(`/api/subsections?section=${encodeURIComponent(section)}`);
      if (subs.length > 0) {
        navigation.navigate("Subsections", { section, mode });
      } else {
        await startTraining(section);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось загрузить раздел");
    } finally {
      setBusySection(null);
    }
  }

  return (
    <Screen title={mode === "learning" ? "Обучение — раздел" : "Выбор раздела"} showBack>
      {error && (
        <Card>
          <ErrorText>{error}</ErrorText>
        </Card>
      )}
      {!sections && !error && <ActivityIndicator color={colors.accent} style={styles.spinner} />}
      {sections && (
        <>
          <ListItem title="🎲 Все разделы" onPress={() => startTraining("ALL")} disabled={busySection === "ALL"} />
          {sections.map((s) => (
            <ListItem
              key={s.name}
              title={s.name}
              count={s.count}
              onPress={() => handlePick(s.name)}
              disabled={busySection === s.name}
            />
          ))}
        </>
      )}
    </Screen>
  );
}

const styles = StyleSheet.create({
  spinner: { marginTop: 40 },
});

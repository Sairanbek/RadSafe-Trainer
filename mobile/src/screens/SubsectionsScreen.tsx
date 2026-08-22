import { useEffect, useState } from "react";
import { ActivityIndicator, StyleSheet } from "react-native";
import { Screen } from "../components/Screen";
import { api, ApiError } from "../api/client";
import { useModule } from "../context/ModuleContext";
import type { StartTestResponse, Subsection } from "../api/types";
import { Card, ErrorText, ListItem } from "../components/UI";
import { colors } from "../theme";
import type { RootScreenProps } from "../navigation/types";

export function SubsectionsScreen({ navigation, route }: RootScreenProps<"Subsections">) {
  const { section, mode } = route.params;
  const { module } = useModule();
  const [subsections, setSubsections] = useState<Subsection[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<Subsection[]>(
        `/api/subsections?section=${encodeURIComponent(section)}&module=${encodeURIComponent(module)}`,
      )
      .then(setSubsections)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Не удалось загрузить подразделы"));
  }, [section, module]);

  const totalCount = subsections?.reduce((sum, s) => sum + s.count, 0) ?? 0;

  async function start(subsection?: string) {
    setBusy(subsection ?? "ALL");
    setError(null);
    try {
      const res = await api.post<StartTestResponse>("/api/tests/start", {
        mode,
        module,
        section,
        subsection,
      });
      if (!res.session_id || !res.question) {
        setError(res.message ?? "Вопросы не найдены");
        return;
      }
      navigation.replace("Test", { sessionId: res.session_id, start: res });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось начать тренировку");
    } finally {
      setBusy(null);
    }
  }

  return (
    <Screen title={section} showBack>
      {error && (
        <Card>
          <ErrorText>{error}</ErrorText>
        </Card>
      )}
      {!subsections && !error && <ActivityIndicator color={colors.accent} style={styles.spinner} />}
      {subsections && (
        <>
          <ListItem title="🎲 Весь раздел" count={totalCount} onPress={() => start(undefined)} disabled={busy === "ALL"} />
          {subsections.map((s) => (
            <ListItem
              key={s.name}
              title={s.name}
              count={s.count}
              onPress={() => start(s.name)}
              disabled={busy === s.name}
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

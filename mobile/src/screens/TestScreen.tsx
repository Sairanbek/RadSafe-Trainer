import { useCallback, useEffect, useState } from "react";
import { ActivityIndicator, ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Timer } from "../components/Timer";
import { api, ApiError } from "../api/client";
import { renderBold } from "../utils/markdown";
import { Card, ErrorText, PrimaryButton } from "../components/UI";
import { colors, radius } from "../theme";
import type {
  AiTextResponse,
  AnswerResponse,
  LearningNextResponse,
  Mode,
  QuestionPayload,
  SessionStateResponse,
  Summary,
} from "../api/types";
import type { RootScreenProps } from "../navigation/types";

const MODE_LABELS: Record<Mode, string> = {
  training: "Тренировка",
  exam: "Аттестация",
  mistakes: "Мои ошибки",
  learning: "Обучение",
};

interface Feedback {
  chosen: string;
  correct: boolean;
  correctLetter: string;
  correctText: string;
}

export function TestScreen({ navigation, route }: RootScreenProps<"Test">) {
  const { sessionId, start } = route.params;

  const [mode, setMode] = useState<Mode | null>(null);
  const [section, setSection] = useState<string>("");
  const [question, setQuestion] = useState<QuestionPayload | null>(null);
  const [pendingQuestion, setPendingQuestion] = useState<QuestionPayload | null>(null);
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [pendingSummary, setPendingSummary] = useState<Summary | null>(null);
  const [answering, setAnswering] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [learningDoneMessage, setLearningDoneMessage] = useState<string | null>(null);
  const [explanation, setExplanation] = useState<string | null>(null);
  const [explaining, setExplaining] = useState(false);
  const [bankExplanation, setBankExplanation] = useState<{ text: string; source: string | null } | null>(
    null,
  );

  const goToSummary = useCallback(
    (summary: Summary) => {
      navigation.replace("Summary", { summary, mode: mode ?? "training", section });
    },
    [navigation, mode, section],
  );

  useEffect(() => {
    if (start && start.session_id === sessionId) {
      setMode(start.mode);
      setSection(start.section);
      setQuestion(start.question);
      setLoading(false);
      return;
    }

    api
      .get<SessionStateResponse>(`/api/tests/${sessionId}`)
      .then((res) => {
        setMode(res.mode);
        setSection(res.section);
        if (res.finished && res.summary) {
          goToSummary(res.summary);
          return;
        }
        setQuestion(res.question);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Не удалось загрузить тест"))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  async function handleAnswer(letter: string) {
    if (answering || feedback) return;
    setAnswering(true);
    setError(null);
    try {
      const res = await api.post<AnswerResponse>(`/api/tests/${sessionId}/answer`, { letter });
      setFeedback({
        chosen: letter,
        correct: res.correct,
        correctLetter: res.correct_letter,
        correctText: res.correct_text,
      });
      setBankExplanation(res.explanation ? { text: res.explanation, source: res.source } : null);
      if (res.finished && res.summary) {
        setPendingSummary(res.summary);
      } else {
        setPendingQuestion(res.question);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось отправить ответ");
    } finally {
      setAnswering(false);
    }
  }

  function handleNext() {
    if (pendingSummary) {
      goToSummary(pendingSummary);
      return;
    }
    setQuestion(pendingQuestion);
    setPendingQuestion(null);
    setFeedback(null);
    setExplanation(null);
    setBankExplanation(null);
  }

  async function handleLearningNext() {
    if (answering) return;
    setAnswering(true);
    setError(null);
    try {
      const res = await api.post<LearningNextResponse>(`/api/tests/${sessionId}/next`);
      if (res.finished) {
        setLearningDoneMessage(res.message ?? "Просмотр завершён");
        setQuestion(null);
      } else {
        setQuestion(res.question);
        setExplanation(null);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось загрузить следующий вопрос");
    } finally {
      setAnswering(false);
    }
  }

  async function handleExplain() {
    if (explaining || explanation || !question) return;
    setExplaining(true);
    setError(null);
    try {
      const chosenText = feedback ? question.options.find((o) => o.letter === feedback.chosen)?.text ?? null : null;
      const res = await api.post<AiTextResponse>("/api/ai/explain", {
        question_id: question.id,
        chosen_text: chosenText,
      });
      setExplanation(res.text);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось получить объяснение");
    } finally {
      setExplaining(false);
    }
  }

  const handleExpire = useCallback(async () => {
    try {
      const res = await api.get<SessionStateResponse>(`/api/tests/${sessionId}`);
      if (res.finished && res.summary) {
        goToSummary(res.summary);
      }
    } catch {
      /* ignore — пользователь может повторить */
    }
  }, [sessionId, goToSummary]);

  if (loading) {
    return (
      <SafeAreaView style={styles.safe}>
        <ActivityIndicator color={colors.accent} style={styles.centerSpinner} />
      </SafeAreaView>
    );
  }

  if (error && !question) {
    return (
      <SafeAreaView style={styles.safe}>
        <View style={styles.content}>
          <Card>
            <ErrorText>{error}</ErrorText>
          </Card>
        </View>
      </SafeAreaView>
    );
  }

  if (learningDoneMessage) {
    return (
      <SafeAreaView style={styles.safe}>
        <View style={styles.centerMsgWrap}>
          <Text style={styles.centerMsg}>{learningDoneMessage}</Text>
          <PrimaryButton title="🏠 Главное меню" onPress={() => navigation.popToTop()} />
        </View>
      </SafeAreaView>
    );
  }

  if (!question) {
    return (
      <SafeAreaView style={styles.safe}>
        <View style={styles.centerMsgWrap}>
          <Text style={styles.centerMsg}>Вопросы закончились 🎉</Text>
        </View>
      </SafeAreaView>
    );
  }

  const isLearning = mode === "learning";

  // В режиме обучения разбор приходит вместе с вопросом, в остальных — вместе
  // с ответом. Он бесплатный и мгновенный, поэтому к Gemini идём только когда
  // разбора в банке нет (пока это вопросы по радиационной безопасности).
  const storedExplanation = isLearning
    ? question.explanation
      ? { text: question.explanation, source: question.source }
      : null
    : bankExplanation;

  const explainBlock = storedExplanation ? (
    <Card style={styles.explanationCard}>
      <Text style={styles.explanationLabel}>📖 Разбор</Text>
      <Text style={styles.explanationText}>
        {renderBold(storedExplanation.text, styles.explanationText)}
      </Text>
      {storedExplanation.source && (
        <Text style={styles.explanationSource}>{storedExplanation.source}</Text>
      )}
    </Card>
  ) : explanation ? (
    <Card style={styles.explanationCard}>
      <Text style={styles.explanationLabel}>🤖 Объяснение</Text>
      <Text style={styles.explanationText}>{renderBold(explanation, styles.explanationText)}</Text>
    </Card>
  ) : (
    <TouchableOpacity style={[styles.ghostBtn, explaining && styles.disabled]} onPress={handleExplain} disabled={explaining}>
      <Text style={styles.ghostBtnText}>{explaining ? "Думаю…" : "🤖 Объяснить"}</Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.safe} edges={["top", "left", "right"]}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>{mode ? MODE_LABELS[mode] : "Тест"}</Text>
      </View>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.progress}>
          Вопрос {question.index} из {question.total}
        </Text>

        {mode === "exam" && question.timer_seconds_left !== null && (
          <Timer secondsLeft={question.timer_seconds_left} onExpire={handleExpire} />
        )}

        <Card>
          <Text style={styles.questionText}>{question.question}</Text>
        </Card>

        <View style={styles.options}>
          {question.options.map((opt) => {
            let variant: "default" | "correct" | "wrong" = "default";
            if (isLearning) {
              if (opt.letter === question.correct_letter) variant = "correct";
            } else if (feedback) {
              if (opt.letter === feedback.correctLetter) variant = "correct";
              else if (opt.letter === feedback.chosen) variant = "wrong";
            }
            return (
              <TouchableOpacity
                key={opt.letter}
                style={[styles.option, variant === "correct" && styles.optionCorrect, variant === "wrong" && styles.optionWrong]}
                disabled={isLearning || answering || !!feedback}
                onPress={() => handleAnswer(opt.letter)}
              >
                <View
                  style={[
                    styles.optionLetter,
                    variant === "correct" && styles.optionLetterCorrect,
                    variant === "wrong" && styles.optionLetterWrong,
                  ]}
                >
                  <Text
                    style={[
                      styles.optionLetterText,
                      (variant === "correct" || variant === "wrong") && styles.optionLetterTextOnColor,
                    ]}
                  >
                    {opt.letter}
                  </Text>
                </View>
                <Text style={styles.optionText}>{opt.text}</Text>
              </TouchableOpacity>
            );
          })}
        </View>

        {error && <ErrorText>{error}</ErrorText>}

        {isLearning && (
          <>
            {explainBlock}
            <PrimaryButton title="Далее →" onPress={handleLearningNext} disabled={answering} />
          </>
        )}

        {!isLearning && feedback && (
          <>
            <View style={[styles.feedbackBanner, feedback.correct ? styles.feedbackCorrect : styles.feedbackWrong]}>
              <Text style={feedback.correct ? styles.feedbackTextCorrect : styles.feedbackTextWrong}>
                {feedback.correct ? "✅ Верно!" : `❌ Неверно. Правильный ответ: ${feedback.correctText}`}
              </Text>
            </View>
            {explainBlock}
            <PrimaryButton title={pendingSummary ? "Показать результат" : "Далее →"} onPress={handleNext} />
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.bg },
  header: { paddingHorizontal: 16, paddingVertical: 12 },
  headerTitle: { fontSize: 17, fontWeight: "700", color: colors.text },
  content: { padding: 16, gap: 14 },
  centerSpinner: { flex: 1 },
  centerMsgWrap: { flex: 1, alignItems: "center", justifyContent: "center", padding: 24, gap: 16 },
  centerMsg: { color: colors.textDim, fontSize: 15, textAlign: "center" },
  progress: { fontSize: 13, color: colors.textDim },
  questionText: { fontSize: 17, lineHeight: 24, fontWeight: "500", color: colors.text },
  options: { gap: 10 },
  option: {
    flexDirection: "row",
    gap: 12,
    alignItems: "flex-start",
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    padding: 14,
  },
  optionCorrect: { borderColor: colors.success, backgroundColor: colors.successBg },
  optionWrong: { borderColor: colors.danger, backgroundColor: colors.dangerBg },
  optionLetter: {
    width: 26,
    height: 26,
    borderRadius: 13,
    backgroundColor: colors.bgElevated,
    alignItems: "center",
    justifyContent: "center",
  },
  optionLetterCorrect: { backgroundColor: colors.success },
  optionLetterWrong: { backgroundColor: colors.danger },
  optionLetterText: { fontWeight: "700", fontSize: 13, color: colors.text },
  optionLetterTextOnColor: { color: "#ffffff" },
  optionText: { flex: 1, fontSize: 14.5, lineHeight: 20, color: colors.text },
  feedbackBanner: { borderRadius: 12, padding: 14 },
  feedbackCorrect: { backgroundColor: colors.successBg },
  feedbackWrong: { backgroundColor: colors.dangerBg },
  feedbackTextCorrect: { color: colors.success, fontWeight: "700", fontSize: 14.5 },
  feedbackTextWrong: { color: colors.danger, fontWeight: "700", fontSize: 14.5 },
  ghostBtn: {
    backgroundColor: colors.bgElevated,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: "center",
  },
  ghostBtnText: { color: colors.text, fontWeight: "700", fontSize: 15 },
  disabled: { opacity: 0.5 },
  explanationCard: { backgroundColor: colors.accentDim, borderColor: colors.accent },
  explanationLabel: { fontWeight: "700", fontSize: 13, marginBottom: 6, color: colors.accent },
  explanationText: { color: colors.text, fontSize: 14.5, lineHeight: 21 },
  explanationSource: {
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    fontSize: 12,
    color: colors.textDim,
  },
});

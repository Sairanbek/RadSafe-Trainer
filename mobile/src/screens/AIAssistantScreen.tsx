import { useRef, useState } from "react";
import { FlatList, KeyboardAvoidingView, Platform, StyleSheet, Text, TextInput, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { api, ApiError } from "../api/client";
import type { AiMessage, AiTextResponse } from "../api/types";
import { renderBold } from "../utils/markdown";
import { ErrorText } from "../components/UI";
import { colors, radius } from "../theme";
import type { TabScreenProps } from "../navigation/types";

const INTRO: AiMessage = {
  role: "model",
  text: "Здравствуйте! Я помогу с вопросами по радиационной безопасности и подготовке к аттестации. Спросите что-нибудь или запросите план обучения.",
};

export function AIAssistantScreen(_props: TabScreenProps<"Assistant">) {
  const [messages, setMessages] = useState<AiMessage[]>([INTRO]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const listRef = useRef<FlatList>(null);

  function scrollToEnd() {
    setTimeout(() => listRef.current?.scrollToEnd({ animated: true }), 50);
  }

  async function sendMessage(text: string) {
    if (!text.trim() || sending) return;
    setError(null);
    const history = messages;
    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");
    setSending(true);
    scrollToEnd();

    try {
      const res = await api.post<AiTextResponse>("/api/ai/chat", { message: text, history });
      setMessages((prev) => [...prev, { role: "model", text: res.text }]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось получить ответ");
    } finally {
      setSending(false);
      scrollToEnd();
    }
  }

  async function handleStudyPlan() {
    if (sending) return;
    setError(null);
    setSending(true);
    scrollToEnd();
    try {
      const res = await api.post<AiTextResponse>("/api/ai/study-plan");
      setMessages((prev) => [...prev, { role: "model", text: res.text }]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось получить план обучения");
    } finally {
      setSending(false);
      scrollToEnd();
    }
  }

  return (
    <SafeAreaView style={styles.safe} edges={["top", "left", "right"]}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>ИИ-ассистент</Text>
      </View>

      <TouchableOpacity style={styles.planBtn} onPress={handleStudyPlan} disabled={sending}>
        <Text style={styles.planBtnText}>📋 Получить план обучения</Text>
      </TouchableOpacity>

      <KeyboardAvoidingView style={styles.flex} behavior={Platform.OS === "ios" ? "padding" : undefined} keyboardVerticalOffset={90}>
        <FlatList
          ref={listRef}
          style={styles.flex}
          contentContainerStyle={styles.listContent}
          data={sending ? [...messages, { role: "model", text: "…" } as AiMessage] : messages}
          keyExtractor={(_, i) => String(i)}
          renderItem={({ item }) => (
            <View style={[styles.bubble, item.role === "user" ? styles.bubbleUser : styles.bubbleAssistant]}>
              <Text style={item.role === "user" ? styles.bubbleTextUser : styles.bubbleTextAssistant}>
                {renderBold(item.text, item.role === "user" ? styles.bubbleTextUser : styles.bubbleTextAssistant)}
              </Text>
            </View>
          )}
        />

        {error && (
          <View style={styles.errorWrap}>
            <ErrorText>{error}</ErrorText>
          </View>
        )}

        <View style={styles.inputRow}>
          <TextInput
            style={styles.input}
            placeholder="Задайте вопрос…"
            placeholderTextColor={colors.textDim}
            value={input}
            onChangeText={setInput}
            editable={!sending}
          />
          <TouchableOpacity
            style={[styles.sendBtn, (sending || !input.trim()) && styles.sendBtnDisabled]}
            onPress={() => sendMessage(input)}
            disabled={sending || !input.trim()}
          >
            <Text style={styles.sendBtnText}>→</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.bg },
  flex: { flex: 1 },
  header: { paddingHorizontal: 16, paddingVertical: 12 },
  headerTitle: { fontSize: 17, fontWeight: "700", color: colors.text },
  planBtn: {
    marginHorizontal: 16,
    marginBottom: 10,
    backgroundColor: colors.bgElevated,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: "center",
  },
  planBtnText: { color: colors.text, fontWeight: "700", fontSize: 14.5 },
  listContent: { padding: 16, gap: 10 },
  bubble: { maxWidth: "85%", padding: 12, borderRadius: radius },
  bubbleUser: { alignSelf: "flex-end", backgroundColor: colors.accent, borderBottomRightRadius: 4 },
  bubbleAssistant: {
    alignSelf: "flex-start",
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderColor: colors.border,
    borderBottomLeftRadius: 4,
  },
  bubbleTextUser: { color: colors.accentText, fontSize: 14.5, lineHeight: 21 },
  bubbleTextAssistant: { color: colors.text, fontSize: 14.5, lineHeight: 21 },
  errorWrap: { paddingHorizontal: 16, paddingBottom: 6 },
  inputRow: {
    flexDirection: "row",
    gap: 8,
    padding: 12,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  input: {
    flex: 1,
    backgroundColor: colors.bgElevated,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 10,
    color: colors.text,
    fontSize: 15,
  },
  sendBtn: {
    backgroundColor: colors.accent,
    borderRadius: 12,
    paddingHorizontal: 18,
    alignItems: "center",
    justifyContent: "center",
  },
  sendBtnDisabled: { opacity: 0.5 },
  sendBtnText: { color: colors.accentText, fontSize: 16, fontWeight: "700" },
});

import { useState } from "react";
import { Image, KeyboardAvoidingView, Platform, ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { api, ApiError } from "../api/client";
import type { MessageResponse } from "../api/types";
import { Card, ErrorText, FormField, PrimaryButton } from "../components/UI";
import { colors } from "../theme";
import type { AuthScreenProps } from "../navigation/types";

export function ForgotPasswordScreen({ navigation }: AuthScreenProps<"ForgotPassword">) {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit() {
    setError(null);
    setSubmitting(true);
    try {
      const res = await api.post<MessageResponse>("/api/auth/forgot-password", { email });
      setMessage(res.message);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось отправить запрос");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <KeyboardAvoidingView style={styles.flex} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.brand}>
          <Image source={require("../../assets/icon.png")} style={styles.logo} />
          <Text style={styles.title}>Восстановление пароля</Text>
          <Text style={styles.subtitle}>Укажите email, привязанный к аккаунту</Text>
        </View>

        <Card style={styles.form}>
          {message ? (
            <Text style={styles.message}>{message}</Text>
          ) : (
            <>
              <FormField
                label="Email"
                keyboardType="email-address"
                autoCapitalize="none"
                value={email}
                onChangeText={setEmail}
              />
              {error && <ErrorText>{error}</ErrorText>}
              <PrimaryButton
                title={submitting ? "Отправляем…" : "Отправить ссылку"}
                onPress={handleSubmit}
                disabled={submitting}
              />
            </>
          )}
        </Card>

        <TouchableOpacity onPress={() => navigation.navigate("Login")}>
          <Text style={styles.link}>Вернуться ко входу</Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.bg },
  container: { flexGrow: 1, justifyContent: "center", padding: 24, gap: 20 },
  brand: { alignItems: "center", gap: 4 },
  logo: { width: 72, height: 72, resizeMode: "contain", marginBottom: 8 },
  title: { fontSize: 20, fontWeight: "800", color: colors.text, textAlign: "center" },
  subtitle: { fontSize: 14, color: colors.textDim, textAlign: "center" },
  form: { gap: 14 },
  message: { color: colors.text, fontSize: 15, lineHeight: 22 },
  link: { color: colors.accent, fontWeight: "700", textAlign: "center", fontSize: 14 },
});

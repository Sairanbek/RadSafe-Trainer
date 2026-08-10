import { useState } from "react";
import { Image, KeyboardAvoidingView, Platform, ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { useAuth } from "../context/AuthContext";
import { ApiError } from "../api/client";
import { Card, ErrorText, FormField, PrimaryButton } from "../components/UI";
import { colors } from "../theme";
import type { AuthScreenProps } from "../navigation/types";

export function LoginScreen({ navigation }: AuthScreenProps<"Login">) {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit() {
    setError(null);
    setSubmitting(true);
    try {
      await login(email, password);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось войти");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <KeyboardAvoidingView style={styles.flex} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.brand}>
          <Image source={require("../../assets/icon.png")} style={styles.logo} />
          <Text style={styles.title}>RST — RadSafe Trainer</Text>
          <Text style={styles.subtitle}>Готовьтесь к аттестации эффективно</Text>
        </View>

        <Card style={styles.form}>
          <FormField
            label="Email"
            keyboardType="email-address"
            autoCapitalize="none"
            value={email}
            onChangeText={setEmail}
          />
          <FormField label="Пароль" secureTextEntry value={password} onChangeText={setPassword} />
          {error && <ErrorText>{error}</ErrorText>}
          <PrimaryButton title={submitting ? "Входим…" : "Войти"} onPress={handleSubmit} disabled={submitting} />
        </Card>

        <TouchableOpacity onPress={() => navigation.navigate("ForgotPassword")}>
          <Text style={styles.link}>Забыли пароль?</Text>
        </TouchableOpacity>
        <View style={styles.switchRow}>
          <Text style={styles.switchText}>Нет аккаунта? </Text>
          <TouchableOpacity onPress={() => navigation.navigate("Register")}>
            <Text style={styles.link}>Зарегистрироваться</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.bg },
  container: { flexGrow: 1, justifyContent: "center", padding: 24, gap: 20 },
  brand: { alignItems: "center", gap: 4 },
  logo: { width: 72, height: 72, resizeMode: "contain", marginBottom: 8 },
  title: { fontSize: 22, fontWeight: "800", color: colors.text, textAlign: "center" },
  subtitle: { fontSize: 14, color: colors.textDim, textAlign: "center" },
  form: { gap: 14 },
  link: { color: colors.accent, fontWeight: "700", textAlign: "center", fontSize: 14 },
  switchRow: { flexDirection: "row", justifyContent: "center" },
  switchText: { color: colors.textDim, fontSize: 14 },
});

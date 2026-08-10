import { useState } from "react";
import { Image, KeyboardAvoidingView, Platform, ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { useAuth } from "../context/AuthContext";
import { ApiError } from "../api/client";
import { Card, ErrorText, FormField, PrimaryButton } from "../components/UI";
import { colors } from "../theme";
import type { AuthScreenProps } from "../navigation/types";

export function RegisterScreen({ navigation }: AuthScreenProps<"Register">) {
  const { register } = useAuth();
  const [firstName, setFirstName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit() {
    setError(null);
    if (password.length < 8) {
      setError("Пароль должен быть не короче 8 символов");
      return;
    }
    setSubmitting(true);
    try {
      await register(email, password, firstName);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось зарегистрироваться");
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
          <FormField label="Имя" autoCapitalize="words" value={firstName} onChangeText={setFirstName} />
          <FormField
            label="Email"
            keyboardType="email-address"
            autoCapitalize="none"
            value={email}
            onChangeText={setEmail}
          />
          <FormField label="Пароль" secureTextEntry value={password} onChangeText={setPassword} />
          {error && <ErrorText>{error}</ErrorText>}
          <PrimaryButton
            title={submitting ? "Создаём аккаунт…" : "Зарегистрироваться"}
            onPress={handleSubmit}
            disabled={submitting}
          />
        </Card>

        <View style={styles.switchRow}>
          <Text style={styles.switchText}>Уже есть аккаунт? </Text>
          <TouchableOpacity onPress={() => navigation.navigate("Login")}>
            <Text style={styles.link}>Войти</Text>
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

import { useState } from "react";
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { Screen } from "../components/Screen";
import { useAuth } from "../context/AuthContext";
import { api, ApiError } from "../api/client";
import type { MessageResponse, User } from "../api/types";
import { Card, ErrorText, FormField, PrimaryButton } from "../components/UI";
import { colors } from "../theme";
import type { TabScreenProps } from "../navigation/types";

export function ProfileScreen(_props: TabScreenProps<"Profile">) {
  const { user, refreshMe, logout } = useAuth();

  const [firstName, setFirstName] = useState(user?.first_name ?? "");
  const [email, setEmail] = useState(user?.email ?? "");
  const [profileMessage, setProfileMessage] = useState<string | null>(null);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [profileSubmitting, setProfileSubmitting] = useState(false);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [passwordMessage, setPasswordMessage] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [passwordSubmitting, setPasswordSubmitting] = useState(false);

  async function handleProfileSubmit() {
    setProfileError(null);
    setProfileMessage(null);
    setProfileSubmitting(true);
    try {
      await api.patch<User>("/api/auth/me", { first_name: firstName, email });
      await refreshMe();
      setProfileMessage("Профиль обновлён");
    } catch (err) {
      setProfileError(err instanceof ApiError ? err.message : "Не удалось обновить профиль");
    } finally {
      setProfileSubmitting(false);
    }
  }

  async function handlePasswordSubmit() {
    setPasswordError(null);
    setPasswordMessage(null);

    if (newPassword.length < 8) {
      setPasswordError("Новый пароль должен быть не короче 8 символов");
      return;
    }

    setPasswordSubmitting(true);
    try {
      const res = await api.post<MessageResponse>("/api/auth/change-password", {
        current_password: currentPassword,
        new_password: newPassword,
      });
      setPasswordMessage(res.message);
      setCurrentPassword("");
      setNewPassword("");
    } catch (err) {
      setPasswordError(err instanceof ApiError ? err.message : "Не удалось изменить пароль");
    } finally {
      setPasswordSubmitting(false);
    }
  }

  return (
    <Screen
      title="Профиль"
      right={
        <TouchableOpacity onPress={logout}>
          <Text style={styles.logoutIcon}>⏻</Text>
        </TouchableOpacity>
      }
    >
      <Card style={styles.section}>
        <Text style={styles.sectionTitle}>Личные данные</Text>
        <FormField label="Имя" value={firstName} onChangeText={setFirstName} />
        <FormField label="Email" keyboardType="email-address" autoCapitalize="none" value={email} onChangeText={setEmail} />
        {profileMessage && <Text style={styles.successMsg}>{profileMessage}</Text>}
        {profileError && <ErrorText>{profileError}</ErrorText>}
        <PrimaryButton
          title={profileSubmitting ? "Сохраняем…" : "Сохранить"}
          onPress={handleProfileSubmit}
          disabled={profileSubmitting}
        />
      </Card>

      <Card style={styles.section}>
        <Text style={styles.sectionTitle}>Смена пароля</Text>
        <FormField label="Текущий пароль" secureTextEntry value={currentPassword} onChangeText={setCurrentPassword} />
        <FormField label="Новый пароль" secureTextEntry value={newPassword} onChangeText={setNewPassword} />
        {passwordMessage && <Text style={styles.successMsg}>{passwordMessage}</Text>}
        {passwordError && <ErrorText>{passwordError}</ErrorText>}
        <PrimaryButton
          title={passwordSubmitting ? "Меняем…" : "Изменить пароль"}
          onPress={handlePasswordSubmit}
          disabled={passwordSubmitting}
        />
      </Card>

      <Card style={styles.section}>
        <Text style={styles.sectionTitle}>Конфиденциальность</Text>
        <Text style={styles.privacyText}>
          Мы храним email, имя, результаты тестов и историю попыток для показа статистики.
          Сообщения ИИ-ассистенту обрабатываются сервисом Google Gemini. Чтобы удалить свои
          данные, напишите разработчику.
        </Text>
      </Card>
    </Screen>
  );
}

const styles = StyleSheet.create({
  logoutIcon: { fontSize: 20, color: colors.textDim },
  section: { gap: 14 },
  sectionTitle: { fontSize: 16, fontWeight: "700", color: colors.text },
  successMsg: { color: colors.success, fontWeight: "600", fontSize: 14 },
  privacyText: { color: colors.textDim, fontSize: 13, lineHeight: 19 },
});

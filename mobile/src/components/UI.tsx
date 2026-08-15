import type { ReactNode } from "react";
import {
  ActivityIndicator,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
  type TextInputProps,
} from "react-native";
import { colors, radius } from "../theme";

export function Card({ children, style }: { children: ReactNode; style?: object }) {
  return <View style={[styles.card, style]}>{children}</View>;
}

export function PrimaryButton({
  title,
  onPress,
  disabled,
  loading,
}: {
  title: string;
  onPress: () => void;
  disabled?: boolean;
  loading?: boolean;
}) {
  return (
    <TouchableOpacity
      style={[styles.btn, styles.btnPrimary, disabled && styles.btnDisabled]}
      onPress={onPress}
      disabled={disabled || loading}
    >
      {loading ? <ActivityIndicator color={colors.accentText} /> : <Text style={styles.btnPrimaryText}>{title}</Text>}
    </TouchableOpacity>
  );
}

export function GhostButton({ title, onPress, disabled }: { title: string; onPress: () => void; disabled?: boolean }) {
  return (
    <TouchableOpacity style={[styles.btn, styles.btnGhost, disabled && styles.btnDisabled]} onPress={onPress} disabled={disabled}>
      <Text style={styles.btnGhostText}>{title}</Text>
    </TouchableOpacity>
  );
}

export function ListItem({
  title,
  count,
  onPress,
  disabled,
}: {
  title: string;
  count?: number;
  onPress: () => void;
  disabled?: boolean;
}) {
  return (
    <TouchableOpacity style={[styles.listItem, disabled && styles.btnDisabled]} onPress={onPress} disabled={disabled}>
      <Text style={styles.listItemText}>{title}</Text>
      {count !== undefined && (
        <View style={styles.countPill}>
          <Text style={styles.countText}>{count}</Text>
        </View>
      )}
    </TouchableOpacity>
  );
}

export function FormField({
  label,
  ...inputProps
}: { label: string } & TextInputProps) {
  return (
    <View style={styles.field}>
      <Text style={styles.fieldLabel}>{label}</Text>
      <TextInput style={styles.input} placeholderTextColor={colors.textDim} {...inputProps} />
    </View>
  );
}

export function ErrorText({ children }: { children: ReactNode }) {
  return <Text style={styles.errorText}>{children}</Text>;
}

export function ConsentCheckbox({
  checked,
  onToggle,
  children,
}: {
  checked: boolean;
  onToggle: () => void;
  children: ReactNode;
}) {
  return (
    <TouchableOpacity style={styles.consentRow} onPress={onToggle} activeOpacity={0.7}>
      <View style={[styles.checkbox, checked && styles.checkboxChecked]}>
        {checked && <Text style={styles.checkboxMark}>✓</Text>}
      </View>
      <Text style={styles.consentText}>{children}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius,
    padding: 16,
  },
  btn: {
    borderRadius: 12,
    paddingVertical: 14,
    paddingHorizontal: 18,
    alignItems: "center",
    justifyContent: "center",
  },
  btnPrimary: {
    backgroundColor: colors.accent,
  },
  btnPrimaryText: {
    color: colors.accentText,
    fontWeight: "700",
    fontSize: 15,
  },
  btnGhost: {
    backgroundColor: colors.bgElevated,
    borderWidth: 1,
    borderColor: colors.border,
  },
  btnGhostText: {
    color: colors.text,
    fontWeight: "700",
    fontSize: 15,
  },
  btnDisabled: {
    opacity: 0.5,
  },
  listItem: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 10,
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    padding: 14,
  },
  listItemText: {
    color: colors.text,
    fontSize: 15,
    flexShrink: 1,
  },
  countPill: {
    backgroundColor: colors.bgElevated,
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 3,
  },
  countText: {
    color: colors.textDim,
    fontSize: 12.5,
  },
  field: {
    gap: 6,
  },
  fieldLabel: {
    fontSize: 13,
    color: colors.textDim,
  },
  input: {
    backgroundColor: colors.bgElevated,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    paddingVertical: 12,
    paddingHorizontal: 14,
    fontSize: 15,
    color: colors.text,
  },
  errorText: {
    color: colors.danger,
    fontSize: 13.5,
  },
  consentRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 8,
  },
  checkbox: {
    width: 20,
    height: 20,
    borderRadius: 5,
    borderWidth: 1.5,
    borderColor: colors.border,
    alignItems: "center",
    justifyContent: "center",
    marginTop: 1,
    flexShrink: 0,
  },
  checkboxChecked: {
    backgroundColor: colors.accent,
    borderColor: colors.accent,
  },
  checkboxMark: {
    color: colors.accentText,
    fontSize: 13,
    fontWeight: "700",
    lineHeight: 14,
  },
  consentText: {
    flex: 1,
    fontSize: 12.5,
    color: colors.textDim,
    lineHeight: 18,
  },
});

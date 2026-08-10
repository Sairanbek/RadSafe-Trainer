import type { ReactNode } from "react";
import { Image, ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useNavigation } from "@react-navigation/native";
import { colors } from "../theme";

export function Screen({
  title,
  children,
  scroll = true,
  showBack = false,
  right,
}: {
  title: string;
  children: ReactNode;
  scroll?: boolean;
  showBack?: boolean;
  right?: ReactNode;
}) {
  const navigation = useNavigation();
  const Body = scroll ? ScrollView : View;

  return (
    <SafeAreaView style={styles.safe} edges={["top", "left", "right"]}>
      <View style={styles.header}>
        {showBack ? (
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
            <Text style={styles.backText}>‹</Text>
          </TouchableOpacity>
        ) : (
          <Image source={require("../../assets/icon.png")} style={styles.logo} />
        )}
        <Text style={styles.title} numberOfLines={1}>
          {title}
        </Text>
        <View style={styles.spacer} />
        {right}
      </View>
      <Body
        style={styles.body}
        contentContainerStyle={scroll ? styles.scrollContent : styles.flexContent}
      >
        {children}
      </Body>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: colors.bg,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  logo: {
    width: 26,
    height: 26,
    resizeMode: "contain",
  },
  backBtn: {
    width: 26,
    alignItems: "flex-start",
  },
  backText: {
    fontSize: 26,
    color: colors.text,
    lineHeight: 26,
  },
  title: {
    fontSize: 17,
    fontWeight: "700",
    color: colors.text,
    flexShrink: 1,
  },
  spacer: {
    flex: 1,
  },
  body: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
    gap: 14,
    flexGrow: 1,
  },
  flexContent: {
    flex: 1,
    padding: 16,
    gap: 14,
  },
});

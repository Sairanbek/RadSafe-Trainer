import { Text, type TextStyle } from "react-native";

/** Рендерит **жирный** текст из ответов ИИ как вложенные <Text>. */
export function renderBold(text: string, baseStyle?: TextStyle) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <Text key={i} style={[baseStyle, { fontWeight: "700" }]}>
          {part.slice(2, -2)}
        </Text>
      );
    }
    return (
      <Text key={i} style={baseStyle}>
        {part}
      </Text>
    );
  });
}

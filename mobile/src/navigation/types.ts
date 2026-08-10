import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import type { CompositeScreenProps } from "@react-navigation/native";
import type { BottomTabScreenProps } from "@react-navigation/bottom-tabs";
import type { Mode, StartTestResponse, Summary } from "../api/types";

export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
  ForgotPassword: undefined;
};

export type TabParamList = {
  Dashboard: undefined;
  Stats: undefined;
  History: undefined;
  Assistant: undefined;
  Profile: undefined;
};

export type RootStackParamList = {
  Tabs: undefined;
  Sections: { mode: Mode } | undefined;
  Subsections: { section: string; mode: Mode };
  Test: { sessionId: number; start?: StartTestResponse };
  Summary: { summary: Summary; mode: Mode; section: string };
};

export type AuthScreenProps<T extends keyof AuthStackParamList> = NativeStackScreenProps<AuthStackParamList, T>;

export type RootScreenProps<T extends keyof RootStackParamList> = NativeStackScreenProps<RootStackParamList, T>;

export type TabScreenProps<T extends keyof TabParamList> = CompositeScreenProps<
  BottomTabScreenProps<TabParamList, T>,
  NativeStackScreenProps<RootStackParamList>
>;

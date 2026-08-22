import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { Platform } from "react-native";
import * as SecureStore from "expo-secure-store";
import { api } from "../api/client";
import { useAuth } from "./AuthContext";
import type { Module } from "../api/types";

/**
 * Выбранное направление подготовки (радиационная безопасность, радиология,
 * госслужба). Все запросы к банку вопросов, статистике и истории идут в
 * границах одного направления.
 *
 * Хранится там же, где токены: expo-secure-store на устройстве и localStorage
 * в web-режиме. Секрета тут нет, просто не заводим ради одной строки ещё одну
 * зависимость на хранилище.
 */

const STORAGE_KEY = "rst_module";
export const DEFAULT_MODULE = "Радиационная безопасность";

async function readStored(): Promise<string | null> {
  if (Platform.OS === "web") return window.localStorage.getItem(STORAGE_KEY);
  return SecureStore.getItemAsync(STORAGE_KEY);
}

async function writeStored(value: string): Promise<void> {
  if (Platform.OS === "web") {
    window.localStorage.setItem(STORAGE_KEY, value);
    return;
  }
  await SecureStore.setItemAsync(STORAGE_KEY, value);
}

interface ModuleContextValue {
  module: string;
  setModule: (name: string) => void;
  modules: Module[];
  loading: boolean;
}

const ModuleContext = createContext<ModuleContextValue | null>(null);

export function ModuleProvider({ children }: { children: ReactNode }) {
  const [module, setModuleState] = useState<string>(DEFAULT_MODULE);
  const [modules, setModules] = useState<Module[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    readStored().then((saved) => {
      if (saved) setModuleState(saved);
    });
  }, []);

  // Список направлений тянем только после входа: до него /api/modules отдаёт
  // 401, и без перезапроса пользователь остался бы без переключателя.
  useEffect(() => {
    if (!user) {
      setModules([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    api
      .get<Module[]>("/api/modules")
      .then((list) => {
        setModules(list);
        if (list.length > 0 && !list.some((m) => m.name === module)) {
          setModule(list[0].name);
        }
      })
      .catch(() => setModules([]))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  function setModule(name: string) {
    setModuleState(name);
    void writeStored(name);
  }

  return (
    <ModuleContext.Provider value={{ module, setModule, modules, loading }}>
      {children}
    </ModuleContext.Provider>
  );
}

export function useModule(): ModuleContextValue {
  const ctx = useContext(ModuleContext);
  if (!ctx) throw new Error("useModule используется вне ModuleProvider");
  return ctx;
}

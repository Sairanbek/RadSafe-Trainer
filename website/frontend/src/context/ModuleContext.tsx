import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api } from "../api/client";
import { useAuth } from "./AuthContext";
import type { Module } from "../api/types";

/**
 * Выбранное направление подготовки (радиационная безопасность, радиология,
 * госслужба). Все запросы к банку вопросов, статистике и истории идут в
 * границах одного направления — без него аттестация подмешивала бы вопросы
 * из чужой предметной области.
 */

const STORAGE_KEY = "rst_module";
export const DEFAULT_MODULE = "Радиационная безопасность";

interface ModuleContextValue {
  module: string;
  setModule: (name: string) => void;
  modules: Module[];
  loading: boolean;
}

const ModuleContext = createContext<ModuleContextValue | null>(null);

export function ModuleProvider({ children }: { children: ReactNode }) {
  const [module, setModuleState] = useState<string>(
    () => window.localStorage.getItem(STORAGE_KEY) ?? DEFAULT_MODULE,
  );
  const [modules, setModules] = useState<Module[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  // Список направлений запрашиваем только с появлением пользователя: провайдер
  // висит над всеми маршрутами, включая страницу входа, и запрос на старте
  // возвращал бы 401 и больше не повторялся.
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
        // Сохранённое направление могло исчезнуть из банка — откатываемся
        // на первое доступное, иначе пользователь увидит пустые разделы.
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
    window.localStorage.setItem(STORAGE_KEY, name);
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

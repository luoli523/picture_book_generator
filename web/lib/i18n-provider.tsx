"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import Link from "next/link";
import { BookOpen } from "lucide-react";
import { translations, type Locale } from "./i18n";

interface I18nContextType {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string) => string;
}

const I18nContext = createContext<I18nContextType | null>(null);

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("en");

  useEffect(() => {
    const stored = localStorage.getItem("locale") as Locale | null;
    if (stored === "zh" || stored === "en") {
      setLocaleState(stored);
    } else if (navigator.language.startsWith("zh")) {
      setLocaleState("zh");
    }
  }, []);

  const setLocale = useCallback((l: Locale) => {
    setLocaleState(l);
    localStorage.setItem("locale", l);
    document.documentElement.lang = l;
  }, []);

  const t = useCallback(
    (key: string) => translations[locale][key] ?? key,
    [locale],
  );

  return (
    <I18nContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within I18nProvider");
  return ctx;
}

export function useT() {
  return useI18n().t;
}

/** Global navigation bar with language toggle */
export function NavBar() {
  const { locale, setLocale, t } = useI18n();

  return (
    <nav className="sticky top-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
      <div className="max-w-5xl mx-auto flex items-center justify-between px-6 h-14">
        <Link href="/" className="flex items-center gap-2 text-primary font-extrabold text-lg">
          <BookOpen size={22} strokeWidth={2.5} />
          {t("nav.title")}
        </Link>
        <button
          type="button"
          onClick={() => setLocale(locale === "zh" ? "en" : "zh")}
          className="px-3 py-1.5 rounded-lg text-sm font-semibold border border-border hover:border-primary/40 hover:bg-muted transition"
        >
          {locale === "zh" ? "EN" : "中文"}
        </button>
      </div>
    </nav>
  );
}

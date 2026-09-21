import { createContext, useContext, useEffect, useMemo, useState } from 'react';

import en from '../locales/en/common.json';
import te from '../locales/te/common.json';
import hi from '../locales/hi/common.json';
import ta from '../locales/ta/common.json';
import kn from '../locales/kn/common.json';
import ml from '../locales/ml/common.json';
import mr from '../locales/mr/common.json';
import bn from '../locales/bn/common.json';

const CATALOG = { en, te, hi, ta, kn, ml, mr, bn };

export const LANG_META = [
  { code: 'en', label: 'English', native: 'English', speech: 'en-IN' },
  { code: 'te', label: 'Telugu', native: 'తెలుగు', speech: 'te-IN' },
  { code: 'hi', label: 'Hindi', native: 'हिन्दी', speech: 'hi-IN' },
  { code: 'ta', label: 'Tamil', native: 'தமிழ்', speech: 'ta-IN' },
  { code: 'kn', label: 'Kannada', native: 'ಕನ್ನಡ', speech: 'kn-IN' },
  { code: 'ml', label: 'Malayalam', native: 'മലയാളം', speech: 'ml-IN' },
  { code: 'mr', label: 'Marathi', native: 'मराठी', speech: 'mr-IN' },
  { code: 'bn', label: 'Bengali', native: 'বাংলা', speech: 'bn-IN' },
];

const I18nContext = createContext(null);

function deepGet(obj, path) {
  return path.split('.').reduce((acc, key) => (acc == null ? undefined : acc[key]), obj);
}

export function I18nProvider({ children }) {
  const [lang, setLangState] = useState(() => localStorage.getItem('sangam-lang') || 'en');

  const setLang = (code) => {
    const next = CATALOG[code] ? code : 'en';
    setLangState(next);
    localStorage.setItem('sangam-lang', next);
  };

  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  const value = useMemo(() => {
    const dict = CATALOG[lang] || en;
    const t = (path, fallback = '') => {
      const v = deepGet(dict, path);
      if (v != null) return v;
      const enVal = deepGet(en, path);
      return enVal != null ? enVal : fallback || path;
    };
    const speechCode = LANG_META.find((l) => l.code === lang)?.speech || 'en-IN';
    return { lang, setLang, t, speechCode, languages: LANG_META };
  }, [lang]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error('useI18n must be used within I18nProvider');
  return ctx;
}

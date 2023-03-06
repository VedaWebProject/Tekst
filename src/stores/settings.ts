import { ref, type Ref } from 'vue';
import { defineStore } from 'pinia';
import { i18n, setI18nLanguage } from '@/i18n';
import type { AvailableLanguage } from '@/i18n';

declare type ThemeMode = 'light' | 'dark';

export const useSettingsStore = defineStore('settings', () => {
  // theme
  const theme: Ref<ThemeMode> = ref('light');

  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light';
  }

  // language
  const language = ref(i18n.global.locale);
  const languages = i18n.global.availableLocales;

  async function setLanguage(l: string = language.value): Promise<AvailableLanguage> {
    return setI18nLanguage(l).then((lang: AvailableLanguage) => {
      language.value = lang.key;
      return lang;
    });
  }

  return {
    theme,
    toggleTheme,
    language,
    languages,
    setLanguage,
  };
});

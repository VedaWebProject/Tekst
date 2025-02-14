import helpTranslationsModules from '@/assets/i18n/help';
import { useStateStore } from '@/stores';

export interface HelpText {
  title: string | null;
  content: string;
}

const helpTexts: Record<string, Record<string, HelpText>> = {};

export function useHelp() {
  const state = useStateStore();

  async function _getHelpTexts(locale: string = state.locale): Promise<Record<string, HelpText>> {
    if (!helpTexts[locale]) {
      if (helpTranslationsModules[locale]) {
        try {
          helpTexts[locale] = (await helpTranslationsModules[locale]()).default;
        } catch {
          console.error(`Could not load help text translations for locale '${locale}'.`);
          return Promise.reject('Locale not found');
        }
      } else {
        return Promise.reject('Locale not found');
      }
    }
    return helpTexts[locale];
  }

  async function getHelpText(helpKey: string): Promise<HelpText> {
    try {
      return (await _getHelpTexts())[helpKey];
    } catch {
      console.error(
        `Could not load help text translation '${helpKey}' for locale '${state.locale}'.`
      );
      return Promise.reject('Locale not found');
    }
  }

  return { getHelpText };
}

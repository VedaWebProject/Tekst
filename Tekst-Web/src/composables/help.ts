import helpTranslationsModules from '@/assets/i18n/help';
import { useStateStore } from '@/stores';

type HelpScope = 'v' | 'u' | 's';

export interface HelpText {
  title: string | null;
  content: string;
  scope: HelpScope;
}

const _scopesMap: Record<HelpScope, HelpScope[]> = {
  v: ['v'],
  u: ['u', 'v'],
  s: ['s', 'u', 'v'],
} as const;

const helpTexts: Record<string, Record<string, HelpText>> = {};

export function useHelp() {
  const state = useStateStore();

  async function getHelpTexts(
    locale: string = state.locale,
    scope?: HelpScope
  ): Promise<Record<string, HelpText>> {
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
    if (!scope) {
      return helpTexts[locale];
    } else {
      return Object.fromEntries(
        Object.entries(helpTexts[locale]).filter((entry) =>
          _scopesMap[scope].includes(entry[1].scope)
        )
      );
    }
  }

  async function getHelpText(helpKey: string): Promise<HelpText> {
    try {
      return (await getHelpTexts())[helpKey];
    } catch {
      console.error(
        `Could not load help text translation '${helpKey}' for locale '${state.locale}'.`
      );
      return Promise.reject('Locale not found');
    }
  }

  return { getHelpText, getHelpTexts };
}

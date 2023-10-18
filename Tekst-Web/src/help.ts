import helpTranslationsModules from '@/assets/help';
import { useStateStore } from './stores';

export interface HelpText {
  title: string | null;
  content: string;
}

const helpTexts: Record<string, Record<string, HelpText>> = {};

export function useHelp() {
  const state = useStateStore();

  async function getHelpTexts(locale: string = state.locale): Promise<Record<string, HelpText>> {
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
      return (await getHelpTexts())[helpKey];
    } catch {
      console.error(
        `Could not load help text translation '${helpKey}' for locale '${state.locale}'.`
      );
      return Promise.reject('Locale not found');
    }

    // if (!helpTexts[state.locale] || !helpTexts[state.locale][helpKey]) {
    //   const msg = `Could not load help text translation '${helpKey}' for locale '${state.locale}'.`;
    //   console.error(msg);
    //   return Promise.reject(msg);
    // }
    // return (await helpTexts[state.locale][helpKey]()).default.content;
  }

  // async function getAllHelpTexts(): Promise<Record<string, string>> {
  //   if (!helpTexts[state.locale]) return Promise.reject('Locale not found');
  //   const out: Record<string, string> = {};
  //   for (const key in helpTexts[state.locale]) {
  //     out[key] = await getHelpText(key);
  //   }
  //   return out;
  // }

  return { getHelpText, getHelpTexts };
}

import type { Translation } from './api';

export function hashCode(obj: any) {
  const string = JSON.stringify(obj);
  let hash = 0;
  for (let i = 0; i < string.length; i++) {
    const code = string.charCodeAt(i);
    hash = (hash << 5) - hash + code;
    hash = hash & hash;
  }
  return hash;
}

export function pickTranslation(translations?: Translation[], localeKey: string = '*') {
  if (!translations) {
    return '';
  }
  return (
    (
      translations.find((t) => t.locale === localeKey) ||
      translations.find((t) => t.locale === '*') ||
      translations.find((t) => t.locale === 'enUS') ||
      translations[0]
    )?.translation || ''
  );
}

import type { SubtitleTranslation } from '@/api';

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

export function determineTextSubtitle(
  subtitleTranslations: SubtitleTranslation[],
  localeKey: string
) {
  const subtitleTranslation =
    subtitleTranslations.find((s) => s && s.locale === localeKey) ||
    subtitleTranslations.find((s) => s && s.locale === 'enUS') ||
    subtitleTranslations[0];
  return subtitleTranslation ? subtitleTranslation.subtitle : '';
}

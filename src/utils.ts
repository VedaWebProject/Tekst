import type { SubtitleTranslation } from './openapi';

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

export function keepChangedRecords(
  changed: Record<string, any | null>,
  original: Record<string, any | null>,
  forceKeep: string[] = []
) {
  return Object.keys(changed).reduce((prev, curr) => {
    if (changed[curr] !== original[curr] || forceKeep.includes(curr)) prev[curr] = changed[curr];
    return prev;
  }, {} as Record<string, any | null>);
}

export function haveRecordsChanged(changed: Record<string, any>, original: Record<string, any>) {
  for (const key in original) {
    if (JSON.stringify(changed[key]) !== JSON.stringify(original[key])) {
      return true;
    }
  }
  return false;
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

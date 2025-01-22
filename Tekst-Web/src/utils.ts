import type { LocationRead, TextRead, Translation, TranslationLocaleKey } from '@/api';
import { NIcon } from 'naive-ui';
import { h, type Component } from 'vue';

export function hashCode(obj: object) {
  const string = JSON.stringify(obj);
  let hash = 0;
  for (let i = 0; i < string.length; i++) {
    const code = string.charCodeAt(i);
    hash = (hash << 5) - hash + code;
    hash = hash & hash;
  }
  return hash;
}

export function pickTranslation(
  translations?: Translation[],
  localeKey: TranslationLocaleKey = '*'
) {
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

export function renderIcon(icon?: Component, color?: string) {
  return () => h(NIcon, { color }, { default: () => (icon ? h(icon) : null) });
}

export function utcToLocalTime(utcDateTimeString: string): Date {
  return new Date(utcDateTimeString + (!utcDateTimeString.toUpperCase().endsWith('Z') ? 'Z' : ''));
}

export function getFullLocationLabel(
  locationPath: LocationRead[] = [],
  textLevelLabels: string[] = [],
  text?: TextRead
) {
  return locationPath
    .map((n) => {
      if (!n.label) return '';
      const lvlLabel = textLevelLabels[n.level] || '';
      const locationPrefix = text?.labeledLocation && lvlLabel ? `${lvlLabel}: ` : '';
      return locationPrefix + n.label;
    })
    .join(text?.locDelim || ', ');
}

export async function checkUrl(url?: string, method: 'GET' | 'HEAD' = 'HEAD'): Promise<boolean> {
  if (!url) return false;
  try {
    new URL(url);
    const response = await fetch(url, { method });
    return response.ok;
  } catch {
    return false;
  }
}

export function isOverlayOpen() {
  return document.querySelectorAll('.n-modal-body-wrapper, .n-image-preview-overlay').length > 0;
}

export function isInputFocused() {
  return (
    document.activeElement?.tagName === 'INPUT' || document.activeElement?.tagName === 'TEXTAREA'
  );
}

export async function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

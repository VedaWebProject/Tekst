import type { LocationRead, TextRead, Translation, TranslationLocaleKey } from '@/api';
import { uniqBy } from 'lodash-es';
import { NIcon } from 'naive-ui';
import { h, type Component } from 'vue';
import type { components } from './api/schema';

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
    document.activeElement?.tagName === 'INPUT' ||
    document.activeElement?.tagName === 'TEXTAREA' ||
    !!document.querySelector('.cm-editor.cm-focused')
  );
}

export async function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function groupAndSortItems(
  items: { key: string; value: string[] }[],
  cfg: components['schemas']['ItemIntegrationConfig'],
  unique: boolean = true,
  filterNullishKeys: boolean = true
): {
  group?: string;
  items: { key: string; value: string[] }[];
}[] {
  const _compare = (a: { key: string; value: string[] }, b: { key: string; value: string[] }) => {
    const comp =
      (itemPropsByKey[a.key] ? itemPropsByKey[a.key].index : Number.MAX_SAFE_INTEGER) -
      (itemPropsByKey[b.key] ? itemPropsByKey[b.key].index : Number.MAX_SAFE_INTEGER);
    if (comp !== 0) return comp;
    return a.key.localeCompare(b.key);
  };
  const proc_items = (unique ? uniqBy(items, 'key') : items).filter(
    (item) => !filterNullishKeys || item.key != null
  );
  const itemPropsByKey = Object.fromEntries(
    cfg.itemProps.map((props, i) => [props.key, { index: i, group: props.group }])
  );
  const grouped = cfg.groups
    .map((g) => ({
      group: g.key,
      items: proc_items
        .filter((item) => !!itemPropsByKey[item.key] && itemPropsByKey[item.key].group === g.key)
        .sort(_compare),
    }))
    .filter((g) => !!g.items.length);
  const ungrouped = [
    {
      group: undefined,
      items: proc_items
        .filter(
          (item) =>
            !itemPropsByKey[item.key] ||
            !itemPropsByKey[item.key].group ||
            !cfg.groups.map((g) => g.key).includes(itemPropsByKey[item.key].group as string)
        )
        .sort(_compare),
    },
  ].filter((g) => !!g.items.length);
  return [...grouped, ...ungrouped];
}

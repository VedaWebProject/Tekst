import type {
  LocationRead,
  TextRead,
  Translation,
  TranslationLocaleKey,
  UserReadPublic,
} from '@/api';
import type { components } from '@/api/schema';
import { $t, getLocaleProfile } from '@/i18n';
import { uniqBy } from 'lodash-es';
import { NIcon } from 'naive-ui';
import { h, type Component } from 'vue';
import env from './env';

export function hashCode(obj: unknown) {
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

export function renderIcon(icon?: Component, color?: string, size?: string | number) {
  return icon ? () => h(NIcon, { color, size }, { default: () => h(icon) }) : undefined;
}

export function utcToLocalTime(utcDateTimeString: string): Date {
  return new Date(utcDateTimeString + (!utcDateTimeString.toUpperCase().endsWith('Z') ? 'Z' : ''));
}

export function utcToDateString(
  utcTimeString?: string | null,
  localeCode: Intl.UnicodeBCP47LocaleIdentifier = 'en-US'
): string {
  if (!utcTimeString) return '';
  return utcToLocalTime(utcTimeString).toLocaleDateString(
    getLocaleProfile(localeCode).displayShort
  );
}

export function utcToDateTimeString(
  utcTimeString?: string | null,
  localeCode: Intl.UnicodeBCP47LocaleIdentifier = 'en-US'
): string {
  if (!utcTimeString) return '';
  return utcToLocalTime(utcTimeString).toLocaleString(getLocaleProfile(localeCode).displayShort);
}

export function getFullLocationLabel(
  locationPath: LocationRead[] = [],
  textLevelLabels: string[] = [],
  text?: TextRead
) {
  if (!text) return '';
  return (
    (text.slugInLocLabels ? `${text.slug.toUpperCase()} ` : '') +
    locationPath
      .map((n) => {
        if (!n.label) return '';
        const lvlLabel = textLevelLabels[n.level] || '';
        const locationPrefix = text?.labeledLocation && lvlLabel ? `${lvlLabel}: ` : '';
        return locationPrefix + n.label;
      })
      .join(text?.locDelim || ', ')
  );
}

export async function checkUrl(url?: string, method: 'GET' | 'HEAD' = 'HEAD'): Promise<boolean> {
  if (!url) return false;
  try {
    return (await fetch(new URL(url), { method })).ok;
  } catch {
    return false;
  }
}

export async function validateUrlInput(input: HTMLInputElement) {
  if (!input.value || !URL.canParse(input.value) || !(await checkUrl(input.value))) {
    input.style.color = 'var(--error-color)';
    input.title = $t('contents.warnUrlInvalid', { url: input.value });
  } else {
    input.style.color = 'var(--success-color)';
    input.title = '';
  }
}

export function isOverlayOpen() {
  return (
    document.querySelectorAll('.n-modal-body-wrapper, .n-image-preview-overlay, .driver-overlay')
      .length > 0
  );
}

export function isInputFocused() {
  return (
    document.activeElement?.tagName === 'INPUT' ||
    document.activeElement?.tagName === 'TEXTAREA' ||
    !!document.querySelector('.cm-editor.cm-focused')
  );
}

export async function delay(ms: number = 50) {
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

export function userDisplayText(user: UserReadPublic, showAffiliation: boolean = true) {
  return (
    (user.name ? user.name : `@${user.username}`) +
    (showAffiliation && user.affiliation ? ` (${user.affiliation})` : '')
  );
}

/**
 * Replaces the `{{res_url}}` placeholder in the given text with the info URL of the given resource.
 * Removes the placeholder if the resource ID or text slug are not provided.
 * @param text Text to replace the placeholder in
 * @param textSlug Slug of the target working text
 * @param resourceId  ID of the resource to link to
 * @returns Text with the placeholder replaced or removed.
 */
export function replaceResUrlPh(text?: string | null, textSlug?: string, resourceId?: string) {
  if (!textSlug || !resourceId) {
    console.warn('replaceResUrlPh: textSlug or resourceId is undefined');
    return text?.replace(/\{\{\s*res_url\s*\}\}/g, '') ?? '';
  } else {
    return (
      text?.replace(
        /\{\{\s*res_url\s*\}\}/g,
        `${origin}${env.WEB_PATH_STRIPPED}/texts/${textSlug}/resources#id=${resourceId}`
      ) ?? ''
    ).trim();
  }
}

/**
 * Replaces the `{{curr_date}}` placeholder with the current date in the specified locale.
 * If the locale is not specified, `enUS` is used.
 * @param text
 * @param locale
 * @returns Text with the `{{curr_date}}` placeholder replaced with the current date.
 */
export function replaceCurrDatePh(text?: string | null, locale?: string) {
  return (
    text?.replace(
      /\{\{\s*curr_date\s*\}\}/g,
      new Date().toLocaleDateString(getLocaleProfile(locale ?? 'enUS').displayShort)
    ) ?? ''
  ).trim();
}

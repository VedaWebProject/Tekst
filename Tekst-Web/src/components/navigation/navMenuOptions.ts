import { NIcon, type MenuOption } from 'naive-ui';
import { h, type Component, computed } from 'vue';
import { RouterLink, type RouteLocationRaw } from 'vue-router';
import { $t } from '@/i18n';
import { useBrowseStore, useStateStore } from '@/stores';
import { usePlatformData } from '@/composables/platformData';
import type { ClientSegmentHead } from '@/api';
import { pickTranslation } from '@/utils';

import {
  EyeIcon,
  ManageAccountIcon,
  TextsIcon,
  BarChartIcon,
  AddCircleIcon,
  SettingsIcon,
  InfoIcon,
  BookIcon,
  SearchIcon,
} from '@/icons';

function renderIcon(icon: Component, noop: boolean = false) {
  return noop ? undefined : () => h(NIcon, undefined, { default: () => h(icon) });
}

function renderLink(
  label: string | (() => string),
  to: RouteLocationRaw,
  props?: Record<string, unknown>
) {
  return () =>
    h(
      RouterLink,
      {
        ...props,
        to,
        style: {
          fontSize: 'var(--app-ui-font-size)',
        },
      },
      { default: label }
    );
}

export function useMainMenuOptions(showIcons: boolean = true) {
  const { pfData } = usePlatformData();
  const state = useStateStore();
  const browse = useBrowseStore();

  const infoPagesOptions = computed(() => {
    const pages: ClientSegmentHead[] = [];
    // add pages with current locale
    pages.push(...(pfData.value?.infoSegments.filter((p) => p.locale === state.locale) || []));
    // add pages without locale
    pages.push(
      ...(pfData.value?.infoSegments.filter(
        (p) => p.locale === '*' && !pages.find((i) => i.key === p.key)
      ) || [])
    );
    // add pages with enUS locale (fallback)
    pages.push(
      ...(pfData.value?.infoSegments.filter(
        (p) => p.locale === 'enUS' && !pages.find((i) => i.key === p.key)
      ) || [])
    );
    return pages.map((p) => ({
      label: renderLink(() => p.title || p.key, { name: 'info', params: { p: p.key } }),
      key: `page_${p.key}`,
      icon: renderIcon(InfoIcon, !showIcons),
    }));
  });

  const menuOptions = computed<MenuOption[]>(() => [
    {
      label: renderLink(() => $t('nav.browse'), {
        name: 'browse',
        params: { text: state.text?.slug },
        query: { lvl: browse.level, pos: browse.position },
      }),
      key: 'browse',
      icon: renderIcon(BookIcon, !showIcons),
    },
    {
      label: renderLink(() => $t('nav.search'), {
        name: 'search',
        params: { text: state.text?.slug },
      }),
      key: 'search',
      icon: renderIcon(SearchIcon, !showIcons),
    },
    ...(infoPagesOptions.value.length
      ? [
          {
            label: () =>
              pickTranslation(pfData.value?.settings.navInfoEntry, state.locale) || $t('nav.info'),
            key: 'info',
            children: infoPagesOptions.value,
          },
        ]
      : []),
  ]);

  return {
    menuOptions,
  };
}

export function useAccountMenuOptions(showIcons: boolean = true) {
  const menuOptions: MenuOption[] = [
    {
      label: renderLink(() => $t('account.profile'), { name: 'accountProfile' }),
      key: 'accountProfile',
      icon: renderIcon(EyeIcon, !showIcons),
    },
    {
      label: renderLink(() => $t('account.account'), { name: 'accountManage' }),
      key: 'accountManage',
      icon: renderIcon(ManageAccountIcon, !showIcons),
    },
  ];

  return {
    menuOptions,
  };
}

export function useAdminMenuOptions(showIcons: boolean = true) {
  const state = useStateStore();

  const menuOptions = computed<MenuOption[]>(() => [
    {
      label: renderLink(() => $t('admin.statistics.heading'), { name: 'adminStatistics' }),
      key: 'adminStatistics',
      icon: renderIcon(BarChartIcon, !showIcons),
    },
    {
      label: $t('admin.text.heading'),
      key: 'adminText',
      icon: renderIcon(TextsIcon, !showIcons),
      children: [
        {
          label: renderLink(() => $t('admin.text.general.heading'), {
            name: 'adminTextsGeneral',
            params: { text: state.text?.slug },
          }),
          key: 'adminTextsGeneral',
        },
        {
          label: renderLink(() => $t('admin.text.levels.heading'), {
            name: 'adminTextsLevels',
            params: { text: state.text?.slug },
          }),
          key: 'adminTextsLevels',
        },
        {
          label: renderLink(() => $t('admin.text.locations.heading'), {
            name: 'adminTextsLocations',
            params: { text: state.text?.slug },
          }),
          key: 'adminTextsLocations',
        },
      ],
    },
    {
      label: renderLink(() => $t('admin.newText.heading'), { name: 'adminNewText' }),
      key: 'adminNewText',
      icon: renderIcon(AddCircleIcon, !showIcons),
    },
    {
      label: $t('admin.system.heading'),
      key: 'adminSystem',
      icon: renderIcon(SettingsIcon, !showIcons),
      children: [
        {
          label: renderLink(() => $t('admin.system.platformSettings.heading'), {
            name: 'adminSystemSettings',
          }),
          key: 'adminSystemSettings',
        },
        {
          label: renderLink(() => $t('admin.system.infoPages.heading'), {
            name: 'adminSystemInfoPages',
          }),
          key: 'adminSystemInfoPages',
        },
        {
          label: renderLink(() => $t('admin.system.segments.heading'), {
            name: 'adminSystemSegments',
          }),
          key: 'adminSystemSegments',
        },
        {
          label: renderLink(() => $t('admin.users.heading'), { name: 'adminSystemUsers' }),
          key: 'adminSystemUsers',
        },
      ],
    },
  ]);

  return {
    menuOptions,
  };
}

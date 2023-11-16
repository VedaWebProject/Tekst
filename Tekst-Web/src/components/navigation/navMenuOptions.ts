import { NIcon, type MenuOption } from 'naive-ui';
import { h, type Component, computed } from 'vue';
import { RouterLink, type RouteLocationRaw } from 'vue-router';
import { $t } from '@/i18n';

import RemoveRedEyeRound from '@vicons/material/RemoveRedEyeRound';
import ManageAccountsRound from '@vicons/material/ManageAccountsRound';

import LibraryBooksOutlined from '@vicons/material/LibraryBooksOutlined';
import BarChartRound from '@vicons/material/BarChartRound';
import AddCircleOutlineRound from '@vicons/material/AddCircleOutlineRound';
import SettingsApplicationsOutlined from '@vicons/material/SettingsApplicationsOutlined';
import { useStateStore } from '@/stores';
import { usePlatformData } from '@/platformData';
import type { ClientSegmentHead } from '@/api';

function renderIcon(icon: Component, props?: Record<string, unknown>) {
  return () => h(NIcon, props, { default: () => h(icon) });
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
        to,
        style: {
          fontSize: 'var(--app-ui-font-size)',
        },
        ...props,
      },
      { default: label }
    );
}

export function useMainMenuOptions() {
  const { pfData } = usePlatformData();
  const state = useStateStore();

  const pagesOptions = computed(() => {
    const pages: ClientSegmentHead[] = [];
    // add pages with current locale
    pages.push(...(pfData.value?.pagesInfo.filter((p) => p.locale === state.locale) || []));
    // add pages without locale
    pages.push(
      ...(pfData.value?.pagesInfo.filter((p) => !p.locale && !pages.find((i) => i.key === p.key)) ||
        [])
    );
    // add pages with enUS locale (fallback)
    pages.push(
      ...(pfData.value?.pagesInfo.filter(
        (p) => p.locale === 'enUS' && !pages.find((i) => i.key === p.key)
      ) || [])
    );
    return pages.map((p) => ({
      label: renderLink(() => p.title || p.key, { name: 'page', query: { p: p.key } }),
      key: `page_${p.key}`,
    }));
  });

  const menuOptions = computed<MenuOption[]>(() => [
    {
      label: renderLink(() => $t('nav.browse'), {
        name: 'browse',
        params: { text: state.text?.slug },
      }),
      key: 'browse',
    },
    {
      label: renderLink(() => $t('nav.search'), {
        name: 'search',
        params: { text: state.text?.slug },
      }),
      key: 'search',
    },
    ...(pagesOptions.value.length
      ? [
          {
            label: () => $t('nav.more'),
            key: 'page',
            children: pagesOptions.value,
          },
        ]
      : []),
  ]);

  return {
    menuOptions,
  };
}

export function useAccountMenuOptions() {
  const menuOptions: MenuOption[] = [
    {
      label: renderLink(() => $t('account.profile'), { name: 'accountProfile' }),
      key: 'accountProfile',
      icon: renderIcon(RemoveRedEyeRound),
    },
    {
      label: renderLink(() => $t('account.account'), { name: 'accountManage' }),
      key: 'accountManage',
      icon: renderIcon(ManageAccountsRound),
    },
  ];

  return {
    menuOptions,
  };
}

export function useAdminMenuOptions() {
  const state = useStateStore();

  const menuOptions = computed<MenuOption[]>(() => [
    {
      label: renderLink(() => $t('admin.statistics.heading'), { name: 'adminStatistics' }),
      key: 'adminStatistics',
      icon: renderIcon(BarChartRound),
    },
    {
      label: $t('admin.text.heading'),
      key: 'adminText',
      icon: renderIcon(LibraryBooksOutlined),
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
          label: renderLink(() => $t('admin.text.nodes.heading'), {
            name: 'adminTextsNodes',
            params: { text: state.text?.slug },
          }),
          key: 'adminTextsNodes',
        },
      ],
    },
    {
      label: renderLink(() => $t('admin.newText.heading'), { name: 'adminNewText' }),
      key: 'adminNewText',
      icon: renderIcon(AddCircleOutlineRound),
    },
    {
      label: $t('admin.system.heading'),
      key: 'adminSystem',
      icon: renderIcon(SettingsApplicationsOutlined),
      children: [
        {
          label: renderLink(() => $t('admin.system.platformSettings.heading'), {
            name: 'adminSystemSettings',
          }),
          key: 'adminSystemSettings',
        },
        {
          label: renderLink(() => $t('admin.system.pages.heading'), { name: 'adminSystemPages' }),
          key: 'adminSystemPages',
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

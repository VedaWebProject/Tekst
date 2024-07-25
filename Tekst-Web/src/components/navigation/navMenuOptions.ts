import { NBadge, type MenuOption } from 'naive-ui';
import { h, computed } from 'vue';
import { RouterLink, type RouteLocationRaw } from 'vue-router';
import { $t } from '@/i18n';
import {
  useAuthStore,
  useBrowseStore,
  useResourcesStore,
  useStateStore,
  useUserMessagesStore,
} from '@/stores';
import { usePlatformData } from '@/composables/platformData';
import type { ClientSegmentHead } from '@/api';
import { pickTranslation, renderIcon } from '@/utils';

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
  MaintenanceIcon,
  SystemIcon,
  SegmentsIcon,
  UsersIcon,
  LevelsIcon,
  TreeIcon,
  MessageIcon,
  CommunityIcon,
  ResourceIcon,
  LogOutIcon,
} from '@/icons';

function renderLink(label: unknown, to: RouteLocationRaw, props?: Record<string, unknown>) {
  return () =>
    h(
      RouterLink,
      {
        ...props,
        to,
        style: {
          fontSize: 'var(--font-size)',
        },
      },
      { default: label }
    );
}

export function useMainMenuOptions(showIcons: boolean = true) {
  const { pfData } = usePlatformData();
  const state = useStateStore();
  const auth = useAuthStore();
  const browse = useBrowseStore();
  const resources = useResourcesStore();

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
      icon: (showIcons && renderIcon(InfoIcon)) || undefined,
    }));
  });

  const menuOptions = computed<MenuOption[]>(() => [
    {
      label: renderLink(
        () =>
          pickTranslation(pfData.value?.settings.navBrowseEntry, state.locale) || $t('nav.browse'),
        {
          name: 'browse',
          params: { text: state.text?.slug },
          query: { lvl: browse.level, pos: browse.position },
        }
      ),
      key: 'browse',
      icon: (showIcons && renderIcon(BookIcon)) || undefined,
    },
    {
      label: renderLink(
        () =>
          pickTranslation(pfData.value?.settings.navSearchEntry, state.locale) || $t('nav.search'),
        {
          name: 'search',
          params: { text: state.text?.slug },
        }
      ),
      key: 'search',
      icon: (showIcons && renderIcon(SearchIcon)) || undefined,
    },
    ...(state.smallScreen && auth.loggedIn
      ? [
          {
            label: renderLink(
              () =>
                h('div', null, [
                  $t('resources.heading'),
                  h(
                    NBadge,
                    { dot: true, offset: [4, -10], show: !!resources.correctionsCountTotal },
                    undefined
                  ),
                ]),
              {
                name: 'resources',
                params: {
                  text: state.text?.slug || '',
                },
              }
            ),
            key: 'resources',
            icon: (showIcons && renderIcon(ResourceIcon)) || undefined,
          },
          {
            label: renderLink(() => $t('community.heading'), {
              name: 'community',
            }),
            key: 'community',
            icon: (showIcons && renderIcon(CommunityIcon)) || undefined,
          },
        ]
      : []),
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
  const state = useStateStore();
  const userMessages = useUserMessagesStore();
  const menuOptions: MenuOption[] = [
    {
      label: renderLink(() => $t('account.profile'), { name: 'accountProfile' }),
      key: 'accountProfile',
      icon: (showIcons && renderIcon(EyeIcon)) || undefined,
    },
    {
      label: renderLink(() => $t('account.account'), { name: 'accountSettings' }),
      key: 'accountSettings',
      icon: (showIcons && renderIcon(ManageAccountIcon)) || undefined,
    },
    {
      label: renderLink(
        () =>
          h('div', null, [
            $t('account.messages.heading'),
            h(NBadge, { dot: true, offset: [4, -10], show: !!userMessages.unreadCount }, undefined),
          ]),
        {
          name: 'accountMessages',
        }
      ),
      key: 'accountMessages',
      icon: (showIcons && renderIcon(MessageIcon)) || undefined,
    },
    ...(state.smallScreen
      ? [
          {
            label: renderLink(() => $t('account.logoutBtn'), { name: 'logout' }),
            key: 'logout',
            icon: (showIcons && renderIcon(LogOutIcon)) || undefined,
          },
        ]
      : []),
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
      icon: (showIcons && renderIcon(BarChartIcon)) || undefined,
    },
    {
      label: $t('admin.text.heading'),
      key: 'adminText',
      icon: (showIcons && renderIcon(TextsIcon)) || undefined,
      children: [
        {
          key: 'currentTextGroup',
          type: 'group',
          label: state.text?.title || '',
          children: [
            {
              label: renderLink(() => $t('admin.text.settings.heading'), {
                name: 'adminTextsSettings',
                params: { text: state.text?.slug },
              }),
              key: 'adminTextsSettings',
              icon: (showIcons && renderIcon(SettingsIcon)) || undefined,
            },
            {
              label: renderLink(() => $t('admin.text.levels.heading'), {
                name: 'adminTextsLevels',
                params: { text: state.text?.slug },
              }),
              key: 'adminTextsLevels',
              icon: (showIcons && renderIcon(LevelsIcon)) || undefined,
            },
            {
              label: renderLink(() => $t('admin.text.locations.heading'), {
                name: 'adminTextsLocations',
                params: { text: state.text?.slug },
              }),
              key: 'adminTextsLocations',
              icon: (showIcons && renderIcon(TreeIcon)) || undefined,
            },
          ],
        },
        {
          key: 'textGeneralGroup',
          type: 'group',
          label: $t('general.general'),
          children: [
            {
              label: renderLink(() => $t('admin.newText.heading'), { name: 'adminNewText' }),
              key: 'adminNewText',
              icon: (showIcons && renderIcon(AddCircleIcon)) || undefined,
            },
          ],
        },
      ],
    },
    {
      label: $t('admin.system.heading'),
      key: 'adminSystem',
      icon: (showIcons && renderIcon(SystemIcon)) || undefined,
      children: [
        {
          label: renderLink(() => $t('admin.system.platformSettings.heading'), {
            name: 'adminSystemSettings',
          }),
          key: 'adminSystemSettings',
          icon: (showIcons && renderIcon(SettingsIcon)) || undefined,
        },
        {
          label: renderLink(() => $t('admin.system.infoPages.heading'), {
            name: 'adminSystemInfoPages',
          }),
          key: 'adminSystemInfoPages',
          icon: (showIcons && renderIcon(InfoIcon)) || undefined,
        },
        {
          label: renderLink(() => $t('admin.system.segments.heading'), {
            name: 'adminSystemSegments',
          }),
          key: 'adminSystemSegments',
          icon: (showIcons && renderIcon(SegmentsIcon)) || undefined,
        },
        {
          label: renderLink(() => $t('admin.users.heading'), { name: 'adminSystemUsers' }),
          key: 'adminSystemUsers',
          icon: (showIcons && renderIcon(UsersIcon)) || undefined,
        },
        {
          label: renderLink(() => $t('admin.system.maintenance.heading'), {
            name: 'adminSystemMaintenance',
          }),
          key: 'adminSystemMaintenance',
          icon: (showIcons && renderIcon(MaintenanceIcon)) || undefined,
        },
      ],
    },
  ]);

  return {
    menuOptions,
  };
}

import type { ClientSegmentHead } from '@/api';
import { $t } from '@/i18n';
import {
  useAuthStore,
  useBrowseStore,
  useResourcesStore,
  useStateStore,
  useUserMessagesStore,
} from '@/stores';
import { pickTranslation, renderIcon } from '@/utils';
import { NBadge, type MenuOption } from 'naive-ui';
import { computed, h } from 'vue';
import { RouterLink, type RouteLocationRaw } from 'vue-router';

import {
  BookIcon,
  CommunityIcon,
  EyeIcon,
  InfoIcon,
  LogoutIcon,
  MaintenanceIcon,
  ManageAccountIcon,
  MessageIcon,
  ResourceIcon,
  SearchIcon,
  SegmentsIcon,
  SettingsIcon,
  TextsIcon,
  UsersIcon,
} from '@/icons';

function renderLink(label: unknown, to: RouteLocationRaw, props?: Record<string, unknown>) {
  return () =>
    h(
      RouterLink,
      {
        ...props,
        to,
      },
      { default: label }
    );
}

export function useMainMenuOptions(showIcons: boolean = true) {
  const state = useStateStore();
  const auth = useAuthStore();
  const browse = useBrowseStore();
  const resources = useResourcesStore();

  const infoPagesOptions = computed(() => {
    const pages: ClientSegmentHead[] = [];
    // add pages with current locale
    pages.push(...(state.pf?.infoSegments.filter((p) => p.locale === state.locale) || []));
    // add pages without locale
    pages.push(
      ...(state.pf?.infoSegments.filter(
        (p) => p.locale === '*' && !pages.find((i) => i.key === p.key)
      ) || [])
    );
    // add pages with enUS locale (fallback)
    pages.push(
      ...(state.pf?.infoSegments.filter(
        (p) => p.locale === 'enUS' && !pages.find((i) => i.key === p.key)
      ) || [])
    );
    return pages.map((p) => ({
      label: renderLink(() => p.title || p.key, { name: 'info', params: { pageKey: p.key } }),
      key: `page_${p.key}`,
      icon: (showIcons && state.smallScreen && renderIcon(InfoIcon)) || undefined,
    }));
  });

  const menuOptions = computed<MenuOption[]>(() => [
    {
      label: renderLink(
        () => pickTranslation(state.pf?.state.navBrowseEntry, state.locale) || $t('nav.browse'),
        {
          name: 'browse',
          params: { textSlug: state.text?.slug, locId: browse.locationPathHead?.id },
        }
      ),
      key: 'browse',
      icon: (showIcons && renderIcon(BookIcon)) || undefined,
    },
    {
      label: renderLink(
        () => pickTranslation(state.pf?.state.navSearchEntry, state.locale) || $t('nav.search'),
        {
          name: 'search',
          params: { textSlug: state.text?.slug },
        }
      ),
      key: 'search',
      icon: (showIcons && renderIcon(SearchIcon)) || undefined,
    },
    ...(auth.loggedIn
      ? [
          {
            label: renderLink(() => $t('community.heading'), {
              name: 'community',
            }),
            key: 'community',
            icon: (showIcons && renderIcon(CommunityIcon)) || undefined,
          },
        ]
      : []),
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
                  textSlug: state.text?.slug || '',
                },
              }
            ),
            key: 'resources',
            icon: (showIcons && renderIcon(ResourceIcon)) || undefined,
          },
        ]
      : []),
    ...(state.smallScreen && !!auth.user?.isSuperuser
      ? [
          {
            label: renderLink(() => $t('texts.heading'), {
              name: 'textSettings',
              params: {
                textSlug: state.text?.slug || '',
              },
            }),
            key: 'textSettings',
            icon: (showIcons && renderIcon(TextsIcon)) || undefined,
          },
        ]
      : []),
    ...(infoPagesOptions.value.length
      ? [
          {
            label: () =>
              pickTranslation(state.pf?.state.navInfoEntry, state.locale) || $t('nav.info'),
            key: 'info',
            children: infoPagesOptions.value,
            icon: (showIcons && renderIcon(InfoIcon)) || undefined,
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
            key: 'logoutDivider',
            type: 'divider',
          },
          {
            label: renderLink(() => $t('account.logoutBtn'), { name: 'logout' }),
            key: 'logout',
            icon: (showIcons && renderIcon(LogoutIcon)) || undefined,
          },
        ]
      : []),
  ];

  return {
    menuOptions,
  };
}

export function useAdminMenuOptions(showIcons: boolean = true) {
  const menuOptions = computed<MenuOption[]>(() => [
    {
      label: renderLink(() => $t('general.settings'), {
        name: 'adminSettings',
      }),
      key: 'adminSettings',
      icon: (showIcons && renderIcon(SettingsIcon)) || undefined,
    },
    {
      label: renderLink(() => $t('admin.infoPages.heading'), {
        name: 'adminInfoPages',
      }),
      key: 'adminInfoPages',
      icon: (showIcons && renderIcon(InfoIcon)) || undefined,
    },
    {
      label: renderLink(() => $t('admin.segments.heading'), {
        name: 'adminSegments',
      }),
      key: 'adminSegments',
      icon: (showIcons && renderIcon(SegmentsIcon)) || undefined,
    },
    {
      label: renderLink(() => $t('admin.users.heading'), { name: 'adminUsers' }),
      key: 'adminUsers',
      icon: (showIcons && renderIcon(UsersIcon)) || undefined,
    },
    {
      label: renderLink(() => $t('admin.maintenance.heading'), {
        name: 'adminMaintenance',
      }),
      key: 'adminMaintenance',
      icon: (showIcons && renderIcon(MaintenanceIcon)) || undefined,
    },
  ]);

  return {
    menuOptions,
  };
}

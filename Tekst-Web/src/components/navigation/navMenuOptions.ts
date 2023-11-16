import { NIcon, type MenuOption } from 'naive-ui';
import { h, type Component } from 'vue';
import { RouterLink } from 'vue-router';
import { $t } from '@/i18n';
import { useStateStore } from '@/stores';

import RemoveRedEyeRound from '@vicons/material/RemoveRedEyeRound';
import ManageAccountsRound from '@vicons/material/ManageAccountsRound';

import LibraryBooksOutlined from '@vicons/material/LibraryBooksOutlined';
import BarChartRound from '@vicons/material/BarChartRound';
import AddCircleOutlineRound from '@vicons/material/AddCircleOutlineRound';
import SettingsApplicationsOutlined from '@vicons/material/SettingsApplicationsOutlined';

const state = useStateStore();

function renderIcon(icon: Component, props?: Record<string, unknown>) {
  return () => h(NIcon, props, { default: () => h(icon) });
}

export const accountMenuOptions: MenuOption[] = [
  {
    label: () =>
      h(
        RouterLink,
        {
          to: { name: 'accountProfile' },
        },
        { default: () => $t('account.profile') }
      ),
    key: 'accountProfile',
    icon: renderIcon(RemoveRedEyeRound),
  },
  {
    label: () =>
      h(
        RouterLink,
        {
          to: { name: 'accountManage' },
        },
        { default: () => $t('account.account') }
      ),
    key: 'accountManage',
    icon: renderIcon(ManageAccountsRound),
  },
];

export const adminMenuOptions: MenuOption[] = [
  {
    label: () =>
      h(
        RouterLink,
        {
          to: { name: 'adminStatistics' },
        },
        { default: () => $t('admin.statistics.heading') }
      ),
    key: 'adminStatistics',
    icon: renderIcon(BarChartRound),
  },
  {
    label: $t('admin.text.heading'),
    key: 'adminText',
    icon: renderIcon(LibraryBooksOutlined),
    children: [
      {
        label: () =>
          h(
            RouterLink,
            {
              to: { name: 'adminTextsGeneral', params: { text: state.text?.slug } },
            },
            { default: () => $t('admin.text.general.heading') }
          ),
        key: 'adminTextsGeneral',
      },
      {
        label: () =>
          h(
            RouterLink,
            {
              to: { name: 'adminTextsLevels', params: { text: state.text?.slug } },
            },
            { default: () => $t('admin.text.levels.heading') }
          ),
        key: 'adminTextsLevels',
      },
      {
        label: () =>
          h(
            RouterLink,
            {
              to: { name: 'adminTextsNodes', params: { text: state.text?.slug } },
            },
            { default: () => $t('admin.text.nodes.heading') }
          ),
        key: 'adminTextsNodes',
      },
    ],
  },
  {
    label: () =>
      h(
        RouterLink,
        {
          to: { name: 'adminNewText' },
        },
        { default: () => $t('admin.newText.heading') }
      ),
    key: 'adminNewText',
    icon: renderIcon(AddCircleOutlineRound),
  },
  {
    label: $t('admin.system.heading'),
    key: 'adminSystem',
    icon: renderIcon(SettingsApplicationsOutlined),
    children: [
      {
        label: () =>
          h(
            RouterLink,
            {
              to: { name: 'adminSystemSettings' },
            },
            { default: () => $t('admin.system.platformSettings.heading') }
          ),
        key: 'adminSystemSettings',
      },
      {
        label: () =>
          h(
            RouterLink,
            {
              to: { name: 'adminSystemPages' },
            },
            { default: () => $t('admin.system.pages.heading') }
          ),
        key: 'adminSystemPages',
      },
      {
        label: () =>
          h(
            RouterLink,
            {
              to: { name: 'adminSystemSegments' },
            },
            { default: () => $t('admin.system.segments.heading') }
          ),
        key: 'adminSystemSegments',
      },
      {
        label: () =>
          h(
            RouterLink,
            {
              to: { name: 'adminSystemUsers' },
            },
            { default: () => $t('admin.users.heading') }
          ),
        key: 'adminSystemUsers',
      },
    ],
  },
];

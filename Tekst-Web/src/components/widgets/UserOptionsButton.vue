<script setup lang="ts">
import { ref, computed, h, type Component } from 'vue';
import { useAuthStore, useStateStore } from '@/stores';
import { useRouter } from 'vue-router';
import { NButton, NIcon, NDropdown } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import { useTheme } from '@/theme';

import LogInRound from '@vicons/material/LogInRound';
import LogOutRound from '@vicons/material/LogOutRound';
import PersonRound from '@vicons/material/PersonRound';
import RemoveRedEyeRound from '@vicons/material/RemoveRedEyeRound';
import ManageAccountsRound from '@vicons/material/ManageAccountsRound';
import PeopleRound from '@vicons/material/PeopleRound';
import BarChartRound from '@vicons/material/BarChartRound';
import MenuBookOutlined from '@vicons/material/MenuBookOutlined';
import AddCircleOutlineRound from '@vicons/material/AddCircleOutlineRound';

const { t } = useI18n({ useScope: 'global' });
const auth = useAuthStore();
const state = useStateStore();
const { accentColors } = useTheme();
const router = useRouter();

const tooltip = computed(() =>
  auth.loggedIn
    ? t('account.tipUserBtn', { username: auth.user?.username })
    : t('account.tipLoginBtn')
);

const showUserDropdown = ref(false);

const userOptions = computed(() => [
  {
    type: 'group',
    label: `${auth.user?.firstName} ${auth.user?.lastName} (${auth.user?.username})`,
    key: 'user',
    children: [
      {
        label: t('account.profile'),
        key: 'accountProfile',
        icon: renderIcon(RemoveRedEyeRound),
      },
      {
        label: t('account.manage.heading'),
        key: 'accountManage',
        icon: renderIcon(ManageAccountsRound),
      },
    ],
  },
  ...(auth.user?.isSuperuser
    ? [
        {
          type: 'divider',
          key: 'dividerAdministration',
        },
        {
          type: 'group',
          label: t('admin.optionGroupLabel'),
          key: 'admin',
          children: [
            {
              label: t('admin.statistics.heading'),
              key: 'adminStatistics',
              icon: renderIcon(BarChartRound),
            },
            {
              label: t('admin.users.heading'),
              key: 'adminUsers',
              icon: renderIcon(PeopleRound),
            },
            {
              label: t('admin.texts.heading'),
              key: 'adminTexts',
              icon: renderIcon(MenuBookOutlined),
            },
            {
              label: t('admin.newText.heading'),
              key: 'adminNewText',
              icon: renderIcon(AddCircleOutlineRound),
            },
          ],
        },
      ]
    : []),
  {
    type: 'divider',
    key: 'dividerLogout',
  },
  {
    label: t('account.logoutBtn'),
    key: 'logout',
    icon: renderIcon(LogOutRound),
  },
]);

const color = computed(() => (auth.loggedIn ? accentColors.value.base : undefined));

function renderIcon(icon: Component) {
  return () => h(NIcon, null, { default: () => h(icon) });
}

async function handleClick() {
  if (!auth.loggedIn) {
    auth.showLoginModal(undefined, { name: 'accountProfile' });
  } else if (!showUserDropdown.value) {
    showUserDropdown.value = true;
  }
}

function handleUserOptionSelect(key: string) {
  showUserDropdown.value = false;
  if (key === 'logout') {
    auth.logout();
  } else if (key === 'adminTexts') {
    router.push({
      name: 'adminTexts',
      params: { text: state.text?.slug },
    });
  } else {
    router.push({
      name: key,
    });
  }
}
</script>

<template>
  <n-dropdown
    :show="showUserDropdown"
    :options="userOptions"
    :on-clickoutside="() => (showUserDropdown = false)"
    :size="state.dropdownSize"
    @select="handleUserOptionSelect"
    show-arrow
  >
    <n-button
      :secondary="!auth.loggedIn"
      circle
      size="large"
      @click="handleClick"
      :title="tooltip"
      :focusable="false"
      :color="color"
      :style="auth.loggedIn && 'color: #fff'"
      class="user-options-button"
    >
      <template #icon>
        <n-icon v-if="auth.loggedIn" :component="PersonRound" />
        <n-icon v-else :component="LogInRound" />
      </template>
    </n-button>
  </n-dropdown>
</template>

<style scoped>
.user-options-button {
  font-size: var(--app-ui-font-size-mini) !important;
  font-weight: var(--app-ui-font-weight-normal) !important;
}
</style>

<style scoped>
.user-options-button {
  font-size: var(--app-ui-font-size-mini) !important;
  font-weight: var(--app-ui-font-weight-normal) !important;
}
</style>

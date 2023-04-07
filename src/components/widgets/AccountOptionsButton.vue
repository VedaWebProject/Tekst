<script setup lang="ts">
import { ref, computed, h, type Component } from 'vue';
import { useAuthStore, useStateStore } from '@/stores';
import { useRouter } from 'vue-router';
import { NButton, NIcon, NDropdown } from 'naive-ui';
import LogInRound from '@vicons/material/LogInRound';
import LogOutRound from '@vicons/material/LogOutRound';
import ManageAccountsRound from '@vicons/material/ManageAccountsRound';
import { useI18n } from 'vue-i18n';

const { t } = useI18n({ useScope: 'global' });
const auth = useAuthStore();
const state = useStateStore();
const router = useRouter();
const tooltip = computed(() =>
  auth.loggedIn ? t('account.tipAccountBtn') : t('login.tipLoginBtn')
);

const showAccountDropdown = ref(false);

const accountOptions = computed(() => [
  {
    label: t('account.manage'),
    key: 'manage',
    icon: renderIcon(ManageAccountsRound),
  },
  {
    label: t('login.logout'),
    key: 'logout',
    icon: renderIcon(LogOutRound),
  },
]);

const initials = computed(
  () =>
    auth.loggedIn &&
    auth.user &&
    `${auth.user.firstName[0].toUpperCase()}${auth.user.lastName[0].toUpperCase()}`
);

const color = computed(() => (auth.loggedIn && auth.user ? state.accentColors.fade2 : undefined));

function renderIcon(icon: Component) {
  return () => h(NIcon, null, { default: () => h(icon) });
}

function handleClick() {
  if (!auth.loggedIn) {
    router.push({ name: 'login' });
  } else {
    showAccountDropdown.value = !showAccountDropdown.value;
  }
}

function handleAccountOptionSelect(option: string) {
  showAccountDropdown.value = false;
  switch (option) {
    case 'manage':
      router.push({ name: 'account' });
      break;
    case 'logout':
      auth.logout();
      break;
  }
}
</script>

<template>
  <n-dropdown
    :show="showAccountDropdown"
    :options="accountOptions"
    :on-clickoutside="() => (showAccountDropdown = false)"
    :size="state.dropdownSize"
    @select="handleAccountOptionSelect"
  >
    <n-button
      :secondary="!auth.loggedIn || !auth.user"
      circle
      size="large"
      @click="handleClick"
      :title="tooltip"
      :focusable="false"
      :color="color"
      class="account-options-button"
    >
      <template v-if="auth.loggedIn && auth.user">{{ initials }}</template>
      <template v-if="!auth.loggedIn || !auth.user" #icon>
        <n-icon :component="LogInRound" />
      </template>
      <!-- {{ label }} -->
    </n-button>
  </n-dropdown>
</template>

<style scoped>
.account-options-button {
  font-size: var(--app-ui-font-size-mini) !important;
  font-weight: var(--app-ui-font-weight-normal) !important;
}
</style>

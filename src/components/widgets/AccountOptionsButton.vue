<script setup lang="ts">
import { ref, computed, h, type Component } from 'vue';
import { useAuthStore, useStateStore } from '@/stores';
import { useRouter } from 'vue-router';
import { NButton, NIcon, NDropdown } from 'naive-ui';
import LogInRound from '@vicons/material/LogInRound';
import LogOutRound from '@vicons/material/LogOutRound';
import AccountCircleRound from '@vicons/material/AccountCircleRound';
import ManageAccountsRound from '@vicons/material/ManageAccountsRound';
import { useI18n } from 'vue-i18n';

const { t } = useI18n({ useScope: 'global' });
const auth = useAuthStore();
const state = useStateStore();
const router = useRouter();
const icon = computed(() => (auth.loggedIn ? AccountCircleRound : LogInRound));
// const label = computed(() => (auth.loggedIn ? t('login.logout') : t('login.login')));
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
      secondary
      circle
      size="large"
      @click="handleClick"
      :title="tooltip"
      :focusable="false"
    >
      <template #icon>
        <n-icon :component="icon" />
      </template>
      <!-- {{ label }} -->
    </n-button>
  </n-dropdown>
</template>

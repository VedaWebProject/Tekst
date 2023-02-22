<script setup lang="ts">
import { computed } from 'vue';
import { useAuthStore } from '@/stores';
import router from '@/router';
import { NButton, NIcon } from 'naive-ui';
import LogInRound from '@vicons/material/LogInRound';
import LogOutRound from '@vicons/material/LogOutRound';
import { i18n } from '@/i18n';

const t = i18n.global.t;
const auth = useAuthStore();
const icon = computed(() => (auth.loggedIn ? LogOutRound : LogInRound));
const label = computed(() => (auth.loggedIn ? t('login.logout') : t('login.login')));
const tooltip = computed(() => (auth.loggedIn ? t('login.tipLogoutBtn') : t('login.tipLoginBtn')));

function handleClick() {
  if (!auth.loggedIn) {
    router.push('/login');
  } else {
    auth.logout();
  }
}
</script>

<template>
  <n-button @click="handleClick" :title="tooltip" :focusable="false">
    <template #icon>
      <n-icon :component="icon" />
    </template>
    {{ label }}
  </n-button>
</template>

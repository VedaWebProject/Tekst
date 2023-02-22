<script setup lang="ts">
import LanguageSwitcher from '@/components/LanguageSwitcher.vue';
import ThemeModeSwitcher from '@/components/ThemeModeSwitcher.vue';
import MainNavigation from '@/components/MainNavigation.vue';
import LoginLogoutButton from '@/components/LoginLogoutButton.vue';
import { NSpace } from 'naive-ui';
import { usePlatformStore } from '@/stores';

const pf = usePlatformStore();
</script>

<template>
  <header>
    <img id="header-logo" :alt="`${pf.get('general.title')} Logo`" src="@/assets/logo.png" />
    <div>
      <div id="page-title">{{ pf.get('general.title') }}</div>
      <div>{{ $t('general.welcomeTest') }}</div>
      <MainNavigation />
    </div>
    <div id="header-branding-extra">
      <n-space inline :wrap-item="false" size="small">
        <ThemeModeSwitcher size="large" />
        <LanguageSwitcher size="large" />
        <LoginLogoutButton />
      </n-space>
    </div>
  </header>
</template>

<style scoped>
header {
  display: flex;
  align-items: stretch;
  justify-content: start;
  border-bottom: 3px solid var(--accent-color);
  padding: 0.8em;
  padding-bottom: 0;
}

header #header-logo {
  align-self: center;
  height: 86px;
  width: auto;
  margin-right: 1rem;
}

#header-branding-extra {
  flex-grow: 1;
  text-align: right;
}
</style>

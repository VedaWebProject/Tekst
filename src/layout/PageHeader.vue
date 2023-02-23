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
    <img id="header-logo" :alt="`${pf.get('info.platform_name')} Logo`" src="@/assets/logo.png" />
    <div id="page-title">{{ pf.get('info.platform_name') }}</div>
    <MainNavigation />
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
  align-items: center;
  justify-content: start;
  border-bottom: 3px solid var(--accent-color);
  padding: 0.5rem;
}

header #header-logo {
  align-self: center;
  height: 56px;
  width: auto;
  margin-right: 1rem;
}

header #page-title {
  font-size: 1.2rem;
  margin-right: 1rem;
}

#header-branding-extra {
  flex-grow: 1;
  text-align: right;
}
</style>

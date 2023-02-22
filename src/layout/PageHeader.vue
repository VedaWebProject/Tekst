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
    <div id="header-branding-container">
      <img :alt="pf.get('general.title') + ' Logo'" class="logo" src="@/assets/logo.png" />
      <div>
        <h1>{{ pf.get('general.title') }}</h1>
        <h2>{{ $t('general.welcomeTest') }}</h2>
      </div>
      <div id="header-branding-extra">
        <n-space inline :wrap-item="false" size="small">
          <ThemeModeSwitcher />
          <LanguageSwitcher />
          <LoginLogoutButton />
        </n-space>
      </div>
    </div>

    <MainNavigation />

    <nav style="display: flex; justify-content: space-around"></nav>
  </header>
</template>

<style scoped>
header {
  border: 1px dashed #bbb;
  border-bottom-color: var(--accent-color);
  border-bottom-width: 5px;
  border-bottom-style: solid;
  padding: 0.8em;
}

#header-branding-container {
  display: flex;
  align-items: stretch;
  justify-content: start;
  height: 100px;
}

#header-branding-container .logo {
  height: 100%;
  width: auto;
  margin-right: 0.8em;
}

#header-branding-extra {
  flex-grow: 1;
  text-align: right;
}
</style>

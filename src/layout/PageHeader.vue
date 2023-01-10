<script setup lang="ts">
import { RouterLink } from 'vue-router';
import LanguageSwitcher from '@/i18n/LanguageSwitcher.vue';
import ThemeModeSwitcher from '@/components/ThemeModeSwitcher.vue';
import { NSpace } from 'naive-ui';
import { useUiDataStore } from '@/stores/uiData';

const ui = useUiDataStore();
</script>

<template>
  <header>
    <div id="header-branding-container">
      <img :alt="ui.data.platform.title + ' Logo'" class="logo" src="@/assets/logo.png" />
      <div>
        <h1>{{ ui.data.platform.title }}</h1>
        <h2>{{ $t('general.welcome') }}</h2>
      </div>
      <div id="header-branding-extra">
        <n-space inline :wrap-item="false" size="small">
          <ThemeModeSwitcher size="small" />
          <LanguageSwitcher size="small" />
        </n-space>
      </div>
    </div>

    <nav>
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/about">About</RouterLink>
    </nav>
  </header>
</template>

<style scoped>
header {
  border: 1px dashed #ff0000;
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

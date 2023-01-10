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
    <h1>{{ ui.data.platform.title }}</h1>
    <h2>{{ ui.data.platform.description }}</h2>
    <img alt="TextRig Logo" class="logo" src="@/assets/logo.png" width="125" height="125" />

    <nav>
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/about">About</RouterLink>
    </nav>

    <h2>{{ $t('foo.welcome') }}</h2>
    <n-space inline :wrap-item="false" size="small">
      <LanguageSwitcher size="small" />
      <ThemeModeSwitcher size="small" />
    </n-space>
  </header>
</template>

<style scoped>
header {
  border: 1px dashed #ff0000;
  padding: 0.8rem;
}
</style>

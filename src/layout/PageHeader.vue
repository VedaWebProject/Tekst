<script setup lang="ts">
import { RouterLink } from 'vue-router';
import LanguageSwitcher from '@/i18n/LanguageSwitcher.vue';
import ThemeModeSwitcher from '@/components/ThemeModeSwitcher.vue';
import { NSpace } from 'naive-ui';
</script>

<template>
  <header>
    <h1>AppTitle</h1>
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
  background-color: #ff0000;
}
</style>

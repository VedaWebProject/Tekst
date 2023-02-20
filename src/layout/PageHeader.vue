<script setup lang="ts">
import { RouterLink } from 'vue-router';
import router from '@/router';
import LanguageSwitcher from '@/components/LanguageSwitcher.vue';
import ThemeModeSwitcher from '@/components/ThemeModeSwitcher.vue';
import { NSpace, NButton } from 'naive-ui';
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
          <ThemeModeSwitcher size="small" />
          <LanguageSwitcher size="small" />
          <n-button @click="() => router.push('/login')" size="small">Login</n-button>
        </n-space>
      </div>
    </div>

    <nav style="display: flex; justify-content: space-around">
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/about">About</RouterLink>
      <RouterLink to="/account">Account</RouterLink>
      <RouterLink to="/admin">Admin</RouterLink>
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

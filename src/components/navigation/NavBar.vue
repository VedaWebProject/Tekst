<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { NButton, NIcon } from 'naive-ui';
import NavBarRouterLink from './NavBarRouterLink.vue';
import ThemeModeSwitcher from '../ThemeModeSwitcher.vue';
import LanguageSwitcher from '../LanguageSwitcher.vue';
import AccountOptionsButton from '../AccountOptionsButton.vue';
import { usePlatformStore, useStateStore } from '@/stores';
import { useRoute } from 'vue-router';

import MenuRound from '@vicons/material/MenuRound';

import InfoOutlined from '@vicons/material/InfoOutlined';
import MenuBookOutlined from '@vicons/material/MenuBookOutlined';
import SearchRound from '@vicons/material/SearchRound';
import HelpOutlineRound from '@vicons/material/HelpOutlineRound';

const pf = usePlatformStore();
const state = useStateStore();
const menuOpen = ref(false);
const menuVisible = computed(() => !state.smallScreen || menuOpen.value);
const dropdownSize = computed(() => (state.smallScreen ? 'huge' : undefined));

const route = useRoute();
watch(route, () => (menuOpen.value = false));
</script>

<template>
  <div class="navbar" :class="state.smallScreen && 'navbar-smallscreen'">
    <img class="navbar-logo" :alt="`${pf.get('info.platformName')} Logo`" src="/logo.png" />
    <div class="navbar-title">{{ pf.get('info.platformName') }}</div>

    <n-button
      v-if="state.smallScreen"
      quaternary
      circle
      size="large"
      :focusable="false"
      :keyboard="false"
      @click="() => (menuOpen = !menuOpen)"
    >
      <template #icon>
        <n-icon size="32">
          <MenuRound />
        </n-icon>
      </template>
    </n-button>

    <div v-show="menuVisible" class="navbar-menu">
      <NavBarRouterLink
        :label="$t('nav.about')"
        route="about"
        :icon="InfoOutlined"
        :show-icon="state.smallScreen"
      />
      <NavBarRouterLink
        :label="$t('nav.browse')"
        route="browse"
        :icon="MenuBookOutlined"
        :show-icon="state.smallScreen"
      />
      <NavBarRouterLink
        :label="$t('nav.search')"
        route="search"
        :icon="SearchRound"
        :show-icon="state.smallScreen"
      />
      <NavBarRouterLink
        :label="$t('nav.help')"
        route="help"
        :icon="HelpOutlineRound"
        :show-icon="state.smallScreen"
      />
      <div class="navbar-menu-divider"></div>
      <div class="navbar-menu-extra">
        <ThemeModeSwitcher />
        <LanguageSwitcher :dropdown-size="dropdownSize" />
        <AccountOptionsButton :dropdown-size="dropdownSize" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex-wrap: wrap;
  max-width: var(--max-app-width);
  margin: 0 auto;
  padding: 0.75rem;
}

.navbar *,
.navbar *::before,
.navbar *::after {
  font-weight: 300;
}

.navbar-smallscreen .navbar {
  padding-bottom: 0px;
}

.navbar-logo {
  align-self: center;
  height: 48px;
  width: auto;
  margin-right: 12px;
}

.navbar-title {
  margin-right: 1.75rem;
  font-size: 1.8rem;
  /* color: var(--accent-color-intense); */
  white-space: nowrap;
}

.navbar-smallscreen .navbar-title {
  flex-grow: 2;
}

.navbar-menu {
  flex-grow: 2;
  display: flex;
  flex-direction: row;
  align-items: center;
}
.navbar-smallscreen .navbar-menu {
  flex-direction: column;
  align-items: stretch;
  flex-basis: 100%;
  padding-top: 0.75rem;
}

.navbar-menu-divider {
  height: 0px;
  flex-grow: 2;
}

.navbar-smallscreen .navbar-menu-divider {
  flex-grow: 1;
  width: 100%;
  margin: 0;
}

.navbar-menu-extra {
  display: flex;
  gap: 12px;
}

.navbar-smallscreen .navbar-menu-extra {
  justify-content: space-around;
  gap: 40px;
  max-width: 320px;
  margin: 24px auto;
}
</style>

<style>
.navbar-smallscreen .navbar-router-link {
  padding: 0.75rem 1.5rem;
  font-size: 22px;
  margin: 6px 0;
  background-color: var(--accent-color-fade4);
  border-radius: 4px;
}

.navbar-smallscreen .navbar-menu-extra {
  font-size: 44px;
}
</style>

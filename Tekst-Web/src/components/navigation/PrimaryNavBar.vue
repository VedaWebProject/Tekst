<script setup lang="ts">
import { ref, watch } from 'vue';
import { NButton, NIcon } from 'naive-ui';
import ThemeModeSwitcher from '@/components/widgets/ThemeModeSwitcher.vue';
import LocaleSwitcher from '@/components/widgets/LocaleSwitcher.vue';
import UserOptionsButton from '@/components/widgets/UserOptionsButton.vue';
import QuickSearchWidget from '@/components/widgets/QuickSearch.vue';
import HelpNavButton from '@/components/widgets/HelpNavButton.vue';
import { useAuthStore, useStateStore } from '@/stores';
import { useRoute, RouterLink } from 'vue-router';
import { usePlatformData } from '@/platformData';
import NavigationMenu from '@/components/navigation/NavigationMenu.vue';
import { useMainMenuOptions } from './navMenuOptions';

import MenuRound from '@vicons/material/MenuRound';

const { pfData, systemHome } = usePlatformData();
const auth = useAuthStore();
const state = useStateStore();
const { menuOptions } = useMainMenuOptions();

const menuOpen = ref(false);

const route = useRoute();

watch(
  () => route.name,
  () => {
    menuOpen.value = false;
  }
);
</script>

<template>
  <div class="navbar" :class="state.smallScreen && 'navbar-smallscreen'">
    <img class="navbar-logo" :alt="`${pfData?.settings.infoPlatformName} Logo`" src="/logo.png" />
    <div class="title-container">
      <RouterLink
        :to="!!systemHome ? { path: '/' } : { name: 'browse' }"
        :title="pfData?.settings.infoDescription"
        class="navbar-title"
      >
        {{ pfData?.settings.infoPlatformName }}
      </RouterLink>
      <div v-if="pfData?.settings.showHeaderInfo" class="navbar-description">
        {{ pfData?.settings.infoDescription }}
      </div>
    </div>

    <div v-if="!state.smallScreen" class="navbar-menu">
      <NavigationMenu :options="menuOptions" />
      <div class="navbar-menu-divider"></div>
      <div class="navbar-menu-extra">
        <QuickSearchWidget />
        <ThemeModeSwitcher />
        <LocaleSwitcher />
        <HelpNavButton />
        <UserOptionsButton v-if="pfData?.security?.closedMode === false || auth.loggedIn" />
      </div>
    </div>

    <div v-if="state.smallScreen" style="flex-grow: 2"></div>
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

    <!-- <div v-show="menuVisible" class="navbar-menu">
      <NavBarRouterLink
        :label="$t('nav.browse')"
        :route="{ name: 'browse', params: { text: textParam } }"
        :show-icon="state.smallScreen"
      />
      <NavBarRouterLink
        :label="$t('nav.search')"
        :route="{ name: 'search', params: { text: textParam } }"
        :show-icon="state.smallScreen"
      />
      <MorePagesDropdown />
      <div class="navbar-menu-divider"></div>
      <div class="navbar-menu-extra">
        <QuickSearchWidget />
        <ThemeModeSwitcher />
        <LocaleSwitcher />
        <HelpNavButton />
        <UserOptionsButton v-if="pfData?.security?.closedMode === false || auth.loggedIn" />
      </div>
    </div> -->
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
  padding: var(--layout-gap);
  font-size: var(--app-ui-font-size-small);
}

.navbar-smallscreen {
  padding: var(--layout-gap);
}

.navbar a:any-link {
  color: var(--n-font-color);
}

.navbar a:hover {
  color: var(--accent-color);
}

.navbar *,
.navbar *::before,
.navbar *::after {
  font-weight: 300;
}

.title-container {
  display: inline-flex;
  flex-direction: column;
  margin-right: var(--layout-gap);
}

.navbar-logo {
  height: 48px;
  width: auto;
  margin-right: var(--content-gap);
}

.navbar-title {
  font-size: var(--app-ui-font-size-huge);
  white-space: nowrap;
  min-width: 120px;
}

.navbar-smallscreen .navbar-title {
  flex-grow: 2;
}

.navbar-description {
  opacity: 1;
  font-size: var(--app-ui-font-size-mini);
  width: 0;
  min-width: 100%;
  line-height: 1.2;
}

.navbar-menu {
  flex-grow: 4;
  display: flex;
  flex-direction: row;
  align-items: center;
}
.navbar-smallscreen .navbar-menu {
  flex-direction: column;
  align-items: stretch;
  flex-basis: 100%;
  padding-top: 0.75rem;
  gap: 0.5rem;
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
  align-items: center;
  gap: 12px;
}

.navbar-smallscreen .navbar-menu-extra {
  justify-content: space-around;
  width: 100%;
  max-width: 320px;
  margin: 0 auto 0 auto;
}
</style>

<style>
.navbar-smallscreen .navbar-router-link {
  padding: 0.5rem 1.5rem;
  background-color: var(--accent-color-fade5);
  border-radius: var(--app-ui-border-radius);
}

.navbar-smallscreen .navbar-more {
  padding: 0.5rem 1.5rem;
}

.navbar-smallscreen .quicksearch-widget {
  flex-grow: 2;
}
</style>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { NFlex, NButton, NIcon } from 'naive-ui';
import ThemeModeSwitcher from '@/components/navigation/ThemeModeSwitcher.vue';
import LocaleSwitcher from '@/components/navigation/LocaleSwitcher.vue';
import UserActionsButton from '@/components/navigation/UserActionsButton.vue';
import QuickSearchWidget from '@/components/navigation/QuickSearch.vue';
import HelpNavButton from '@/components/navigation/HelpNavButton.vue';
import { useAuthStore, useBrowseStore, useStateStore } from '@/stores';
import { RouterLink } from 'vue-router';
import { usePlatformData } from '@/composables/platformData';
import NavigationMenu from '@/components/navigation/NavigationMenu.vue';
import { useMainMenuOptions } from './navMenuOptions';
import DrawerMenu from './DrawerMenu.vue';
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';
import { HamburgerMenuIcon } from '@/icons';
import { useLogo } from '@/composables/logo';

const { pfData, systemHome } = usePlatformData();
const auth = useAuthStore();
const state = useStateStore();
const browse = useBrowseStore();

const { menuOptions: mainMenuOptions } = useMainMenuOptions(false);
const menuOpen = ref(false);
const showUserActionsButton = computed(
  () => pfData.value?.security?.closedMode === false || auth.loggedIn
);

const { pageLogo } = useLogo();
const titleLinkTo = computed(() => {
  if (systemHome.value) {
    return '/';
  } else {
    return {
      name: 'browse',
      params: { text: state.text?.slug },
      query: { lvl: browse.level, pos: browse.position },
    };
  }
});
</script>

<template>
  <n-flex
    align="center"
    :wrap="false"
    class="navbar"
    :class="state.smallScreen && 'navbar-smallscreen'"
  >
    <img class="navbar-logo" alt="" :src="pageLogo" />
    <div class="navbar-title">
      <router-link :to="titleLinkTo">
        <div class="text-gigantic">{{ pfData?.settings.platformName }}</div>
      </router-link>
      <div v-if="pfData?.settings.platformSubtitle?.length" class="translucent text-tiny">
        <translation-display :value="pfData?.settings.platformSubtitle" />
      </div>
    </div>

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
        <n-icon size="32" :component="HamburgerMenuIcon" />
      </template>
    </n-button>
  </n-flex>

  <n-flex v-if="!state.smallScreen" class="navbar-menu">
    <navigation-menu :options="mainMenuOptions" />
    <n-flex justify="end" style="flex-grow: 2">
      <quick-search-widget />
      <theme-mode-switcher />
      <locale-switcher />
      <help-nav-button />
      <user-actions-button v-if="showUserActionsButton" />
    </n-flex>
  </n-flex>

  <drawer-menu
    v-if="state.smallScreen"
    v-model:show="menuOpen"
    :show-user-actions-button="showUserActionsButton"
  />
</template>

<style scoped>
.navbar {
  max-width: var(--max-app-width);
  margin: 0 auto;
  padding: var(--layout-gap);
  font-size: var(--font-size-small);
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

.navbar-logo {
  max-height: 64px;
  width: auto;
}

.navbar-title {
  flex-grow: 2;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.navbar-menu {
  max-width: var(--max-app-width);
  margin: 0 auto var(--content-gap) auto;
  padding: 0 var(--layout-gap);
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
</style>

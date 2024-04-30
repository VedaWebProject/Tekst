<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { NFlex, NButton, NIcon } from 'naive-ui';
import ThemeModeSwitcher from '@/components/navigation/ThemeModeSwitcher.vue';
import LocaleSwitcher from '@/components/navigation/LocaleSwitcher.vue';
import UserActionsButton from '@/components/navigation/UserActionsButton.vue';
import QuickSearchWidget from '@/components/navigation/QuickSearch.vue';
import HelpNavButton from '@/components/navigation/HelpNavButton.vue';
import { useAuthStore, useBrowseStore, useStateStore, useThemeStore } from '@/stores';
import { useRoute, RouterLink } from 'vue-router';
import { usePlatformData } from '@/composables/platformData';
import NavigationMenu from '@/components/navigation/NavigationMenu.vue';
import { useMainMenuOptions } from './navMenuOptions';
import DrawerMenu from './DrawerMenu.vue';
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';
import logo from '@/assets/logo.png';
import logoDarkmode from '@/assets/logo-darkmode.png';
import { HamburgerMenuIcon } from '@/icons';
import { STATIC_PATH } from '@/common';

const { pfData, systemHome } = usePlatformData();
const auth = useAuthStore();
const theme = useThemeStore();
const state = useStateStore();
const browse = useBrowseStore();
const route = useRoute();

const { menuOptions: mainMenuOptions } = useMainMenuOptions(false);
const menuOpen = ref(false);
const showUserActionsButton = computed(
  () => pfData.value?.security?.closedMode === false || auth.loggedIn
);

const customLogoError = ref(false);
const logoPath = computed(() =>
  customLogoError.value
    ? theme.darkMode
      ? logoDarkmode
      : logo
    : theme.darkMode
      ? `${STATIC_PATH}/logo-darkmode.png`
      : `${STATIC_PATH}/logo.png`
);

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

watch(
  () => route.name,
  () => {
    menuOpen.value = false;
  }
);
</script>

<template>
  <n-flex
    align="center"
    :wrap="false"
    class="navbar"
    :class="state.smallScreen && 'navbar-smallscreen'"
  >
    <img class="navbar-logo" alt="" :src="logoPath" @error="customLogoError = true" />
    <n-flex vertical style="flex-grow: 2; gap: 0">
      <n-flex align="baseline">
        <router-link :to="titleLinkTo">
          <div class="text-gigantic">{{ pfData?.settings.infoPlatformName }}</div>
        </router-link>
        <div v-if="pfData?.settings.infoSubtitle?.length" class="translucent text-tiny">
          <translation-display :value="pfData?.settings.infoSubtitle" />
        </div>
      </n-flex>
      <navigation-menu v-if="!state.smallScreen" :options="mainMenuOptions" />
    </n-flex>

    <div v-if="!state.smallScreen" class="navbar-menu">
      <div class="navbar-menu-extra">
        <quick-search-widget />
        <theme-mode-switcher />
        <locale-switcher />
        <help-nav-button />
        <user-actions-button v-if="showUserActionsButton" />
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

  <drawer-menu
    v-if="state.smallScreen"
    v-model:show="menuOpen"
    :show-user-actions-button="showUserActionsButton"
  />
</template>

<style scoped>
.navbar {
  gap: 1.5rem !important;
  max-width: var(--max-app-width);
  margin: 0 auto;
  padding: var(--content-gap) var(--layout-gap);
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

.navbar-menu {
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

<script setup lang="ts">
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';
import DrawerMenu from '@/components/navigation/DrawerMenu.vue';
import LocaleSwitcher from '@/components/navigation/LocaleSwitcher.vue';
import NavigationMenu from '@/components/navigation/NavigationMenu.vue';
import { useMainMenuOptions } from '@/components/navigation/navMenuOptions';
import ThemeModeSwitcher from '@/components/navigation/ThemeModeSwitcher.vue';
import UserActionsButton from '@/components/navigation/UserActionsButton.vue';
import QuickSearch from '@/components/search/QuickSearch.vue';
import { useLogo } from '@/composables/logo';
import { usePlatformData } from '@/composables/platformData';
import { CorrectionNoteIcon, HamburgerMenuIcon, MessageIcon } from '@/icons';
import {
  useAuthStore,
  useBrowseStore,
  useResourcesStore,
  useStateStore,
  useUserMessagesStore,
} from '@/stores';
import { NBadge, NButton, NFlex, NIcon } from 'naive-ui';
import { computed, ref } from 'vue';
import { RouterLink } from 'vue-router';

const { pfData, systemHome } = usePlatformData();
const auth = useAuthStore();
const state = useStateStore();
const browse = useBrowseStore();
const userMessages = useUserMessagesStore();
const resources = useResourcesStore();

const { menuOptions: mainMenuOptions } = useMainMenuOptions(false);
const menuOpen = ref(false);
const showUserActionsButton = computed(
  () => pfData.value?.security.closedMode === false || auth.loggedIn
);

const { pageLogo } = useLogo();
const titleLinkTo = computed(() => {
  if (systemHome.value) {
    return '/';
  } else {
    return {
      name: 'browse',
      params: {
        textSlug: state.text?.slug,
        locId: browse.locationPathHead?.id,
      },
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
    <img
      v-if="pageLogo && pfData?.state.showLogoInHeader"
      class="navbar-logo"
      alt=""
      :src="pageLogo"
    />
    <div class="navbar-title">
      <router-link :to="titleLinkTo">
        <div class="text-gigantic">{{ pfData?.state.platformName }}</div>
      </router-link>
      <div v-if="pfData?.state.platformSubtitle.length" class="translucent text-tiny">
        <translation-display :value="pfData?.state.platformSubtitle" />
      </div>
    </div>

    <n-flex
      v-if="!state.smallScreen"
      justify="end"
      align="flex-start"
      style="flex-grow: 2; align-self: stretch"
    >
      <theme-mode-switcher />
      <locale-switcher />
      <user-actions-button v-if="showUserActionsButton" />
    </n-flex>

    <n-badge
      v-else
      :show="!!userMessages.unreadCount || !!resources.correctionsCountTotal"
      :offset="[-8, 6]"
    >
      <template #value>
        <n-flex :wrap="false" size="small">
          <n-icon v-if="!!resources.correctionsCountTotal" :component="CorrectionNoteIcon" />
          <n-icon v-if="!!userMessages.unreadCount" :component="MessageIcon" />
        </n-flex>
      </template>
      <n-button
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
    </n-badge>
  </n-flex>

  <n-flex align="center" class="navbar-menu">
    <navigation-menu v-if="!state.smallScreen" :options="mainMenuOptions" style="flex: 6 1" />
    <drawer-menu v-else v-model:show="menuOpen" :show-user-actions-button="showUserActionsButton" />
    <quick-search :class="{ 'my-sm': state.smallScreen }" style="flex: 1 1 300px" />
  </n-flex>
</template>

<style scoped>
.navbar {
  max-width: var(--max-app-width);
  margin: 0 auto;
  padding: var(--gap-lg);
}

.navbar-smallscreen {
  padding: var(--gap-lg);
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
  margin: 0 auto var(--gap-md) 0;
  padding: 0 var(--gap-lg);
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

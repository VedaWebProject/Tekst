<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
// import { useWindowSize } from '@vueuse/core';
// import { useStateStore } from '@/stores';
import MainNavigationRouterLink from './MainNavigationRouterLink.vue';
import ThemeModeSwitcher from '../ThemeModeSwitcher.vue';
import LanguageSwitcher from '../LanguageSwitcher.vue';
import AccountOptionsButton from '../AccountOptionsButton.vue';

import InfoOutlined from '@vicons/material/InfoOutlined';
import MenuBookOutlined from '@vicons/material/MenuBookOutlined';
import SearchRound from '@vicons/material/SearchRound';
import HelpOutlineRound from '@vicons/material/HelpOutlineRound';

const route = useRoute();
// const state = useStateStore();
const activeRouteName = computed(() => route.name?.toString() || null);
const activeKey = ref<string | null>(activeRouteName.value);
watch(activeRouteName, (newRouteName) => (activeKey.value = newRouteName));

// const { width } = useWindowSize();
</script>

<template>
  <div class="main-navigation">
    <MainNavigationRouterLink label="About" route="about" :icon="InfoOutlined" />
    <MainNavigationRouterLink label="Browse" route="browse" :icon="MenuBookOutlined" />
    <MainNavigationRouterLink label="Search" route="search" :icon="SearchRound" />
    <MainNavigationRouterLink label="Help" route="help" :icon="HelpOutlineRound" />
    <div class="main-nav-divider"></div>
    <ThemeModeSwitcher />
    <LanguageSwitcher />
    <AccountOptionsButton />
  </div>
</template>

<style scoped>
.main-navigation {
  display: flex;
}

.main-navigation > .main-nav-divider {
  flex-grow: 2;
}
</style>

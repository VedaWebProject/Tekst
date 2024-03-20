<script setup lang="ts">
import { RouterView } from 'vue-router';
import NavigationMenu from '@/components/navigation/NavigationMenu.vue';
import { useAccountMenuOptions } from '@/components/navigation/navMenuOptions';
import { useStateStore } from '@/stores';

const state = useStateStore();
const { menuOptions } = useAccountMenuOptions();
</script>

<template>
  <navigation-menu v-if="!state.smallScreen" :options="menuOptions" embed center />
  <router-view></router-view>
</template>

<style scoped></style>

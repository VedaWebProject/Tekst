<script setup lang="ts">
import { RouterView } from 'vue-router';
import NavigationMenu from '@/components/navigation/NavigationMenu.vue';
import { useStateStore } from '@/stores';
import { useAdminMenuOptions } from '@/components/navigation/navMenuOptions';

const state = useStateStore();
const { menuOptions } = useAdminMenuOptions();
</script>

<template>
  <navigation-menu v-if="!state.smallScreen" :options="menuOptions" embed center />
  <router-view></router-view>
</template>

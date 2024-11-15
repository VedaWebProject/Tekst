<script setup lang="ts">
import NavigationMenu from '@/components/navigation/NavigationMenu.vue';
import { useAdminMenuOptions } from '@/components/navigation/navMenuOptions';
import { useStateStore } from '@/stores';
import { RouterView } from 'vue-router';

const state = useStateStore();
const { menuOptions } = useAdminMenuOptions();
</script>

<template>
  <navigation-menu v-if="!state.smallScreen" :options="menuOptions" embed center />
  <router-view></router-view>
</template>

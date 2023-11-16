<script setup lang="ts">
import { RouterView } from 'vue-router';
import NavigationMenu from '@/components/navigation/NavigationMenu.vue';
import { useStateStore } from '@/stores';
import { useAdminMenuOptions } from '@/components/navigation/navMenuOptions';

const state = useStateStore();
const { menuOptions } = useAdminMenuOptions();
</script>

<template>
  <div v-if="!state.smallScreen" style="display: flex; justify-content: center">
    <NavigationMenu :options="menuOptions" embed />
  </div>
  <router-view></router-view>
</template>

<style scoped></style>

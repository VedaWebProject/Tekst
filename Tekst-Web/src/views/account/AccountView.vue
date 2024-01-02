<script setup lang="ts">
import { RouterView } from 'vue-router';
import NavigationMenu from '@/components/navigation/NavigationMenu.vue';
import { useAccountMenuOptions } from '@/components/navigation/navMenuOptions';

const { menuOptions } = useAccountMenuOptions();
</script>

<template>
  <NavigationMenu :options="menuOptions" embed center />
  <router-view></router-view>
</template>

<style scoped></style>

<script setup lang="ts">
import { RouterView } from 'vue-router';
import NavigationMenu from '@/components/navigation/NavigationMenu.vue';
import { accountMenuOptions } from '@/components/navigation/navMenuOptions';
</script>

<template>
  <div style="display: flex; justify-content: center">
    <NavigationMenu :options="accountMenuOptions" />
  </div>
  <router-view></router-view>
</template>

<style scoped></style>

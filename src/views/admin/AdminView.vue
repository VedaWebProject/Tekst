<script setup lang="ts">
import { RouterView } from 'vue-router';
import NavBarRouterLink from '@/components/navigation/NavBarRouterLink.vue';

import PeopleRound from '@vicons/material/PeopleRound';
import DashboardRound from '@vicons/material/DashboardRound';
</script>

<template>
  <div style="display: flex">
    <NavBarRouterLink
      :label="$t('administration.overview')"
      :route="{ name: 'adminOverview' }"
      :icon="DashboardRound"
      show-icon
    />
    <NavBarRouterLink
      :label="$t('administration.users')"
      :route="{ name: 'adminUsers' }"
      :icon="PeopleRound"
      show-icon
    />
  </div>
  <div class="content-block">
    <h1>{{ $t('administration.heading') }}</h1>
    <router-view></router-view>
  </div>
</template>

<style scoped></style>

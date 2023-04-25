<script setup lang="ts">
import { RouterView } from 'vue-router';
import SecondaryNavBar from '@/components/navigation/SecondaryNavBar.vue';
import NavBarRouterLink from '@/components/navigation/NavBarRouterLink.vue';

import PeopleRound from '@vicons/material/PeopleRound';
import BarChartRound from '@vicons/material/BarChartRound';
</script>

<template>
  <SecondaryNavBar>
    <NavBarRouterLink
      :label="$t('admin.statistics.heading')"
      :route="{ name: 'adminStatistics' }"
      :icon="BarChartRound"
      show-icon
    />
    <NavBarRouterLink
      :label="$t('admin.users.heading')"
      :route="{ name: 'adminUsers' }"
      :icon="PeopleRound"
      show-icon
    />
  </SecondaryNavBar>

  <router-view></router-view>
</template>

<style scoped></style>

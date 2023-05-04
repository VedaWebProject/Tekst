<script setup lang="ts">
import { RouterView } from 'vue-router';
import SecondaryNavBar from '@/components/navigation/SecondaryNavBar.vue';
import NavBarRouterLink from '@/components/navigation/NavBarRouterLink.vue';

import PeopleRound from '@vicons/material/PeopleRound';
import BarChartRound from '@vicons/material/BarChartRound';
import LibraryBooksRound from '@vicons/material/LibraryBooksRound';
import { useStateStore } from '@/stores';

const state = useStateStore();
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
    <NavBarRouterLink
      :label="$t('admin.texts.heading')"
      :route="{ name: 'adminTexts', params: { text: state.text?.slug } }"
      :icon="LibraryBooksRound"
      show-icon
    />
  </SecondaryNavBar>

  <router-view></router-view>
</template>

<style scoped></style>

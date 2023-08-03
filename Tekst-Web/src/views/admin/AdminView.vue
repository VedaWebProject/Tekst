<script setup lang="ts">
import { RouterView } from 'vue-router';
import { useStateStore } from '@/stores';
import SecondaryNavBar from '@/components/navigation/SecondaryNavBar.vue';
import NavBarRouterLink from '@/components/navigation/NavBarRouterLink.vue';

import PeopleRound from '@vicons/material/PeopleRound';
import BarChartRound from '@vicons/material/BarChartRound';
import MenuBookOutlined from '@vicons/material/MenuBookOutlined';
import AddCircleOutlineRound from '@vicons/material/AddCircleOutlineRound';
import { useI18n } from 'vue-i18n';

const state = useStateStore();
const { t } = useI18n({ useScope: 'global' });
</script>

<template>
  <SecondaryNavBar>
    <NavBarRouterLink
      :label="t('admin.statistics.heading')"
      :route="{ name: 'adminStatistics' }"
      :icon="BarChartRound"
      show-icon
    />
    <NavBarRouterLink
      :label="t('admin.users.heading')"
      :route="{ name: 'adminUsers' }"
      :icon="PeopleRound"
      show-icon
    />
    <NavBarRouterLink
      :label="t('admin.texts.heading')"
      :route="{ name: 'adminTexts', params: { text: state.text?.slug } }"
      :icon="MenuBookOutlined"
      show-icon
    />
    <NavBarRouterLink
      :label="t('admin.newText.heading')"
      :route="{ name: 'adminNewText' }"
      :icon="AddCircleOutlineRound"
      show-icon
    />
  </SecondaryNavBar>

  <router-view></router-view>
</template>

<style scoped></style>

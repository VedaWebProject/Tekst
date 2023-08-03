<script setup lang="ts">
import NavBarRouterLink from '@/components/navigation/NavBarRouterLink.vue';
import SecondaryNavBar from '@/components/navigation/SecondaryNavBar.vue';
import { useI18n } from 'vue-i18n';
import { RouterView } from 'vue-router';

import ManageAccountsRound from '@vicons/material/ManageAccountsRound';
import RemoveRedEyeRound from '@vicons/material/RemoveRedEyeRound';

const { t } = useI18n({ useScope: 'global' });
</script>

<template>
  <SecondaryNavBar>
    <NavBarRouterLink
      :label="t('account.profile')"
      :route="{ name: 'accountProfile' }"
      :icon="RemoveRedEyeRound"
      show-icon
    />
    <NavBarRouterLink
      :label="t('account.manage.heading')"
      :route="{ name: 'accountManage' }"
      :icon="ManageAccountsRound"
      show-icon
    />
  </SecondaryNavBar>

  <router-view></router-view>
</template>

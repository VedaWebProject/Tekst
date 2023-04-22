<script setup lang="ts">
import NavBarRouterLink from '@/components/navigation/NavBarRouterLink.vue';
import SecondaryNavBar from '@/components/navigation/SecondaryNavBar.vue';
import { useAuthStore } from '@/stores';
import { RouterView } from 'vue-router';

import ManageAccountsRound from '@vicons/material/ManageAccountsRound';

const auth = useAuthStore();
</script>

<template>
  <SecondaryNavBar>
    <NavBarRouterLink
      :label="$t('user.account.headingManage')"
      :route="{ name: 'accountManage' }"
      :icon="ManageAccountsRound"
      show-icon
    />
  </SecondaryNavBar>

  <div class="content-block">
    <h1>{{ $t('user.account.heading', { name: auth.user?.firstName }) }}</h1>
    <router-view></router-view>
  </div>
</template>

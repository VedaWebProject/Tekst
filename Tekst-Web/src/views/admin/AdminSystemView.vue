<script setup lang="ts">
import { RouterView } from 'vue-router';

import NavBarRouterLink from '@/components/navigation/NavBarRouterLink.vue';
import SecondaryNavBar from '@/components/navigation/SecondaryNavBar.vue';
import IconHeading from '@/components/typography/IconHeading.vue';

import SettingsApplicationsOutlined from '@vicons/material/SettingsApplicationsOutlined';
</script>

<template>
  <SecondaryNavBar style="margin-top: 0.5rem">
    <NavBarRouterLink
      :label="$t('admin.system.pages.heading')"
      :route="{ name: 'adminSystemPages' }"
      size="tiny"
    />
    <NavBarRouterLink
      :label="$t('admin.system.segments.heading')"
      :route="{ name: 'adminSystemSegments' }"
      size="tiny"
    />
  </SecondaryNavBar>

  <IconHeading level="1" :icon="SettingsApplicationsOutlined">
    {{ $t('admin.system.heading') }}
  </IconHeading>

  <router-view></router-view>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router';

import IconHeading from '@/components/typography/IconHeading.vue';
import SettingsApplicationsOutlined from '@vicons/material/SettingsApplicationsOutlined';
</script>

<template>
  <IconHeading level="1" :icon="SettingsApplicationsOutlined">
    {{ $t('admin.system.heading') }}
  </IconHeading>
  <router-view></router-view>
</template>

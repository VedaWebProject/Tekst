<script setup lang="ts">
import { RouterView } from 'vue-router';
import IconHeading from '@/components/generic/IconHeading.vue';

import { SettingsIcon } from '@/icons';
</script>

<template>
  <icon-heading level="1" :icon="SettingsIcon">
    {{ $t('admin.system.heading') }}
  </icon-heading>
  <router-view></router-view>
</template>

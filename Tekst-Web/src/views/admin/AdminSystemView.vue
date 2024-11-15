<script setup lang="ts">
import IconHeading from '@/components/generic/IconHeading.vue';
import { RouterView } from 'vue-router';

import { SystemIcon } from '@/icons';
</script>

<template>
  <icon-heading level="1" :icon="SystemIcon">
    {{ $t('admin.system.heading') }}
  </icon-heading>
  <router-view></router-view>
</template>

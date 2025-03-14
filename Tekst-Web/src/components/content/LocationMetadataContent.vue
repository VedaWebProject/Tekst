<script setup lang="ts">
import type { LocationMetadataResourceRead } from '@/api';
import { useStateStore, useThemeStore } from '@/stores';
import { useThemeVars } from 'naive-ui';

const props = withDefaults(
  defineProps<{
    resource: LocationMetadataResourceRead;
    focusView?: boolean;
  }>(),
  {
    focusView: false,
  }
);

const state = useStateStore();
const theme = useThemeStore();
const nuiTheme = useThemeVars();

// TODO
</script>

<template>
  <div>
    <!-- TODO -->
  </div>
</template>

<style scoped>

</style>

<script setup lang="ts">
import { NIcon } from 'naive-ui';
import type { Component } from 'vue';

import { HourglassIcon } from '@/icons';

const props = defineProps<{
  message: string;
  icon: Component;
  loading?: boolean;
}>();
</script>

<template>
  <div class="huge-labelled-icon">
    <n-icon :size="128" :component="props.loading ? HourglassIcon : props.icon" />
    <div style="font-size: var(--app-ui-font-size-huge)">
      {{ !props.loading && props.message }}
    </div>
  </div>
</template>

<style scoped>
.huge-labelled-icon {
  width: 768px;
  max-width: 100%;
  margin: 0 auto;
  padding: 3rem 0;
  text-align: center;
  opacity: 0.5;
  font-size: var(--app-ui-font-size-huge);
}

.huge-labelled-icon > * {
  text-align: center;
}
</style>

<script setup lang="ts">
import { NButton, NIcon } from 'naive-ui';
import type { Component } from 'vue';

defineProps<{
  iconComponent: Component;
  title: string;
  disabled?: boolean;
  full?: boolean;
  toggled?: boolean;
}>();
</script>

<template>
  <n-button
    :quaternary="!toggled"
    :secondary="toggled"
    :type="toggled ? 'primary' : undefined"
    :block="full"
    :circle="!full"
    :focusable="false"
    :title="!full ? title : undefined"
    :disabled="disabled"
    :class="{ 'block-left-align': full }"
  >
    <template #icon>
      <n-icon :component="iconComponent" />
    </template>
    <template v-if="full" #default>
      {{ title }}
    </template>
  </n-button>
</template>

<style scoped>
.block-left-align {
  justify-content: flex-start;
}
</style>

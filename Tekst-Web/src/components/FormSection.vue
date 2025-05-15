<script setup lang="ts">
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { NFlex } from 'naive-ui';

withDefaults(
  defineProps<{
    title?: string;
    helpKey?: string;
    showBox?: boolean;
  }>(),
  {
    showBox: true,
  }
);
</script>

<template>
  <div :class="{ 'gray-box': showBox }">
    <n-flex v-if="title || $slots.title" align="center" :wrap="false" class="mb-md">
      <b class="text-medium" :class="{ 'mt-sm': !showBox }">
        <slot name="title">{{ title || '???' }}</slot>
      </b>
      <help-button-widget v-if="helpKey" :help-key="helpKey" />
    </n-flex>
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { NFlex } from 'naive-ui';

defineProps<{
  title?: string;
  helpKey?: string;
}>();
</script>

<template>
  <div class="gray-box">
    <n-flex v-if="title || $slots.title" align="center" :wrap="false" class="mb-md">
      <b
        ><slot name="title">{{ title || '???' }}</slot></b
      >
      <help-button-widget v-if="helpKey" :help-key="helpKey" />
      <n-flex v-if="$slots.extra" justify="flex-end" style="flex: 2">
        <slot name="extra"></slot>
      </n-flex>
    </n-flex>
    <slot></slot>
  </div>
</template>

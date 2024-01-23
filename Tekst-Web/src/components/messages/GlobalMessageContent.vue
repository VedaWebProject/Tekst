<script setup lang="ts">
import { NCollapse, NCollapseItem } from 'naive-ui';
</script>

<template>
  <slot></slot>
  <n-collapse v-if="$slots.details" style="margin-top: 0.75rem">
    <n-collapse-item
      :title="$t('general.details')"
      name="details"
      style="margin: 0; font-size: var(--app-ui-font-size-mini)"
    >
      <pre
        style="
          font-family: monospace;
          font-size: var(--app-ui-font-size-mini);
          font-weight: var(--app-ui-font-weight-light);
          white-space: pre-wrap;
          line-height: 1;
        "
      ><slot name="details"></slot></pre>
    </n-collapse-item>
  </n-collapse>
</template>

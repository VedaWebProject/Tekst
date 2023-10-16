<script setup lang="ts">
import { NCollapse, NCollapseItem } from 'naive-ui';
</script>

<template>
  <slot></slot>
  <n-collapse v-if="$slots.details" style="margin-top: 0.75rem">
    <n-collapse-item
      :title="$t('errors.details')"
      name="details"
      style="margin: 0; font-size: var(--app-ui-font-size-mini)"
    >
      <div
        style="
          font-family: monospace;
          font-size: var(--app-ui-font-size-mini);
          font-weight: var(--app-ui-font-weight-light);
        "
      >
        <slot name="details"></slot>
      </div>
    </n-collapse-item>
  </n-collapse>
</template>

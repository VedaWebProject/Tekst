<script setup lang="ts">
import { NCollapse, NCollapseItem } from 'naive-ui';
</script>

<template>
  <slot></slot>
  <n-collapse v-if="$slots.details" style="margin-top: var(--content-gap)">
    <n-collapse-item
      :title="$t('general.details')"
      name="details"
      class="text-mini"
      style="margin: 0"
    >
      <pre
        style="
          font-family: monospace;
          font-size: var(--font-size-mini);
          white-space: pre-wrap;
          line-height: 1;
        "
      ><slot name="details"></slot></pre>
    </n-collapse-item>
  </n-collapse>
</template>

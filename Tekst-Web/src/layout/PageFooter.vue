<script setup lang="ts">
import SegmentRenderer from '@/components/SegmentRenderer.vue';
</script>

<template>
  <footer>
    <SegmentRenderer segment-key="systemFooter" />
  </footer>
</template>

<style scoped>
footer {
  padding: 1.75rem var(--layout-gap);
  font-size: var(--app-ui-font-size-small);
}

footer > * {
  max-width: var(--max-app-width);
  margin: 0 auto;
}
</style>

<script setup lang="ts">
import type { PlainTextResourceRead } from '@/api';
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    resource: PlainTextResourceRead;
    reduced?: boolean;
  }>(),
  {
    reduced: false,
  }
);

const contents = computed(() =>
  props.resource.contents?.map((c) => ({
    ...c,
    text: props.reduced ? c.text.replace(/\n+/g, ' ') : c.text,
  }))
);
</script>

<template>
  <div :style="{ fontFamily: resource.config?.general?.font || undefined }">
    <div
      v-for="content in contents"
      :key="content.id"
      class="plain-text-content"
      :title="content.comment || undefined"
    >
      <template v-if="content.text">
        <template v-if="!reduced || !resource.config?.general?.reducedViewOneline">
          {{ content.text }}
        </template>
        <template v-else>
          {{ content.text }}
        </template>
      </template>
    </div>
  </div>
</template>

<style scoped>
.plain-text-content {
  white-space: pre-wrap;
  margin-top: var(--content-gap);
}
.plain-text-content:first-child {
  margin-top: inherit;
}
</style>

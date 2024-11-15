<script setup lang="ts">
import type { RichTextResourceRead } from '@/api';

const props = withDefaults(
  defineProps<{
    resource: RichTextResourceRead;
    reduced?: boolean;
  }>(),
  {
    reduced: false,
  }
);

const fontStyle = {
  fontFamily: props.resource.config.general.font || 'Tekst Content Font',
};
</script>

<template>
  <div
    v-for="content in resource.contents"
    :key="content.id"
    :class="{
      'rich-text-content-wrapper': resource.contents?.length && resource.contents?.length > 1,
    }"
  >
    <div v-if="!reduced" :style="fontStyle">
      <!-- eslint-disable-next-line vue/no-v-html -->
      <div v-html="content.html"></div>
    </div>
    <div v-else class="translucent i ui-font">
      {{ $t('contents.msgContentNoReducedView') }}
    </div>
  </div>
</template>

<style scoped>
.rich-text-content-wrapper {
  padding: 1.5rem 0;
  border-bottom: 1px solid var(--main-bg-color);
}

.rich-text-content-wrapper:last-child {
  border-bottom: none;
}
</style>

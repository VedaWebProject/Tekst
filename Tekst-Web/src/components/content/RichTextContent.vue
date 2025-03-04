<script setup lang="ts">
import type { RichTextResourceRead } from '@/api';
import HydratedHtml from '@/components/generic/HydratedHtml.vue';
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    resource: RichTextResourceRead;
    reduced?: boolean;
  }>(),
  {
    reduced: false,
  }
);

const fontStyle = { fontFamily: props.resource.config.general.font || 'Tekst Content Font' };
const contentCss = computed(() =>
  Object.fromEntries(props.resource.config.general.contentCss.map((c) => [c.prop, c.value]))
);
const cutomStyle = computed(() => ({ ...contentCss.value, ...fontStyle }));
</script>

<template>
  <div>
    <div
      v-for="content in resource.contents"
      :key="content.id"
      :class="{
        'rich-text-content-wrapper': resource.contents?.length && resource.contents?.length > 1,
      }"
    >
      <hydrated-html v-if="!reduced" :html="content.html" :style="cutomStyle" />
      <div v-else class="translucent i ui-font text-small">
        {{ $t('contents.msgContentNoReducedView') }}
      </div>
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

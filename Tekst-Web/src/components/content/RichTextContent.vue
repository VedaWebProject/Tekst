<script setup lang="ts">
import type { RichTextResourceRead } from '@/api';
import HydratedHtml from '@/components/generic/HydratedHtml.vue';
import { computed } from 'vue';
import CommonContentDisplay from './CommonContentDisplay.vue';
import MissingContent from './MissingContent.vue';

const props = withDefaults(
  defineProps<{
    resource: RichTextResourceRead;
    focusView?: boolean;
    showComments?: boolean;
  }>(),
  {
    focusView: false,
  }
);

const fontStyle = {
  fontFamily: props.resource.config.general.font || 'var(--font-family-content)',
};
const contentCss = computed(() =>
  Object.fromEntries(props.resource.config.special.contentCss.map((c) => [c.prop, c.value]))
);
const cutomStyle = computed(() => ({ ...fontStyle, ...contentCss.value }));
</script>

<template>
  <div>
    <template
      v-for="(content, contentIndex) in resource.contents"
      :key="content?.id ?? `${contentIndex}_missing`"
    >
      <common-content-display
        v-if="content"
        :show-comments="showComments"
        :comments="content.comments"
        :font="fontStyle.fontFamily"
      >
        <div
          :class="{
            'rich-text-content-wrapper': resource.contents?.length && resource.contents?.length > 1,
          }"
        >
          <hydrated-html v-if="!focusView" :html="content.html" :style="cutomStyle" />
          <div v-else class="translucent i font-ui text-small">
            {{ $t('contents.msgContentNoFocusView') }}
          </div>
        </div>
      </common-content-display>
      <missing-content v-else />
    </template>
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

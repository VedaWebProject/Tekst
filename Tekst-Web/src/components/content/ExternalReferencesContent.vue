<script setup lang="ts">
import type { ExternalReferencesResourceRead } from '@/api';
import { LinkIcon } from '@/icons';
import { NFlex, NIcon } from 'naive-ui';
import { type CSSProperties } from 'vue';

const props = withDefaults(
  defineProps<{
    resource: ExternalReferencesResourceRead;
    focusView?: boolean;
  }>(),
  {
    focusView: false,
  }
);

const fontStyle: CSSProperties = {
  fontFamily: props.resource.config.general.font || 'Tekst UI Font',
};
</script>

<template>
  <div>
    <n-flex
      v-for="content in resource.contents"
      :key="content.id"
      :vertical="!focusView"
      :wrap="false"
      class="ext-ref-content"
      :class="{ 'mt-lg': !focusView }"
    >
      <n-flex v-for="(link, index) in content.links" :key="index" vertical size="small">
        <n-flex align="center" :wrap="false">
          <n-icon v-if="!focusView" :component="LinkIcon" />
          <a
            :href="link.url"
            target="_blank"
            :title="link.title + (link.description ? ' – ' + link.description : '')"
            style="line-height: 1.2"
            :style="fontStyle"
            rel="noopener noreferrer"
          >
            <n-icon v-if="focusView" :component="LinkIcon" size="24" />
            <template v-else>{{ link.title }}</template>
          </a>
        </n-flex>
        <n-flex v-if="!focusView && link.description" :wrap="false">
          <n-icon />
          <div class="text-tiny translucent ext-ref-description">{{ link.description }}</div>
        </n-flex>
      </n-flex>
    </n-flex>
  </div>
</template>

<style scoped>
.ext-ref-content:not(:only-child) {
  padding: var(--gap-lg) 0;
}

.ext-ref-content {
  margin-top: inherit;
}

.ext-ref-content:not(:first-child) {
  padding-top: var(--gap-lg);
  border-top: 1px solid var(--main-bg-color);
}

.ext-ref-description {
  white-space: pre-line;
}
</style>

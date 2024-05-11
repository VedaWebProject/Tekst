<script setup lang="ts">
import type { ExternalReferencesResourceRead } from '@/api';
import { type CSSProperties } from 'vue';
import { NIcon, NFlex } from 'naive-ui';
import { LinkIcon } from '@/icons';

const props = withDefaults(
  defineProps<{
    resource: ExternalReferencesResourceRead;
    reduced?: boolean;
  }>(),
  {
    reduced: false,
  }
);

const fontStyle: CSSProperties = {
  fontFamily: props.resource.config?.general?.font || 'Tekst UI Font',
};
</script>

<template>
  <div>
    <n-flex
      v-for="content in resource.contents"
      :key="content.id"
      :vertical="!reduced"
      :wrap="false"
      class="ext-ref-content text-medium"
    >
      <n-flex v-for="(link, index) in content.links" :key="index" align="center" :wrap="false">
        <n-icon v-if="!reduced" :component="LinkIcon" />
        <a
          :href="link.url"
          target="_blank"
          :title="link.caption || undefined"
          style="line-height: 1.2"
          :style="fontStyle"
          rel="noopener noreferrer"
        >
          <n-icon v-if="reduced" :component="LinkIcon" size="24" />
          <template v-else>{{ link.caption }}</template>
        </a>
      </n-flex>
    </n-flex>
  </div>
</template>

<style scoped>
.ext-ref-content:not(:only-child) {
  padding: var(--layout-gap) 0;
}
.ext-ref-content {
  margin-top: inherit;
}
.ext-ref-content:not(:first-child) {
  padding-top: var(--layout-gap);
  border-top: 1px solid var(--main-bg-color);
}
</style>

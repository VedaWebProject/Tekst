<script setup lang="ts">
import type { ImagesResourceRead } from '@/api';
import { type CSSProperties } from 'vue';
import { NFlex, NImage, NImageGroup } from 'naive-ui';
import { useStateStore } from '@/stores';
import { type ImageRenderToolbarProps } from 'naive-ui/es/image/src/public-types';

const props = withDefaults(
  defineProps<{
    resource: ImagesResourceRead;
    reduced?: boolean;
  }>(),
  {
    reduced: false,
  }
);

const state = useStateStore();

const fontStyle: CSSProperties = {
  fontFamily: props.resource.config?.general?.font || 'Tekst UI Font',
};

const renderToolbar = ({ nodes }: ImageRenderToolbarProps) => {
  return [
    nodes.prev,
    nodes.next,
    nodes.rotateCounterclockwise,
    nodes.rotateClockwise,
    nodes.zoomOut,
    nodes.zoomIn,
    nodes.close,
  ];
};
</script>

<template>
  <div v-if="!reduced">
    <n-flex
      v-for="content in resource.contents"
      :key="content.id"
      vertical
      :wrap="false"
      class="images-content"
    >
      <n-image-group :render-toolbar="renderToolbar">
        <n-flex :size="[32, 22]">
          <div v-for="(image, index) in content.files" :key="index" class="image-container">
            <n-image
              lazy
              :src="image.url"
              :alt="image.caption || undefined"
              :title="image.caption"
              :height="state.smallScreen ? '80px' : '140px'"
            />
            <div class="caption text-small translucent" :style="fontStyle">{{ image.caption }}</div>
          </div>
        </n-flex>
      </n-image-group>
    </n-flex>
  </div>
  <div v-else class="translucent i ui-font">
    {{ $t('contents.msgContentNoReducedView') }}
  </div>
</template>

<style scoped>
.images-content:not(:only-child) {
  padding: var(--layout-gap) 0;
}
.images-content {
  margin-top: inherit;
}
.images-content:not(:first-child) {
  padding-top: var(--layout-gap);
  border-top: 1px solid var(--main-bg-color);
}
.image-container {
  max-width: 100%;
}
.caption {
  white-space: pre-line;
}
</style>

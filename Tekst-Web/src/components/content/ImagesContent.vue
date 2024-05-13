<script setup lang="ts">
import type { ImagesResourceRead } from '@/api';
import { computed, type CSSProperties } from 'vue';
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

const imageHeight = computed(() =>
  state.smallScreen ? (props.reduced ? '60px' : '80px') : props.reduced ? '60px' : '140px'
);
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
  <div>
    <n-flex
      v-for="content in resource.contents"
      :key="content.id"
      vertical
      :wrap="false"
      class="images-content"
    >
      <n-image-group :render-toolbar="renderToolbar">
        <n-flex :size="reduced ? [20, 10] : [32, 22]">
          <figure
            v-for="(image, index) in content.files"
            :key="index"
            class="image-container"
            :class="{ 'small-screen': state.smallScreen }"
          >
            <n-image
              lazy
              :src="image.thumbUrl || image.url"
              :preview-src="image.url"
              :alt="image.caption || undefined"
              :title="image.caption"
              :height="imageHeight"
            />
            <figcaption v-if="!reduced" class="caption text-small translucent" :style="fontStyle">
              {{ image.caption }}
            </figcaption>
          </figure>
        </n-flex>
      </n-image-group>
    </n-flex>
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
  margin: 0;
  max-width: 40%;
}
.image-container.small-screen {
  max-width: 100%;
}
.caption {
  white-space: pre-line;
}
</style>

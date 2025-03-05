<script setup lang="ts">
import type { ImagesResourceRead } from '@/api';
import { LinkIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { NFlex, NIcon, NImage, NImageGroup } from 'naive-ui';
import { type ImageRenderToolbarProps } from 'naive-ui/es/image/src/public-types';
import { computed, type CSSProperties } from 'vue';

const props = withDefaults(
  defineProps<{
    resource: ImagesResourceRead;
    focusView?: boolean;
  }>(),
  {
    focusView: false,
  }
);

const state = useStateStore();

const imageSize = computed(() =>
  state.smallScreen ? (props.focusView ? '60px' : '80px') : props.focusView ? '60px' : '200px'
);
const fontStyle: CSSProperties = {
  fontFamily: props.resource.config.general.font || 'Tekst UI Font',
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
        <n-flex :vertical="!focusView">
          <figure v-for="(image, index) in content.files" :key="index" class="image-container">
            <n-flex :wrap="state.smallScreen" :size="[18, 0]">
              <div>
                <n-image
                  lazy
                  :src="image.thumbUrl || image.url"
                  :preview-src="image.url"
                  :alt="image.caption || undefined"
                  :title="image.caption"
                  :width="focusView ? undefined : imageSize"
                  :height="focusView ? imageSize : undefined"
                >
                  <template #placeholder>
                    {{ $t('general.loading') }}
                  </template>
                </n-image>
              </div>
              <figcaption v-if="!focusView" class="caption" :style="fontStyle">
                <span class="text-tiny translucent">{{ image.caption }}</span>
                <a
                  v-if="image.sourceUrl"
                  :href="image.sourceUrl"
                  :title="image.sourceUrl"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="source-link mx-sm"
                >
                  <n-icon :component="LinkIcon" />
                </a>
              </figcaption>
            </n-flex>
          </figure>
        </n-flex>
      </n-image-group>
    </n-flex>
  </div>
</template>

<style scoped>
.images-content:not(:only-child) {
  padding: var(--gap-lg) 0;
}

.images-content {
  margin-top: inherit;
}

.images-content:not(:first-child) {
  padding-top: var(--gap-lg);
  border-top: 1px solid var(--main-bg-color);
}

.image-container {
  margin: 0;
}

.image-container:not(:first-child) {
  padding-top: var(--gap-sm);
  border-top: 1px solid var(--main-bg-color);
}

.focus-view .image-container {
  padding-top: 0;
  border: none;
}

.caption {
  white-space: pre-line;
  line-height: 1.2;
  vertical-align: middle;
}

.caption > .source-link {
  display: inline-block;
  vertical-align: -4px;
}
</style>

<script setup lang="ts">
import type { ExternalReferencesResourceRead } from '@/api';
import { LinkIcon } from '@/icons';
import { NFlex, NIcon } from 'naive-ui';
import { type CSSProperties } from 'vue';
import CommonContentDisplay from './CommonContentDisplay.vue';
import MissingContent from './MissingContent.vue';

const props = withDefaults(
  defineProps<{
    resource: ExternalReferencesResourceRead;
    focusView?: boolean;
    showComments?: boolean;
  }>(),
  {
    focusView: false,
  }
);

const fontStyle: CSSProperties = {
  fontFamily: props.resource.config.general.font || 'var(--font-family-ui)',
};
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
        <n-flex :vertical="!focusView">
          <div v-for="(link, index) in content.links" :key="index">
            <a
              :href="link.url"
              target="_blank"
              :title="
                link.title +
                (link.altRef ? ` (${link.altRef})` : '') +
                (link.description ? ' – ' + link.description : '')
              "
              style="line-height: 1.2"
              :style="fontStyle"
              rel="noopener noreferrer"
            >
              <n-flex align="center" size="small">
                <n-icon :component="LinkIcon" :size="focusView ? 24 : undefined" />
                <span v-if="!focusView">{{ link.title }}</span>
              </n-flex>
            </a>
            <div
              v-if="!focusView && link.description"
              :title="$t('common.description')"
              class="text-small translucent pre-wrap"
            >
              {{ link.description }}
              <span v-if="link.altRef">[{{ link.altRef }}]</span>
            </div>
          </div>
        </n-flex>
      </common-content-display>
      <missing-content v-else />
    </template>
  </div>
</template>

<script setup lang="ts">
import type { ExternalReferencesResourceRead } from '@/api';
import { LinkIcon } from '@/icons';
import { NFlex, NIcon } from 'naive-ui';
import { type CSSProperties } from 'vue';
import CommonContentDisplay from './CommonContentDisplay.vue';

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
    <common-content-display
      v-for="content in resource.contents"
      :key="content.id"
      :show-comments="showComments"
      :authors-comment="content.authorsComment"
      :editors-comment="content.editorsComment"
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
            <n-icon v-if="focusView" :component="LinkIcon" size="24" />
            <template v-else>{{ link.title }} &nearr;</template>
          </a>
          <div
            v-if="!focusView && link.altRef"
            :title="$t('resources.types.externalReferences.contentFields.altRef')"
            class="text-small"
          >
            {{ link.altRef }}
          </div>
          <div
            v-if="!focusView && link.description"
            :title="$t('common.description')"
            class="text-small translucent pre-wrap"
          >
            {{ link.description }}
          </div>
        </div>
      </n-flex>
    </common-content-display>
  </div>
</template>

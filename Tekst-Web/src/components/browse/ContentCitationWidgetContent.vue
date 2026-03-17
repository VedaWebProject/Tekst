<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import CopyToClipboardButton from '@/components/generic/CopyToClipboardButton.vue';
import env from '@/env';
import { $t } from '@/i18n';
import { useStateStore } from '@/stores';
import { NDivider, NThing } from 'naive-ui';
import { computed } from 'vue';

const props = defineProps<{
  resource: AnyResourceRead;
}>();

const state = useStateStore();

const baseUrl = `${origin}${env.WEB_PATH_STRIPPED}`.replace(/\/+$/, '');
const queryPart = `?ts=${new Date().getTime()}&res=${props.resource.id}`;
const browseUrl = computed(() => {
  return (
    `${baseUrl}/texts/${state.text?.slug ?? 'unknown'}` +
    `/browse/${props.resource.contents?.[0]?.locationId ?? 'unknown'}` +
    queryPart
  );
});
const citation = computed(() => props.resource.citation + ' – URL: ' + browseUrl.value);
</script>

<template>
  <div>
    <n-thing v-if="props.resource.citation">
      <template #header>
        <b>{{ $t('browse.contentCitation.full') }}</b>
      </template>
      <template #header-extra>
        <copy-to-clipboard-button size="small" :text="citation" show-msg />
      </template>
      <template #description>
        <p class="text-tiny">{{ citation }}</p>
      </template>
    </n-thing>
    <n-divider v-if="props.resource.citation" />
    <n-thing>
      <template #header>
        <b>{{ $t('browse.contentCitation.urlOnly') }}</b>
      </template>
      <template #header-extra>
        <copy-to-clipboard-button size="small" :text="browseUrl" show-msg />
      </template>
      <template #description>
        <p class="text-tiny">{{ browseUrl }}</p>
      </template>
    </n-thing>
  </div>
</template>

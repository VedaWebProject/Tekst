<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import CopyToClipboardButton from '@/components/generic/CopyToClipboardButton.vue';
import env from '@/env';
import { $t } from '@/i18n';
import { useStateStore } from '@/stores';
import { replaceCurrDatePh, replaceResUrlPh } from '@/utils';
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
const citationRes = computed(() =>
  replaceResUrlPh(
    replaceCurrDatePh(props.resource.citation, state.locale),
    state.text?.slug,
    props.resource.id
  )
);
const citationFull = computed(
  () => `${citationRes.value} – ${$t('common.location')}: ${browseUrl.value}`
);
</script>

<template>
  <div>
    <n-thing v-if="props.resource.citation">
      <template #header>
        <b class="text-small">{{ $t('browse.contentCitation.full') }}</b>
      </template>
      <template #header-extra>
        <copy-to-clipboard-button secondary size="small" :text="citationFull" show-msg />
      </template>
      <template #description>
        <p class="text-small">{{ citationFull }}</p>
      </template>
    </n-thing>
    <n-divider v-if="props.resource.citation" />
    <n-thing v-if="props.resource.citation">
      <template #header>
        <b class="text-small">{{ $t('browse.contentCitation.resOnly') }}</b>
      </template>
      <template #header-extra>
        <copy-to-clipboard-button secondary size="small" :text="citationRes" show-msg />
      </template>
      <template #description>
        <p class="text-small">{{ citationRes }}</p>
      </template>
    </n-thing>
    <n-divider v-if="props.resource.citation" />
    <n-thing>
      <template #header>
        <b class="text-small">{{ $t('browse.contentCitation.urlOnly') }}</b>
      </template>
      <template #header-extra>
        <copy-to-clipboard-button secondary size="small" :text="browseUrl" show-msg />
      </template>
      <template #description>
        <a :href="browseUrl" target="_blank" rel="noreferrer" class="text-small">
          <p>{{ browseUrl }}</p>
        </a>
      </template>
    </n-thing>
  </div>
</template>

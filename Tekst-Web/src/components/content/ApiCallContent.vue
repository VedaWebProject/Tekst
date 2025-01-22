<script setup lang="ts">
import type { ApiCallResourceRead } from '@/api';
import HydratedHtml from '@/components/generic/HydratedHtml.vue';
import { HourglassIcon } from '@/icons';
import { NFlex, NIcon } from 'naive-ui';
import { computed, nextTick, onMounted, ref, watch } from 'vue';

const props = withDefaults(
  defineProps<{
    resource: ApiCallResourceRead;
    reduced?: boolean;
  }>(),
  {
    reduced: false,
  }
);

const fontStyle = {
  fontFamily: props.resource.config.general.font || 'Tekst Content Font',
};

const urls = computed(() => props.resource.contents?.map((c) => c.url));
const html = ref<(string | undefined)[]>([]);
const loading = ref(false);

async function performApiCalls(urls?: string[]) {
  if (!urls?.length) return;
  loading.value = true;
  html.value = Array(urls.length).fill(undefined);
  for (const [i, url] of urls.entries()) {
    if (!url) continue;
    try {
      const resp = await fetch(url);
      html.value[i] = resp.ok ? await resp.text() : undefined;
    } catch (e) {
      html.value[i] = undefined;
      console.log(e);
    }
  }
  loading.value = false;
}

watch(
  urls,
  (newUrls, oldUrls) => {
    if (!newUrls?.length) {
      html.value = [];
      return;
    } else if (JSON.stringify(newUrls) === JSON.stringify(oldUrls)) {
      return;
    } else {
      performApiCalls(newUrls);
    }
  },
  { deep: true }
);

onMounted(() => {
  nextTick().then(() => performApiCalls(urls.value));
});
</script>

<template>
  <div>
    <div v-for="(htmlPart, i) in html" :key="i">
      <template v-if="!reduced">
        <n-flex
          v-if="loading"
          align="center"
          size="small"
          :wrap="false"
          class="translucent text-small"
        >
          <n-icon :component="HourglassIcon" />
          <span>{{ $t('general.loading') }}</span>
        </n-flex>
        <hydrated-html v-else-if="htmlPart !== undefined" :html="htmlPart" :style="fontStyle" />
        <div v-else class="translucent i ui-font">
          {{ $t('errors.notFound') }}
        </div>
      </template>
      <div v-else class="translucent i ui-font">
        {{ $t('contents.msgContentNoReducedView') }}
      </div>
    </div>
  </div>
</template>

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

const reqQueries = computed(() => props.resource.contents?.map((c) => c.query));
const html = ref<(string | undefined)[]>([]);
const loading = ref(false);

function prepareRequest(query: string): Request {
  const cfg = props.resource.config.apiCall;
  if (cfg.method === 'GET') {
    return new Request(`${cfg.endpoint}?${query}`, { method: 'GET' });
  } else {
    return new Request(cfg.endpoint || '', {
      method: cfg.method,
      body: query,
      headers: {
        'Content-Type': cfg.contentType || 'application/json',
      },
    });
  }
}

function execTransformJs(transformFnBody?: string | null, data?: string): string {
  if (!transformFnBody) return data || '';
  return Function(`"use strict"; try { ${transformFnBody} } catch (e) { console.error(e); }`).bind(
    data
  )();
}

async function performApiCalls(queries?: string[]) {
  if (!queries?.length) return;
  loading.value = true;
  html.value = Array(queries.length).fill(undefined);
  for (const [i, q] of queries.entries()) {
    if (!q) continue;
    try {
      const resp = await fetch(prepareRequest(q));
      html.value[i] = resp.ok
        ? execTransformJs(props.resource.config.apiCall.transformJs, await resp.text())
        : undefined;
    } catch (e) {
      html.value[i] = undefined;
      console.log(e);
    }
  }
  loading.value = false;
}

watch(
  reqQueries,
  (newQueries, oldQueries) => {
    if (!newQueries?.length) {
      html.value = [];
      return;
    } else if (JSON.stringify(newQueries) === JSON.stringify(oldQueries)) {
      return;
    } else {
      performApiCalls(newQueries);
    }
  },
  { deep: true }
);

onMounted(() => {
  nextTick().then(() => performApiCalls(reqQueries.value));
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

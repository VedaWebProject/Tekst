<script setup lang="ts">
import type { ApiCallContentRead, ApiCallResourceRead } from '@/api';
import HydratedHtml from '@/components/generic/HydratedHtml.vue';
import { useScriptTag } from '@vueuse/core';
import { computed, nextTick, onMounted, ref, watch } from 'vue';

type ContentData = { query: ApiCallContentRead['query']; extra?: ApiCallContentRead['extra'] };
type TransformationInput = { data: string; extra?: unknown };

const props = defineProps<{
  resource: ApiCallResourceRead;
  reduced?: boolean;
}>();

const fontStyle = {
  fontFamily: props.resource.config.general.font || 'Tekst Content Font',
};

const contents = computed(() =>
  props.resource.contents?.map((c) => ({ query: c.query, extra: c.extra }))
);
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

function execTransformJs(
  transformFnBody?: string | null,
  input: TransformationInput = { data: '' }
): string {
  if (!transformFnBody) return input.data;
  try {
    return Function(
      `"use strict"; try { ${transformFnBody} } catch (e) { console.error(e); }`
    ).bind(input)();
  } catch (e) {
    console.log(e);
    return input.data;
  }
}

async function updateContent(contents?: ContentData[]) {
  if (!contents?.length) return;
  loading.value = true;
  const newHtml = Array(contents.length).fill(undefined);
  for (const [i, content] of contents.entries()) {
    if (!content) continue;
    try {
      const resp = await fetch(prepareRequest(content.query));
      newHtml[i] = resp.ok
        ? execTransformJs(props.resource.config.apiCall.transformJs, {
            data: await resp.text(),
            extra: !!content.extra ? JSON.parse(content.extra) : undefined,
          })
        : undefined;
    } catch (e) {
      newHtml[i] = undefined;
      console.log(e);
    }
  }
  html.value = newHtml;
  loading.value = false;
}

watch(
  contents,
  (newContents, oldContents) => {
    if (!newContents?.length) {
      html.value = [];
      return;
    } else if (JSON.stringify(newContents) === JSON.stringify(oldContents)) {
      return;
    } else {
      updateContent(newContents);
    }
  },
  { deep: true }
);

onMounted(async () => {
  // load transform dependencies (if any)
  for (const depUrl of props.resource.config.apiCall.transformDeps) {
    const { load } = useScriptTag(depUrl, undefined, { manual: true });
    await load(true);
  }
  // load and process contents
  nextTick().then(() => updateContent(contents.value));
});
</script>

<template>
  <div>
    <div v-for="(htmlPart, i) in html" :key="i">
      <template v-if="!reduced">
        <hydrated-html v-if="htmlPart !== undefined" :html="htmlPart" :style="fontStyle" />
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

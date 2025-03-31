<script setup lang="ts">
import type { ApiCallContentRead, ApiCallResourceRead } from '@/api';
import HydratedHtml from '@/components/generic/HydratedHtml.vue';
import { useScriptTag } from '@vueuse/core';
import { computed, nextTick, onMounted, ref, watch } from 'vue';

type ContentData = {
  query: ApiCallContentRead['query'];
  context: ApiCallContentRead['transformContext'];
};
type TransformationInput = { data: string; context?: unknown };

const AsyncFunction = async function () {}.constructor;

const props = defineProps<{
  resource: ApiCallResourceRead;
  focusView?: boolean;
}>();

const fontStyle = {
  fontFamily: props.resource.config.general.font || 'Tekst Content Font',
};

const contents = computed(() =>
  props.resource.contents?.map((c) => ({ query: c.query, context: c.transformContext }))
);
const html = ref<(string | undefined)[]>([]);
const loading = ref(false);

function prepareRequest(query: string): Request {
  const cfg = props.resource.config.special.apiCall;
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

async function execTransformJs(
  transformFnBody?: string | null,
  input: TransformationInput = { data: '' }
): Promise<string> {
  if (!transformFnBody) return input.data;
  try {
    return await AsyncFunction(
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
        ? await execTransformJs(props.resource.config.special.transform.js, {
            data: await resp.text(),
            context: !!content.context ? JSON.parse(content.context) : undefined,
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
  for (const depUrl of props.resource.config.special.transform.deps) {
    const { load } = useScriptTag(depUrl, undefined, { manual: true });
    await load(true);
  }
  // load and process contents
  nextTick().then(() => updateContent(contents.value));
});
</script>

<template>
  <div :dir="resource.config.general.rtl ? 'rtl' : undefined">
    <div v-for="(htmlPart, i) in html" :key="i">
      <template v-if="!focusView">
        <div
          v-if="htmlPart !== undefined"
          class="content-loadable"
          :class="{ 'content-loading': loading }"
          :style="fontStyle"
        >
          <hydrated-html :html="htmlPart" />
        </div>
        <div v-else class="translucent i ui-font">
          {{ $t('errors.notFound') }}
        </div>
      </template>
      <div v-else class="translucent i ui-font text-small">
        {{ $t('contents.msgContentNoFocusView') }}
      </div>
    </div>
  </div>
</template>

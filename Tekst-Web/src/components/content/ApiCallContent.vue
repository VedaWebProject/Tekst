<script setup lang="ts">
import type { ApiCallContentRead, ApiCallResourceRead } from '@/api';
import HydratedHtml from '@/components/generic/HydratedHtml.vue';
import { useScriptTag } from '@vueuse/core';
import { computed, nextTick, onMounted, ref, watch } from 'vue';
import CommonContentDisplay from './CommonContentDisplay.vue';

type ContentData = {
  calls: ApiCallContentRead['calls'];
  transformContext?: ApiCallContentRead['transformContext'];
  authorsComment: ApiCallContentRead['authorsComment'];
  editorsComment: ApiCallContentRead['editorsComment'];
};
type TransformationInput = { key: string; data: string; context?: unknown }[];

const AsyncFunction = async function () {}.constructor;

const props = defineProps<{
  resource: ApiCallResourceRead;
  focusView?: boolean;
  showComments?: boolean;
}>();

const fontStyle = {
  fontFamily: props.resource.config.general.font || 'var(--font-family-content)',
};

const contents = computed(() =>
  props.resource.contents?.map((c) => ({
    calls: c.calls,
    transformContext: c.transformContext,
    authorsComment: c.authorsComment,
    editorsComment: c.editorsComment,
  }))
);
const contentProcessed = ref<{ html?: string; authorsComment?: string; editorsComment?: string }[]>(
  []
);
const loading = ref(false);

function prepareRequest(call: ApiCallContentRead['calls'][number]): Request {
  if (call.method === 'GET') {
    return new Request(`${call.endpoint}?${call.query}`, { method: 'GET' });
  } else {
    return new Request(call.endpoint || '', {
      method: call.method,
      body: call.query,
      headers: {
        'Content-Type': call.contentType || 'application/json',
      },
    });
  }
}

async function execTransformJs(
  input: TransformationInput,
  transformFnBody?: string | null
): Promise<string> {
  if (!transformFnBody) {
    return input.map((input) => input.data).join('\n');
  }
  try {
    return await AsyncFunction(
      `"use strict"; try { ${transformFnBody} } catch (e) { console.error(e); }`
    ).bind(input)();
  } catch (e) {
    console.log(e);
    return input.map((input) => input.data).join('\n');
  }
}

async function updateContent(contents?: ContentData[]) {
  if (!contents?.length) return;
  loading.value = true;
  const newHtml = Array(contents.length).fill(undefined);
  for (const [i, content] of contents.entries()) {
    if (!content) continue;
    try {
      const transformInput: TransformationInput = [];
      for (const call of content.calls) {
        const resp = await fetch(prepareRequest(call));
        if (!resp.ok) {
          console.error(`Error ${resp.status} requesting API data: ${resp.statusText}`);
          continue;
        }
        transformInput.push({
          key: call.key,
          data: await resp.text(),
          context: !!content.transformContext ? JSON.parse(content.transformContext) : undefined,
        });
      }
      newHtml[i] = {
        html: await execTransformJs(transformInput, props.resource.config.special.transform.js),
        authorsComment: content.authorsComment,
        editorsComment: content.editorsComment,
      };
    } catch (e) {
      newHtml[i] = undefined;
      console.log(e);
    }
  }
  contentProcessed.value = newHtml;
  loading.value = false;
}

watch(
  contents,
  (newContents, oldContents) => {
    if (!newContents?.length) {
      contentProcessed.value = [];
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
  <div>
    <common-content-display
      v-for="(content, i) in contentProcessed"
      :key="i"
      :show-comments="showComments"
      :authors-comment="content.authorsComment"
      :editors-comment="content.editorsComment"
      :font="fontStyle.fontFamily"
    >
      <template v-if="!focusView">
        <div
          v-if="content.html !== undefined"
          class="content-loadable"
          :class="{ 'content-loading': loading }"
        >
          <hydrated-html :html="content.html" :style="fontStyle" />
        </div>
        <div v-else class="translucent i font-ui">
          {{ $t('errors.notFound') }}
        </div>
      </template>
      <div v-else class="translucent i font-ui text-small">
        {{ $t('contents.msgContentNoFocusView') }}
      </div>
    </common-content-display>
  </div>
</template>

<script setup lang="ts">
import type { ApiCallContentRead, ApiCallResourceRead } from '@/api';
import HydratedHtml from '@/components/generic/HydratedHtml.vue';
import { useScriptTag } from '@vueuse/core';
import { NSpin } from 'naive-ui';
import { nextTick, onMounted, ref, watch } from 'vue';
import CommonContentDisplay from './CommonContentDisplay.vue';

type ResponseData = { key: string; data: string }[];

const AsyncFunction = async function () {}.constructor;

const props = defineProps<{
  resource: ApiCallResourceRead;
  focusView?: boolean;
  showComments?: boolean;
}>();

const fontStyle = {
  fontFamily: props.resource.config.general.font || 'var(--font-family-content)',
};

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
  respData: ResponseData,
  transformContext?: unknown,
  transformFnBody?: string | null
): Promise<string> {
  if (!transformFnBody) {
    return respData.map((rd) => rd.data).join('\n');
  }
  try {
    return await AsyncFunction(
      `"use strict"; try { ${transformFnBody} } catch (e) { console.error(e); }`
    ).bind({ data: respData, context: transformContext })();
  } catch (e) {
    console.log(e);
    return respData.map((rd) => rd.data).join('\n');
  }
}

async function updateContent(contents?: ApiCallContentRead[]) {
  if (!contents?.length) return;
  loading.value = true;
  const newHtml = Array(contents.length).fill(undefined);
  for (const [i, content] of contents.entries()) {
    if (!content) continue;
    try {
      const transformInput: ResponseData = [];
      for (const call of content.calls) {
        const resp = await fetch(prepareRequest(call));
        if (!resp.ok) {
          console.error(`Error ${resp.status} requesting API data: ${resp.statusText}`);
          continue;
        }
        transformInput.push({
          key: call.key,
          data: await resp.text(),
        });
      }
      newHtml[i] = {
        html: await execTransformJs(
          transformInput,
          !!content.transformContext ? JSON.parse(content.transformContext) : undefined,
          props.resource.config.special.transform.js
        ),
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
  () => props.resource.contents?.map((c) => c.id).join('-'),
  (contentIds) => {
    if (!contentIds) {
      contentProcessed.value = [];
    } else {
      updateContent(props.resource.contents);
    }
  }
);

onMounted(async () => {
  // load transform dependencies (if any)
  for (const depUrl of props.resource.config.special.transform.deps) {
    const { load } = useScriptTag(depUrl, undefined, { manual: true });
    await load(true);
  }
  // load and process contents
  nextTick().then(() => updateContent(props.resource.contents));
});
</script>

<template>
  <div>
    <common-content-display
      v-for="(content, i) in contentProcessed"
      :key="i"
      :show-comments="showComments"
      :authors-comment="content?.authorsComment"
      :editors-comment="content?.editorsComment"
      :font="fontStyle.fontFamily"
    >
      <n-spin v-if="!focusView" :show="loading" size="small">
        <div
          v-if="content?.html !== undefined"
          :class="`content-loadable res-${resource.id}` + (loading ? ' content-loading' : '')"
        >
          <hydrated-html
            :html="content?.html"
            :style="fontStyle"
            :node-class="`res-${resource.id}`"
          />
        </div>
        <div v-else class="translucent i font-ui">
          {{ $t('errors.notFound') }}
        </div>
      </n-spin>
      <div v-else class="translucent i font-ui text-small">
        {{ $t('contents.msgContentNoFocusView') }}
      </div>
    </common-content-display>
  </div>
</template>

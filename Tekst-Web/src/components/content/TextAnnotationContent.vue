<script setup lang="ts">
import type { TextAnnotationContentRead, TextAnnotationResourceRead } from '@/api';
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    resource: TextAnnotationResourceRead;
    reduced?: boolean;
  }>(),
  {
    reduced: false,
  }
);

const contents = computed(() =>
  props.resource.contents?.map((c) => ({
    ...c,
    tokens: c.tokens.map((t) => ({
      token: t.token,
      annotations: applyAnnotationDisplayTemplate(t.annotations),
    })),
  }))
);

const fontStyle = {
  fontFamily: props.resource.config?.general?.font || 'Tekst Content Font',
};

function applyAnnotationDisplayTemplate(
  annotations: TextAnnotationContentRead['tokens'][number]['annotations']
): string {
  const templ = props.resource.config?.displayTemplate || '${k}:${v}';
  const delim = props.resource.config?.displayDelimiter || '; ';
  return annotations
    .map((a) => templ.replace(/\$\{k\}/g, a.key).replace(/\$\{v\}/g, a.value))
    .join(delim);
}
</script>

<template>
  <div v-for="content in contents" :key="content.id" class="content-container">
    <div v-for="(token, tokenIndex) in content.tokens" :key="tokenIndex" class="token-container">
      <div class="token b i" :style="fontStyle">
        {{ token.token }}
      </div>
      <div class="annotation">
        {{ token.annotations }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.content-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.content-container:not(:last-child) {
  margin-bottom: var(--layout-gap);
}

.token-container {
  display: flex;
  flex-direction: column;
  flex-wrap: nowrap;
}

.token {
  line-height: 1.5em;
}

.annotation {
  font-size: var(--font-size-small);
}
</style>

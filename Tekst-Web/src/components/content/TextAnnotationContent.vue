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
  <div v-for="content in contents" :key="content.id" class="annotation-container">
    <div v-for="(token, tokenIndex) in content.tokens" :key="tokenIndex">
      <div :style="fontStyle">
        {{ token.token }}
      </div>
      <div v-for="(annotation, annotationIndex) in token.annotations" :key="annotationIndex">
        {{ annotation }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.plain-text-content {
  white-space: pre-wrap;
  margin-top: var(--content-gap);
}
.plain-text-content:first-child {
  margin-top: inherit;
}
</style>

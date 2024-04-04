<script setup lang="ts">
import type { TextAnnotationContentRead, TextAnnotationResourceRead } from '@/api';
import { computed } from 'vue';

interface AnnotationDisplayTemplate {
  key?: string;
  prefix?: string;
  content?: string;
  suffix?: string;
  bold?: boolean;
  italic?: boolean;
  caps?: boolean;
}

interface AnnotationDisplayStructure {
  display: string;
  bold?: boolean;
  italic?: boolean;
  caps?: boolean;
}

const PAT_TMPL_ITEM = /{{((?!}}).+?)}}/g;
const PAT_TMPL_ITEM_PARTS = /_([kpcsf]):(.*?)(?=_[kpcsf]:|$)/g;

const props = withDefaults(
  defineProps<{
    resource: TextAnnotationResourceRead;
    reduced?: boolean;
  }>(),
  {
    reduced: false,
  }
);

const annotationDisplayTemplates = computed<AnnotationDisplayTemplate[]>(() => {
  if (!props.resource.config?.displayTemplate) return [];
  const out: AnnotationDisplayTemplate[] = [];
  // iterate over template items
  const items = [...props.resource.config.displayTemplate.matchAll(PAT_TMPL_ITEM)];
  items.forEach((a, i) => {
    const item: AnnotationDisplayTemplate = {};
    // iterate over template item parts
    [...a[1].matchAll(PAT_TMPL_ITEM_PARTS)].forEach((p) => {
      switch (p[1]) {
        case 'k':
          item.key = p[2];
          break;
        case 'p':
          item.prefix = p[2];
          break;
        case 'c':
          item.content = p[2];
          break;
        case 's':
          item.suffix = p[2];
          break;
        case 'f':
          item.bold = p[2].toLowerCase().includes('b');
          item.italic = p[2].toLowerCase().includes('i');
          item.caps = p[2].toLowerCase().includes('c');
      }
    });
    // remove prefix/suffix if item is first/last
    if (i === 0) {
      item.prefix = undefined;
    } else if (i === items.length - 1) {
      item.suffix = undefined;
    }
    out.push(item);
  });
  return out;
});

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
): AnnotationDisplayStructure[] {
  return annotationDisplayTemplates.value.map((t) => {
    const a = annotations.find((a) => a.key === t.key);
    const c = t.content?.replace(/k/g, a?.key || '').replace(/v/g, a?.value || '');
    return {
      display: `${t.prefix || ''}${c || ''}${t.suffix || ''}`,
      bold: t.bold,
      italic: t.italic,
      caps: t.caps,
    };
  });
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

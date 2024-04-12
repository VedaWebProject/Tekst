<script setup lang="ts">
import type { TextAnnotationContentRead, TextAnnotationResourceRead } from '@/api';
import type { CSSProperties } from 'vue';
import { computed } from 'vue';

interface AnnotationDisplayFormatFlags {
  bold?: boolean;
  italic?: boolean;
  caps?: boolean;
  font?: boolean; // whether to use the resource's font / content font
}

interface AnnotationDisplayTemplate {
  key?: string;
  prefix?: string;
  content?: string;
  suffix?: string;
  format?: AnnotationDisplayFormatFlags;
}

interface AnnotationDisplayStructure {
  display: string;
  format?: AnnotationDisplayFormatFlags;
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
  items.forEach((a) => {
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
          item.format = {
            bold: p[2].toLowerCase().includes('b'),
            italic: p[2].toLowerCase().includes('i'),
            caps: p[2].toLowerCase().includes('c'),
            font: p[2].toLowerCase().includes('f'),
          };
      }
    });
    out.push(item);
  });
  return out;
});

const contents = computed(() =>
  props.resource.contents?.map((c) => ({
    ...c,
    tokens: c.tokens.map((t) => ({
      token: t.token,
      lb: t.lb,
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
  // if there are no annotation display templates, just return the annotations in a
  // default form (k:v, k:v, etc.) without any styling flags set
  if (!annotationDisplayTemplates.value.length) {
    return (
      annotations?.map((a, i) => ({
        display: `${a.key}:${a.value}` + (i < annotations.length - 1 ? '; ' : ''),
      })) || []
    );
  }

  // associate templates with annotations data
  const items = annotationDisplayTemplates.value
    .map((template) => {
      return {
        template,
        data: annotations?.find((a) => a.key === template.key),
      };
    })
    .filter((item) => item.template.content && (item.template.key ? !!item.data : true));

  // apply templates, compute content
  return items.map((item, i) => {
    const content =
      item.template.content
        ?.replace(/k/g, item.data?.key || '')
        .replace(/v/g, item.data?.value || '') || '';
    const prefix = i > 0 ? item.template.prefix || '' : '';
    const suffix = i < items.length - 1 ? item.template.suffix || '' : '';
    return {
      display: `${prefix}${content}${suffix}`,
      format: item.template.format,
    };
  });
}

function getAnnotationStyle(fmtFlags?: AnnotationDisplayFormatFlags): CSSProperties | undefined {
  if (!fmtFlags) return;
  return {
    fontWeight: fmtFlags.bold ? 'bold' : undefined,
    fontStyle: fmtFlags.italic ? 'italic' : undefined,
    fontVariant: fmtFlags.caps ? 'small-caps' : undefined,
    fontFamily: fmtFlags.font ? fontStyle.fontFamily : undefined,
  };
}
</script>

<template>
  <div v-for="content in contents" :key="content.id" class="content-container" :class="{ reduced }">
    <template v-for="(token, tokenIndex) in content.tokens" :key="tokenIndex">
      <div class="token-container">
        <div class="token b i" :style="fontStyle">
          {{ token.token }}
        </div>
        <div class="annotations">
          <span
            v-for="(annotation, index) in token.annotations"
            :key="index"
            :style="getAnnotationStyle(annotation.format)"
          >
            {{ annotation.display }}
          </span>
        </div>
      </div>
      <hr v-if="token.lb" class="token-lb" />
    </template>
  </div>
</template>

<style scoped>
.content-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.content-container:not(:last-child) {
  padding-bottom: 1rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid var(--main-bg-color);
}

.reduced .content-container {
  column-gap: 6px;
}

.token-container {
  display: flex;
  flex-direction: column;
  flex-wrap: nowrap;
  border-left: 1px solid var(--main-bg-color);
  padding-left: 8px;
}

.reduced .token-container {
  padding-left: 4px;
}

.token-lb {
  width: 100%;
  border: none;
  height: 0px;
  margin: 4px 0;
}

.reduced .token-lb {
  display: none;
}

.annotations {
  font-size: var(--font-size-small);
}

.reduced .annotations {
  font-size: var(--font-size-tiny);
  opacity: 0.75;
}
</style>

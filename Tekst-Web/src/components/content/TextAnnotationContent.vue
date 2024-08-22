<script setup lang="ts">
import type { TextAnnotationContentRead, TextAnnotationResourceRead } from '@/api';
import type { CSSProperties } from 'vue';
import { computed, ref } from 'vue';
import { MetadataIcon } from '@/icons';
import { NTable, NAlert } from 'naive-ui';
import GenericModal from '@/components/generic/GenericModal.vue';

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

const showDetailsModal = ref(false);
const tokenDetailsData = ref<TextAnnotationContentRead['tokens'][number]>();
const tokenDetailsComment = computed(() =>
  tokenDetailsData.value?.annotations?.find((a) => a.key === 'comment')?.value.join('\n')
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
      annotations: t.annotations,
      annotationsDisplay: applyAnnotationDisplayTemplate(t.annotations),
      comment: t.annotations?.find((a) => a.key === 'comment')?.value,
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
        .replace(
          /v/g,
          item.data?.value.join(props.resource.config?.multiValueDelimiter || '/') || ''
        ) || '';
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

function handleTokenClick(token: TextAnnotationContentRead['tokens'][number]) {
  if (!token.annotations?.length) return;
  tokenDetailsData.value = token;
  showDetailsModal.value = true;
}
</script>

<template>
  <div v-for="content in contents" :key="content.id" class="content-container" :class="{ reduced }">
    <template v-for="(token, tokenIndex) in content.tokens" :key="tokenIndex">
      <div
        class="token-container"
        :class="{
          'token-with-annos': !!token.annotations?.length,
          'token-with-comment': !!token.annotations?.find((a) => a.key === 'comment'),
        }"
        :title="token.comment?.join(' ') || undefined"
        @click="handleTokenClick(token)"
      >
        <div class="token b i" :style="fontStyle">
          {{ token.token }}
        </div>
        <div class="annotations">
          <span
            v-for="(annotationDisplay, index) in token.annotationsDisplay"
            :key="index"
            :style="getAnnotationStyle(annotationDisplay.format)"
          >
            {{ annotationDisplay.display }}
          </span>
        </div>
      </div>
      <hr v-if="token.lb" class="token-lb" />
    </template>
  </div>

  <generic-modal
    v-model:show="showDetailsModal"
    :title="tokenDetailsData?.token"
    :icon="MetadataIcon"
    heading-level="3"
    :header-style="{
      'font-family': resource.config?.general?.font || 'Tekst Content Font',
      'font-style': 'italic',
    }"
    @after-leave="() => (tokenDetailsData = undefined)"
  >
    <n-alert
      v-if="tokenDetailsComment"
      type="default"
      :show-icon="false"
      :title="$t('general.comment')"
      class="mb-lg"
    >
      <div style="white-space: pre-line">
        {{ tokenDetailsComment }}
      </div>
    </n-alert>
    <n-table :bordered="false" :bottom-bordered="false" size="small">
      <thead>
        <tr>
          <th>{{ $t('resources.types.textAnnotation.contentFields.annotationKey') }}</th>
          <th>{{ $t('resources.types.textAnnotation.contentFields.annotationValue') }}</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="(annotation, index) in tokenDetailsData?.annotations" :key="index">
          <tr v-if="annotation.key !== 'comment'">
            <td>{{ annotation.key }}</td>
            <td class="content-font">
              {{ annotation.value.join(resource.config?.multiValueDelimiter || '/') }}
            </td>
          </tr>
        </template>
      </tbody>
    </n-table>
  </generic-modal>
</template>

<style scoped>
.content-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0px;
}

.content-container:not(:last-child) {
  padding-bottom: var(--gap-lg);
  margin-bottom: var(--gap-lg);
  border-bottom: 1px solid var(--main-bg-color);
}

.reduced .content-container {
  column-gap: 6px;
}

.token-container {
  position: relative;
  display: flex;
  flex-direction: column;
  flex-wrap: nowrap;
  border-left: 1px solid var(--main-bg-color);
  padding: 0 8px;
}

.token-container.token-with-annos {
  cursor: pointer;
  transition: background-color 0.2s;
  background: linear-gradient(135deg, var(--main-bg-color) 5px, transparent 0);
}

.token-container.token-with-annos:hover {
  background-color: var(--accent-color-fade5);
}

.token-container.token-with-comment {
  background: linear-gradient(135deg, var(--accent-color-fade3) 5px, transparent 0);
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

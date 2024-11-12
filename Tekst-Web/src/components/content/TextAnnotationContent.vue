<script setup lang="ts">
import type { TextAnnotationContentRead, TextAnnotationResourceRead } from '@/api';
import type { CSSProperties } from 'vue';
import { computed, nextTick, ref } from 'vue';
import { CheckIcon, ClearIcon, CopyIcon, MetadataIcon } from '@/icons';
import { NTable, NAlert, NDropdown, NButton, NFlex, NIcon } from 'naive-ui';
import GenericModal from '@/components/generic/GenericModal.vue';
import { $t } from '@/i18n';
import { useClipboard } from '@vueuse/core';
import { pickTranslation, renderIcon } from '@/utils';
import { useStateStore } from '@/stores';

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
  group?: string;
  break?: boolean; // line break after this template
}

interface AnnotationDisplay {
  content: string;
  style?: CSSProperties;
  group?: string;
  break?: boolean;
}

interface TokenDetails {
  token: string;
  comment?: string;
  annotations?: TextAnnotationContentRead['tokens'][number]['annotations'];
}

type Token = TextAnnotationContentRead['tokens'][number];

const PAT_TMPL_ITEM = /{{((?!}}).+?)}}/g;
const PAT_TMPL_ITEM_PARTS = /_([kpcsfgb]):(.*?)(?=_[kpcsfgb]:|$)/g;

const props = withDefaults(
  defineProps<{
    resource: TextAnnotationResourceRead;
    reduced?: boolean;
  }>(),
  {
    reduced: false,
  }
);

const state = useStateStore();

const showDetailsModal = ref(false);
const tokenDetails = ref<TokenDetails>();

const annotationGroups = computed(() => props.resource.config.annotationGroups);
const activeAnnoGroups = ref(props.resource.config.annotationGroups.map((g) => g.key));

const showTokenContextMenu = ref(false);
const tokenContextMenuPos = ref({ x: 0, y: 0 });
const tokenContextIndex = ref<string>();
const tokenCopyContent = ref<string>('');
const {
  copy: copyTokenContent,
  copied: tokenContentCopied,
  isSupported: isClipboardSupported,
} = useClipboard({ source: tokenCopyContent, copiedDuring: 500 });

const tokenContextMenuOptions = computed(() => [
  {
    label: () => $t('resources.types.textAnnotation.copyTokenAction'),
    key: 'copyToken',
    disabled: !isClipboardSupported.value,
    icon: renderIcon(CopyIcon),
  },
  {
    label: () => $t('resources.types.textAnnotation.copyFullAction'),
    key: 'copyFull',
    disabled: !isClipboardSupported.value,
    icon: renderIcon(CopyIcon),
  },
]);

const annotationDisplayTemplates = computed<AnnotationDisplayTemplate[]>(() => {
  if (!props.resource.config.displayTemplate) return [];
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
          break;
        case 'g':
          item.group = p[2];
          break;
        case 'b':
          item.break = true;
          break;
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
      comment: t.annotations.find((a) => a.key === 'comment')?.value,
    })),
  }))
);

const fontStyle = {
  fontFamily: props.resource.config.general.font || 'Tekst Content Font',
};

function applyAnnotationDisplayTemplate(annotations: Token['annotations']): AnnotationDisplay[] {
  // if there are no annotation display templates, just return the annotations in a
  // default form (k:v, k:v, etc.) without any styling flags set
  if (!annotationDisplayTemplates.value.length) {
    return (
      annotations?.map((a, i) => ({
        content: `${a.key}:${a.value}` + (i < annotations.length - 1 ? '; ' : ''),
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
      item.template.content?.replace(/k/g, item.data?.key || '').replace(
        /v/g,
        item.data?.value
          // join the values with the delimiter set in the resource config
          .join(props.resource.config.multiValueDelimiter || '/') || ''
      ) || '';
    const prefix = i > 0 ? item.template.prefix || '' : '';
    const suffix = i < items.length - 1 ? item.template.suffix || '' : '';
    return {
      content: `${prefix}${content}${suffix}`,
      style: getAnnotationStyle(item.template.format),
      group: item.template.group,
      break: item.template.break,
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

function handleTokenClick(token: Token) {
  if (!token.annotations.length) return;
  const annos = token.annotations.filter((a) => a.key !== 'comment');
  tokenDetails.value = {
    token: token.token,
    comment: token.annotations.find((a) => a.key === 'comment')?.value.join('\n'),
    annotations: annos.length ? annos : undefined,
  };
  showDetailsModal.value = true;
}

function handleTokenRightClick(e: MouseEvent, token: Token, tokenId: string) {
  showTokenContextMenu.value = false;
  if (!isClipboardSupported.value) return;
  tokenDetails.value = token;
  tokenContextIndex.value = tokenId;
  nextTick().then(() => {
    tokenContextMenuPos.value = { x: e.clientX, y: e.clientY };
    showTokenContextMenu.value = true;
  });
}

function handleTokenContextMenuClickOutside() {
  showTokenContextMenu.value = false;
}

function handleTokenContextMenuSelect(key: string | number) {
  showTokenContextMenu.value = false;
  if (key === 'copyToken') {
    tokenCopyContent.value = tokenDetails.value?.token || '';
  } else if (key === 'copyFull') {
    const token = tokenDetails.value?.token ? tokenDetails.value.token : '';
    const annos = tokenDetails.value?.annotations
      ? tokenDetails.value.annotations
          .map((a) => `${a.key}: ${a.value.join(props.resource.config.multiValueDelimiter)}`)
          .join('; ')
      : [];
    tokenCopyContent.value = token + (annos ? ` (${annos})` : '');
  }
  copyTokenContent(tokenCopyContent.value);
  tokenCopyContent.value = '';
}

function toggleAnnoGroup(key: string) {
  if (activeAnnoGroups.value.includes(key)) {
    activeAnnoGroups.value = activeAnnoGroups.value.filter((g) => g !== key);
  } else {
    activeAnnoGroups.value = [...activeAnnoGroups.value, key];
  }
}
</script>

<template>
  <!-- ANNOTATION GROUP TOGGLES -->
  <n-flex v-if="!!annotationGroups.length" class="mb-lg">
    <n-button
      tertiary
      v-for="group in annotationGroups"
      :key="group.key"
      size="tiny"
      :focusable="false"
      :disabled="activeAnnoGroups.includes(group.key) && activeAnnoGroups.length <= 1"
      @click="toggleAnnoGroup(group.key)"
    >
      <template #icon>
        <n-icon :component="activeAnnoGroups.includes(group.key) ? CheckIcon : ClearIcon" />
      </template>
      {{ pickTranslation(group.translations, state.locale) }}
    </n-button>
  </n-flex>

  <!-- CONTENT -->
  <div
    v-for="(content, contentIndex) in contents"
    :key="content.id"
    class="content-container"
    :class="{ reduced }"
  >
    <template v-for="(token, tokenIndex) in content.tokens" :key="tokenIndex">
      <div
        class="token-container"
        :class="{
          'token-with-annos': !!token.annotations.length,
          'token-with-comment': !!token.annotations.find((a) => a.key === 'comment'),
          'token-content-copied':
            tokenContentCopied && tokenContextIndex === `${contentIndex}-${tokenIndex}`,
        }"
        :title="$t('resources.types.textAnnotation.copyHintTip')"
        @click="handleTokenClick(token)"
        @contextmenu.prevent.stop="
          (e) => handleTokenRightClick(e, token, `${contentIndex}-${tokenIndex}`)
        "
      >
        <div class="token b i" :style="fontStyle">
          {{ token.token }}
        </div>
        <div class="annotations">
          <template v-for="(anno, index) in token.annotationsDisplay" :key="index">
            <template
              v-if="
                !anno.group ||
                !resource.config.annotationGroups.length ||
                activeAnnoGroups.includes(anno.group)
              "
            >
              <span :style="anno.style">{{ anno.content }}</span>
              <br v-if="anno.break" />
            </template>
          </template>
        </div>
      </div>
      <hr v-if="token.lb" class="token-lb" />
    </template>
  </div>

  <generic-modal
    v-model:show="showDetailsModal"
    :title="tokenDetails?.token"
    :icon="MetadataIcon"
    heading-level="3"
    :header-style="{
      'font-family': resource.config.general.font || 'Tekst Content Font',
      'font-style': 'italic',
    }"
    @after-leave="() => (tokenDetails = undefined)"
  >
    <n-alert
      v-if="tokenDetails?.comment"
      type="default"
      :show-icon="false"
      :title="$t('general.comment')"
      class="mb-lg"
    >
      <div class="content-font text-small" style="white-space: pre-line">
        {{ tokenDetails.comment }}
      </div>
    </n-alert>
    <n-table
      v-if="tokenDetails?.annotations"
      :bordered="false"
      :bottom-bordered="false"
      size="small"
    >
      <thead>
        <tr>
          <th>{{ $t('resources.types.textAnnotation.contentFields.annotationKey') }}</th>
          <th>{{ $t('general.value') }}</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="(annotation, index) in tokenDetails.annotations" :key="index">
          <tr v-if="annotation.key !== 'comment'">
            <td>{{ annotation.key }}</td>
            <td class="content-font">
              {{ annotation.value.join(resource.config.multiValueDelimiter || '/') }}
            </td>
          </tr>
        </template>
      </tbody>
    </n-table>
  </generic-modal>

  <n-dropdown
    placement="bottom-start"
    trigger="manual"
    :x="tokenContextMenuPos.x"
    :y="tokenContextMenuPos.y"
    :options="tokenContextMenuOptions"
    :show="showTokenContextMenu"
    :on-clickoutside="handleTokenContextMenuClickOutside"
    @select="handleTokenContextMenuSelect"
  />
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
  outline-color: transparent;
  transition: outline-color 0.3s ease-in-out;
}

.token-container.token-with-annos {
  cursor: pointer;
  background: linear-gradient(135deg, var(--main-bg-color) 5px, transparent 0);
}

.token-container.token-with-annos:hover {
  background-color: var(--accent-color-fade5);
}

.token-container.token-with-comment {
  background: linear-gradient(135deg, var(--accent-color-fade3) 5px, transparent 0);
}

.token-container.token-content-copied {
  outline: 2px dashed var(--accent-color-fade2);
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
  line-height: 1.4em;
  font-size: var(--font-size-small);
}

.reduced .annotations {
  font-size: var(--font-size-tiny);
  opacity: 0.75;
}
</style>

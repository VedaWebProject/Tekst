<script setup lang="ts">
import type { TextAnnotationContentRead, TextAnnotationResourceRead } from '@/api';
import GenericModal from '@/components/generic/GenericModal.vue';
import { $t } from '@/i18n';
import { CheckIcon, ClearIcon, ColorIcon, ColorOffIcon, CopyIcon, MetadataIcon } from '@/icons';
import { useStateStore, useThemeStore } from '@/stores';
import { pickTranslation, renderIcon } from '@/utils';
import { useClipboard } from '@vueuse/core';
import { adjustHue, saturate, toRgba, transparentize } from 'color2k';
import { NAlert, NButton, NDropdown, NFlex, NIcon, NTable } from 'naive-ui';
import type { CSSProperties } from 'vue';
import { computed, nextTick, ref } from 'vue';

interface AnnotationDisplayFormatFlags {
  bold?: boolean;
  italic?: boolean;
  caps?: boolean;
  font?: boolean; // whether to use the resource's font / content font
}

interface AnnotationDisplayTemplate {
  type: 'anno' | 'br';
  key?: string;
  prefix?: string;
  content?: string;
  suffix?: string;
  format?: AnnotationDisplayFormatFlags;
  group?: string;
}

interface AnnotationDisplay {
  content?: string;
  style?: CSSProperties;
  group?: string;
}

interface TokenDetails {
  token: string;
  comment?: string;
  annotations?: TextAnnotationContentRead['tokens'][number]['annotations'];
}

type Token = TextAnnotationContentRead['tokens'][number];

const PAT_TMPL_ITEM = /{{((?!}}).+?)}}/g;
const PAT_TMPL_ITEM_PARTS = /_([kpcsfg]):(.*?)(?=_[kpcsfg]:|$)/g;
const PAT_TMPL_LINE_BREAK = /^br$/g;

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
const theme = useThemeStore();

const showDetailsModal = ref(false);
const tokenDetails = ref<TokenDetails>();

const annoGroups = computed(() => props.resource.config.annotationGroups);
const activeAnnoGroups = ref(props.resource.config.annotationGroups.map((g) => g.key));
const groupColors = computed<Record<string, string>>(() =>
  Object.fromEntries(
    annoGroups.value.map((g, i) => [
      g.key,
      toRgba(
        transparentize(
          saturate(
            adjustHue(
              theme.accentColors.base,
              (360 / (annoLineNumbers.value.length + 1)) * (i + 1)
            ),
            1
          ),
          theme.darkMode ? 0.8 : 0.9
        )
      ),
    ])
  )
);

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

const fontFamilyStyle = computed(() => ({
  fontFamily: props.resource.config.general.font || 'Tekst Content Font',
}));

const annoLineNumbers = computed(() =>
  Array.from(Array(displayTemplates.value.filter((tmpl) => tmpl.type === 'br').length + 1).keys())
);
const colorAnnoLines = ref(false);

const displayTemplates = computed<AnnotationDisplayTemplate[]>(() => {
  if (!props.resource.config.displayTemplate) return [];
  const out: AnnotationDisplayTemplate[] = [];
  // iterate over template items
  const items = [...props.resource.config.displayTemplate.matchAll(PAT_TMPL_ITEM)];
  items.forEach((a) => {
    const item: AnnotationDisplayTemplate = {
      // check if template item is a line break marker
      type: a[1].match(PAT_TMPL_LINE_BREAK) ? 'br' : 'anno',
    };
    if (item.type !== 'br') {
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
        }
      });
    }
    out.push(item);
  });
  return out;
});

function applyDisplayTemplate(tokens: Token[]): AnnotationDisplay[][][] {
  const lineDisplaysPerToken = tokens.map((t) => {
    // if there are no annotation display templates, just return the annotations in a
    // default form (k:v, k:v, etc.) without any styling flags set, in a single line (array)
    if (!displayTemplates.value.length) {
      return [
        t.annotations?.map(
          (a, i) =>
            ({
              type: 'anno',
              content: `${a.key}:${a.value}` + (i < t.annotations.length - 1 ? '; ' : ''),
            }) as AnnotationDisplay
        ) || [],
      ];
    }

    // prepare templates for next step
    const annos = displayTemplates.value
      // associate templates with annotations data
      .map((template) => {
        return {
          template,
          data: t.annotations?.find((a) => a.key === template.key),
        };
      })
      // filter to keep only templates that are either line break markers or annotations
      // that have `content` AND do carry data for `key` (if they have one)
      .filter(
        (item) =>
          item.template.type === 'br' ||
          (item.template.content && (!item.template.key || !!item.data))
      );

    // apply templates, compose final display content
    const lines: AnnotationDisplay[][] = [[]];
    annos.forEach((anno, i) => {
      // if the current template is a line break marker, add an empty line
      if (anno.template.type === 'br') {
        lines.push([]);
        return;
      }
      // compose the content, prefix and suffix from the template and the data
      const content =
        anno.template.content?.replace(/k/g, anno.data?.key || '').replace(
          /v/g,
          anno.data?.value
            // join the values with the delimiter set in the resource config
            .join(props.resource.config.multiValueDelimiter || '/') || ''
        ) || '';
      const prefix = i > 0 ? anno.template.prefix || '' : '';
      const suffix = i < annos.length - 1 ? anno.template.suffix || '' : '';
      lines[lines.length - 1].push({
        content: `${prefix}${content}${suffix}`,
        style: getAnnotationStyle(anno.template.format),
        group: anno.template.group,
      });
    });
    return lines;
  });

  return lineDisplaysPerToken;
}

const contents = computed(() => {
  const out =
    props.resource.contents?.map((c) => {
      const displays = applyDisplayTemplate(c.tokens);
      return {
        ...c,
        tokens: c.tokens.map((t, i) => ({
          token: t.token,
          lb: t.lb,
          annotations: t.annotations,
          annoDisplay: displays[i],
          comment: t.annotations.find((a) => a.key === 'comment')?.value,
        })),
      };
    }) || [];

  // find lines that are empty in every annotation display of every content
  // (either because they have no content or the annotation group is not active)
  const emptyLines: boolean[] = annoLineNumbers.value.map(
    (ln) =>
      !out
        .map((c) => c.tokens)
        .flat()
        .map((t) =>
          t.annoDisplay[ln].filter(
            (anno) =>
              !anno.group || activeAnnoGroups.value.includes(anno.group) || !annoGroups.value.length
          )
        )
        .some((line) => !!line.length)
  );

  // return contents with empty lines removed from their tokens' annotation displays
  return out.map((c) => ({
    ...c,
    tokens: c.tokens.map((t) => ({
      ...t,
      annoDisplay: t.annoDisplay.filter((_, ln) => !emptyLines[ln]),
    })),
  }));
});

function getAnnotationStyle(fmtFlags?: AnnotationDisplayFormatFlags): CSSProperties | undefined {
  if (!fmtFlags) return;
  return {
    fontWeight: fmtFlags.bold ? 'bold' : undefined,
    fontStyle: fmtFlags.italic ? 'italic' : undefined,
    fontVariant: fmtFlags.caps ? 'small-caps' : undefined,
    fontFamily: fmtFlags.font ? fontFamilyStyle.value.fontFamily : undefined,
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
    const delim = props.resource.config.multiValueDelimiter;
    const annos = tokenDetails.value?.annotations
      ? tokenDetails.value.annotations.map((a) => `${a.key}: ${a.value.join(delim)}`).join('; ')
      : [];
    tokenCopyContent.value = token + (annos ? ` (${annos})` : '');
  }
  copyTokenContent(tokenCopyContent.value);
  tokenCopyContent.value = '';
}

function toggleAnnoGroup(key: string) {
  if (activeAnnoGroups.value.includes(key) && activeAnnoGroups.value.length <= 1) {
    activeAnnoGroups.value = annoGroups.value.map((g) => g.key);
  } else if (activeAnnoGroups.value.includes(key)) {
    activeAnnoGroups.value = activeAnnoGroups.value.filter((g) => g !== key);
  } else {
    activeAnnoGroups.value = [...activeAnnoGroups.value, key];
  }
}
</script>

<template>
  <!-- ANNOTATION GROUP TOGGLES -->
  <n-flex v-if="!!annoGroups.length" class="mb-lg">
    <n-button
      :tertiary="!colorAnnoLines"
      :type="colorAnnoLines ? 'primary' : undefined"
      v-for="group in annoGroups"
      :key="group.key"
      size="tiny"
      :focusable="false"
      :disabled="annoGroups.length == 1"
      :color="colorAnnoLines ? groupColors[group.key] : undefined"
      :text-color="colorAnnoLines ? theme.theme.common.textColor1 : undefined"
      @click="toggleAnnoGroup(group.key)"
    >
      <template #icon>
        <n-icon :component="activeAnnoGroups.includes(group.key) ? CheckIcon : ClearIcon" />
      </template>
      {{ pickTranslation(group.translations, state.locale) }}
    </n-button>
    <n-button tertiary size="tiny" :focusable="false" @click="colorAnnoLines = !colorAnnoLines">
      <template #icon>
        <n-icon :component="colorAnnoLines ? ColorOffIcon : ColorIcon" />
      </template>
    </n-button>
  </n-flex>

  <!-- CONTENT -->
  <div v-for="(c, cIndex) in contents" :key="c.id" class="content-container" :class="{ reduced }">
    <template v-for="(t, tIndex) in c.tokens" :key="tIndex">
      <div
        class="token-container"
        :class="{
          'token-with-annos': !!t.annotations.length,
          'token-with-comment': !!t.annotations.find((a) => a.key === 'comment'),
          'token-content-copied': tokenContentCopied && tokenContextIndex === `${cIndex}-${tIndex}`,
        }"
        :title="$t('resources.types.textAnnotation.copyHintTip')"
        @click="handleTokenClick(t)"
        @contextmenu.prevent.stop="(e) => handleTokenRightClick(e, t, `${cIndex}-${tIndex}`)"
      >
        <div class="token b i" :style="fontFamilyStyle">
          {{ t.token }}
        </div>
        <div class="annotations">
          <div
            v-for="(annoLine, lineIndex) in t.annoDisplay"
            :key="lineIndex"
            class="annotation-line"
          >
            <template v-for="(anno, annoIndex) in annoLine" :key="annoIndex">
              <span
                v-if="
                  !anno.group ||
                  !resource.config.annotationGroups.length ||
                  activeAnnoGroups.includes(anno.group)
                "
                :style="{
                  ...anno.style,
                  transition: 'background-color 0.2s ease',
                  backgroundColor:
                    colorAnnoLines && !!anno.group ? groupColors[anno.group] : undefined,
                }"
              >
                {{ anno.content }}
              </span>
            </template>
          </div>
        </div>
      </div>
      <hr v-if="t.lb" class="token-lb" />
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
  margin-right: 4px;
  position: relative;
  display: flex;
  flex-direction: column;
  flex-wrap: nowrap;
  border-left: 2px dashed var(--main-bg-color);
  border-radius: var(--border-radius);
  padding: 0 8px;
  outline-color: transparent;
  transition: outline-color 0.3s ease-in-out;
}

.token-container.token-with-annos {
  cursor: pointer;
  border-left-style: solid;
}

.token-container.token-with-annos:hover {
  background-color: var(--main-bg-color);
}

.token-container.token-with-comment {
  border-left-color: var(--accent-color-fade3);
}

.token-container.token-content-copied {
  border-color: transparent;
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

.annotations > .annotation-line {
  height: 1.4em;
}

.annotations > .annotation-line:empty {
  visibility: hidden;
}
</style>

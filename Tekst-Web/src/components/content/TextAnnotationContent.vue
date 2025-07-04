<script setup lang="ts">
import type { TextAnnotationContentRead, TextAnnotationResourceRead } from '@/api';
import CopyToClipboardButton from '@/components/generic/CopyToClipboardButton.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import { $t } from '@/i18n';
import {
  CheckIcon,
  ClearIcon,
  ColorIcon,
  ColorOffIcon,
  CommentIcon,
  CopyIcon,
  MetadataIcon,
} from '@/icons';
import { useBrowseStore, useStateStore, useThemeStore } from '@/stores';
import { getFullLocationLabel, groupAndSortItems, pickTranslation, renderIcon } from '@/utils';
import { useClipboard } from '@vueuse/core';
import { adjustHue, saturate, toRgba, transparentize } from 'color2k';
import { NAlert, NButton, NDropdown, NFlex, NIcon, NTable, useThemeVars } from 'naive-ui';
import type { CSSProperties } from 'vue';
import { computed, nextTick, ref } from 'vue';
import CommonContentDisplay from './CommonContentDisplay.vue';

const _TOKEN_PLACEHOLDER = '[…]';

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
  form: string;
  comment?: string;
  annotations?: {
    group?: string;
    items: TextAnnotationContentRead['tokens'][number]['annotations'];
  }[];
}

type Token = TextAnnotationContentRead['tokens'][number];

const PAT_TMPL_ITEM = /{{\s*((?!}}).+?)\s*}}/g;
const PAT_TMPL_ITEM_PARTS = /_([kpcsf]):(.*?)(?=_[kpcsf]:|$)/g;
const PAT_TMPL_LINE_BREAK = /^br$/g;

const props = withDefaults(
  defineProps<{
    resource: TextAnnotationResourceRead;
    focusView?: boolean;
    showComments?: boolean;
  }>(),
  {
    focusView: false,
  }
);

const state = useStateStore();
const theme = useThemeStore();
const nuiTheme = useThemeVars();

const showDetailsModal = ref(false);
const tokenDetails = ref<TokenDetails>();
const tokenData = ref<Token>();

const annoCfg = computed(() => props.resource.config.special.annotations.annoIntegration);

const presentGroups = computed(() => {
  const keys = new Set(
    props.resource.contents
      ?.map((c) => c.tokens)
      .flat()
      .map((t) => t.annotations)
      .flat()
      .map((a) => a.key)
  );
  return annoCfg.value.groups
    .filter((g) =>
      annoCfg.value.itemProps
        .filter(
          (props) =>
            keys.has(props.key) && displayTemplates.value.map((t) => t.key).includes(props.key)
        )
        .map((props) => props.group)
        .filter((g) => !!g)
        .includes(g.key)
    )
    .map((g) => g.key);
});

const activeAnnoGroups = ref(
  props.resource.config.special.annotations.annoIntegration.groups.map((g) => g.key)
);
const groupColors = computed<Record<string, string>>(() =>
  Object.fromEntries(
    annoCfg.value.groups.map((g, i) => [
      g.key,
      toRgba(
        transparentize(
          saturate(
            adjustHue(theme.colors.primary.base, (360 / (annoCfg.value.groups.length + 1)) * i),
            1
          ),
          theme.dark ? 0.82 : 0.92
        )
      ),
    ])
  )
);

const showTokenContextMenu = ref(false);
const tokenContextMenuPos = ref({ x: 0, y: 0 });
const tokenContextIndex = ref<string>();
const {
  copy: copyTokenContent,
  copied: tokenContentCopied,
  isSupported: isTokenCopySupported,
} = useClipboard({ copiedDuring: 1000 });

const tokenContextMenuOptions = computed(() => [
  {
    label: () => $t('resources.types.textAnnotation.copyTokenAction'),
    key: 'copyToken',
    disabled: !isTokenCopySupported.value,
    icon: renderIcon(CopyIcon),
  },
  ...(tokenData.value?.annotations?.length
    ? [
        {
          label: () => $t('resources.types.textAnnotation.copyTokenFullAction'),
          key: 'copyFull',
          disabled: !isTokenCopySupported.value,
          icon: renderIcon(CopyIcon),
        },
      ]
    : []),
]);

const fontStyle = computed(() => ({
  fontFamily: props.resource.config.general.font || 'var(--font-family-content)',
}));

const annoLineNumbers = computed(() =>
  Array.from(Array(displayTemplates.value.filter((tmpl) => tmpl.type === 'br').length + 1).keys())
);
const colorAnnoLinesChoice = ref(
  props.resource.config.special.annotations.annoIntegration.groups.length > 1
);
const colorAnnoLines = computed(
  () => colorAnnoLinesChoice.value && annoCfg.value.groups.length > 1
);

const displayTemplates = computed<AnnotationDisplayTemplate[]>(() => {
  if (!props.resource.config.special.annotations.displayTemplate) return [];
  const out: AnnotationDisplayTemplate[] = [];
  // iterate over template items
  const items = [
    ...props.resource.config.special.annotations.displayTemplate.matchAll(PAT_TMPL_ITEM),
  ];
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
            item.group =
              annoCfg.value.itemProps.find((props) => props.key === item.key)?.group || undefined;
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
              group:
                annoCfg.value.itemProps.find((props) => props.key === a.key)?.group || undefined,
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
        anno.template.content
          ?.replace(/\\k/g, anno.data?.key || '')
          .replace(
            /\\t/g,
            pickTranslation(
              annoCfg.value.itemProps.find((props) => props.key === anno.data?.key)?.translations,
              state.locale
            )
          )
          .replace(
            /\\v/g,
            anno.data?.value
              // join the values with the delimiter set in the resource config
              .join(props.resource.config.special.annotations.multiValueDelimiter || '/') || ''
          ) || '';
      const prefix = i > 0 ? anno.template.prefix || '' : '';
      const suffix =
        i < annos.length - 1 && annos[i + 1].template.type !== 'br'
          ? anno.template.suffix || ''
          : '';
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
          form:
            t.annotations
              .find((a) => a.key === 'form')
              ?.value.join(props.resource.config.special.annotations.multiValueDelimiter) ||
            _TOKEN_PLACEHOLDER,
          eol: !!t.annotations.find((a) => a.key === 'eol'),
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
              !anno.group ||
              activeAnnoGroups.value.includes(anno.group) ||
              !annoCfg.value.groups.length
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
    fontFamily: fmtFlags.font ? fontStyle.value.fontFamily : undefined,
  };
}

function handleTokenClick(token: Token) {
  if (!token.annotations.length) return;
  const annos = token.annotations.filter((a) => a.key !== 'comment');
  tokenDetails.value = {
    form:
      token.annotations
        .find((a) => a.key === 'form')
        ?.value.join(props.resource.config.special.annotations.multiValueDelimiter) || '',
    comment: token.annotations.find((a) => a.key === 'comment')?.value.join('\n'),
    annotations: groupAndSortItems(annos, annoCfg.value).map((g) => ({
      group:
        pickTranslation(
          props.resource.config.special.annotations.annoIntegration.groups.find(
            (gg) => gg.key === g.group
          )?.translations,
          state.locale
        ) || g.group,
      items: g.items.map((i) => ({
        key:
          pickTranslation(
            annoCfg.value.itemProps.find((props) => props.key === i.key)?.translations,
            state.locale
          ) || i.key,
        value: i.value,
      })),
    })),
  };
  showDetailsModal.value = true;
}

function handleTokenRightClick(e: MouseEvent, token: Token, tokenId: string) {
  showTokenContextMenu.value = false;
  if (!isTokenCopySupported.value) return;
  tokenData.value = token;
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
  const tokenForm =
    tokenData.value?.annotations
      .find((a) => a.key === 'form')
      ?.value.join(props.resource.config.special.annotations.multiValueDelimiter) ||
    _TOKEN_PLACEHOLDER;
  if (key === 'copyToken') {
    copyTokenContent(tokenForm);
  } else if (key === 'copyFull') {
    const delim = props.resource.config.special.annotations.multiValueDelimiter;
    const annos = tokenData.value?.annotations
      ? tokenData.value.annotations.map((a) => `${a.key}: ${a.value.join(delim)}`).join('; ')
      : [];
    copyTokenContent(tokenForm + (annos ? ` (${annos})` : ''));
  }
}

function toggleAnnoGroup(key: string) {
  if (activeAnnoGroups.value.includes(key) && activeAnnoGroups.value.length <= 1) {
    activeAnnoGroups.value = annoCfg.value.groups.map((g) => g.key);
  } else if (activeAnnoGroups.value.includes(key)) {
    activeAnnoGroups.value = activeAnnoGroups.value.filter((g) => g !== key);
  } else {
    activeAnnoGroups.value = [...activeAnnoGroups.value, key];
  }
}

function generatePlaintextAnno(): string {
  const out: string[] = [];
  const browse = useBrowseStore();
  const resTitle = pickTranslation(props.resource.title, state.locale);
  const locLabel = getFullLocationLabel(
    browse.locationPath.slice(0, contents.value.length > 1 ? -1 : undefined),
    state.textLevelLabels,
    state.text
  );
  out.push(state.text?.title ? `${state.text?.title}\n` : '');
  out.push(resTitle + '\n' + locLabel + '\n\n---\n\n');

  // for each content...
  contents.value.forEach((c, contentIndex) => {
    // preprocess data
    const tokenLines: { form: string; annoLines: string[]; maxLen: number }[][] = [[]];
    c.tokens.forEach((t) => {
      t.form = t.form.normalize('NFC');
      const annoLines: string[] = t.annoDisplay.map((line) =>
        line.map((anno) => anno.content?.normalize('NFC') || '').join('')
      );
      const maxLen = Math.max(t.form.length, ...annoLines.map((l) => l.length));
      tokenLines[tokenLines.length - 1].push({ form: t.form, annoLines, maxLen });
      if (t.eol) tokenLines.push([]); // push new line if token followed by line break
    });
    // "render" token lines
    tokenLines.forEach((l, lineIndex) => {
      l.forEach((t) => {
        out.push(t.form.padEnd(t.maxLen + 1, ' '));
      });
      out.push('\n');
      const annoLineCount = Math.max(...l.map((t) => t.annoLines.length));
      for (let i = 0; i < annoLineCount; i++) {
        l.forEach((t) => {
          out.push(t.annoLines[i]?.padEnd(t.maxLen + 1, ' ') || '');
        });
        if (i < annoLineCount - 1) out.push('\n');
      }
      if (lineIndex < tokenLines.length - 1) out.push('\n\n');
    });
    if (contentIndex < contents.value.length - 1) out.push('\n\n---\n\n');
  });
  return out.join('').trim();
}
</script>

<template>
  <div>
    <n-flex v-if="!focusView" class="mb-md">
      <!-- ANNOTATION GROUP TOGGLES -->
      <template v-if="!!annoCfg.groups.length">
        <template v-for="group in annoCfg.groups">
          <n-button
            v-if="presentGroups.includes(group.key)"
            :tertiary="!colorAnnoLines"
            :type="colorAnnoLines ? 'primary' : undefined"
            :key="group.key"
            size="tiny"
            :focusable="false"
            :disabled="annoCfg.groups.length == 1"
            :color="colorAnnoLines ? groupColors[group.key] : undefined"
            :text-color="colorAnnoLines ? nuiTheme.textColor1 : undefined"
            @click="toggleAnnoGroup(group.key)"
          >
            <template #icon>
              <n-icon :component="activeAnnoGroups.includes(group.key) ? CheckIcon : ClearIcon" />
            </template>
            {{ pickTranslation(group.translations, state.locale) }}
          </n-button>
        </template>
        <n-button
          tertiary
          size="tiny"
          :focusable="false"
          :disabled="annoCfg.groups.length < 2"
          @click="colorAnnoLinesChoice = !colorAnnoLinesChoice"
        >
          <template #icon>
            <n-icon :component="colorAnnoLinesChoice ? ColorOffIcon : ColorIcon" />
          </template>
        </n-button>
      </template>
      <!-- COPY ANNOTATIONS TAB-ALIGNED AS PLAINTEXT -->
      <copy-to-clipboard-button
        tertiary
        size="tiny"
        :text="generatePlaintextAnno"
        :title="$t('resources.types.textAnnotation.copyAnnosPlainAction')"
      />
    </n-flex>

    <!-- CONTENT -->
    <common-content-display
      v-for="(c, cIndex) in contents"
      :key="c.id"
      :show-comments="showComments"
      :authors-comment="c.authorsComment"
      :editors-comment="c.editorsComment"
      :font="fontStyle.fontFamily"
    >
      <n-flex :size="4" class="anno-content">
        <template v-for="(t, tIndex) in c.tokens" :key="tIndex">
          <div
            class="token-container"
            :class="{
              'token-with-annos': !!t.annotations.length,
              'token-with-comment': !!t.annotations.find((a) => a.key === 'comment'),
              'token-content-copied':
                tokenContentCopied && tokenContextIndex === `${cIndex}-${tIndex}`,
            }"
            :title="$t('resources.types.textAnnotation.copyHintTip')"
            @click="handleTokenClick(t)"
            @contextmenu.prevent.stop="(e) => handleTokenRightClick(e, t, `${cIndex}-${tIndex}`)"
          >
            <div class="b i" :style="fontStyle">
              {{ t.form }}
            </div>
            <div class="annotations">
              <div
                v-for="(annoLine, lineIndex) in t.annoDisplay"
                :key="lineIndex"
                class="anno-sequence"
              >
                <template v-for="(anno, annoIndex) in annoLine" :key="annoIndex">
                  <span
                    v-if="
                      !anno.group || !annoCfg.groups.length || activeAnnoGroups.includes(anno.group)
                    "
                    :style="{
                      ...anno.style,
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
          <hr v-if="t.eol" class="token-lb" />
        </template>
      </n-flex>
    </common-content-display>

    <generic-modal
      v-model:show="showDetailsModal"
      :title="tokenDetails?.form"
      :icon="MetadataIcon"
      heading-level="3"
      :header-style="{
        'font-family': resource.config.general.font || 'var(--font-family-content)',
        'font-style': 'italic',
      }"
      @after-leave="() => (tokenDetails = undefined)"
    >
      <n-alert
        v-if="tokenDetails?.comment"
        type="default"
        :title="$t('common.comment')"
        class="mb-lg"
      >
        <template #icon>
          <n-icon :component="CommentIcon" size="medium" />
        </template>
        <div
          class="text-small"
          :style="{ fontFamily: resource.contentFont, whiteSpace: 'pre-line' }"
        >
          {{ tokenDetails.comment }}
        </div>
      </n-alert>

      <!-- ANNOTATIONS TABLES -->
      <n-table :bordered="false" :bottom-bordered="false" size="small">
        <template
          v-for="(group, index) in tokenDetails?.annotations"
          :key="`${group.group || 'ungrouped'}_${index}`"
        >
          <template v-if="!!group.items.length">
            <tr>
              <th colspan="2">
                {{ group.group || $t('common.other') }}
              </th>
            </tr>
            <tr v-for="(annotation, index) in group.items" :key="index">
              <td>{{ annotation.key }}</td>
              <td class="font-content">
                {{
                  annotation.value.join(
                    resource.config.special.annotations.multiValueDelimiter || '/'
                  )
                }}
              </td>
            </tr>
          </template>
        </template>
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
  </div>
</template>

<style scoped>
.token-container {
  position: relative;
  display: flex;
  flex-direction: column;
  flex-wrap: nowrap;
  border-left: 2px dashed var(--main-bg-color);
  border-radius: var(--border-radius);
  padding: 0 8px;
  outline-color: transparent;
  transition: outline-color 0.2s ease-in-out;
}

.token-container.token-with-annos {
  cursor: pointer;
  border-left-style: solid;
  transition: background-color 0.2s ease;
}

.token-container.token-with-annos:hover {
  background-color: var(--main-bg-color);
}

.token-container.token-with-comment {
  border-left-color: var(--primary-color-fade3);
}

.token-container.token-content-copied {
  border-color: transparent;
  outline: 2px dashed var(--primary-color-fade2);
}

.focus-view .token-container {
  padding-left: 4px;
}

.token-lb {
  width: 100%;
  border: none;
  height: 0px;
  margin: 4px 0;
}

.focus-view .token-lb {
  display: none;
}

.annotations {
  line-height: 1.4em;
  font-size: var(--font-size-small);
}

.focus-view .annotations {
  font-size: var(--font-size-tiny);
  opacity: 0.75;
}

.annotations > .anno-sequence {
  display: flex;
  align-items: baseline;
  flex-wrap: nowrap;
  margin-bottom: 2px;
}

.annotations > .anno-sequence:empty {
  visibility: hidden;
}

.annotations > .anno-sequence > span {
  padding: 0 1px;
  white-space: nowrap;
  transition: background-color 0.2s ease;
}

.annotations > .anno-sequence > span:first-child {
  border-top-left-radius: 3px;
  border-bottom-left-radius: 3px;
}

.annotations > .anno-sequence > span:last-child {
  border-top-right-radius: 3px;
  border-bottom-right-radius: 3px;
}
</style>

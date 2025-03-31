<script setup lang="ts">
import type { LineLabellingConfig, PlainTextResourceRead } from '@/api';
import { NFlex } from 'naive-ui';
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    resource: PlainTextResourceRead;
    focusView?: boolean;
  }>(),
  {
    focusView: false,
  }
);

const getLineLabel = (index: number, labellingType: LineLabellingConfig['labellingType']) => {
  switch (labellingType) {
    case 'numbersZeroBased':
      return index.toString();
    case 'numbersOneBased':
      return (index + 1).toString();
    case 'lettersLowercase':
      return String.fromCharCode('a'.charCodeAt(0) + (index % 26));
    case 'lettersUppercase':
      return String.fromCharCode('A'.charCodeAt(0) + (index % 26));
    default:
      return null;
  }
};

const multiContents = computed(() => (props.resource.contents?.length || 0) > 1);

const contents = computed(() =>
  props.resource.contents?.map((c) => ({
    ...c,
    lines: (props.focusView &&
    (props.resource.config.special.focusView.singleLine || multiContents.value)
      ? [c.text.replace(/(\r\n|\r|\n)+/g, props.resource.config.special.focusView.delimiter || ' ')]
      : c.text.split(/(\r\n|\r|\n)+/g).filter((l) => l.trim().length > 0)
    ).map((l, i) => ({
      label: !props.focusView
        ? getLineLabel(i, props.resource.config.special.lineLabelling.labellingType)
        : null,
      text: l,
    })),
  }))
);

const fontStyle = {
  fontFamily: props.resource.config.general.font || 'Tekst Content Font',
};

const contentCss = computed(() =>
  Object.fromEntries(props.resource.config.special.contentCss.map((c) => [c.prop, c.value]))
);
const cutomStyle = computed(() => ({ ...contentCss.value, ...fontStyle }));
</script>

<template>
  <div :style="cutomStyle">
    <div
      v-for="(content, contentIndex) in contents"
      :key="content.id"
      :class="{ 'mt-md': !focusView && contentIndex > 0 }"
      :title="content.comment || undefined"
    >
      <n-flex v-for="(line, index) in content.lines" :key="index" align="baseline" :wrap="false">
        <div
          v-if="resource.config.special.lineLabelling.enabled && line.label != null"
          class="text-color-accent ui-font text-small"
        >
          {{ line.label }}
        </div>
        <div>{{ line.text }}</div>
      </n-flex>
    </div>
  </div>
</template>

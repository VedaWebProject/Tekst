<script setup lang="ts">
import type { LineLabellingConfig, PlainTextResourceRead } from '@/api';
import { computed } from 'vue';
import { NFlex } from 'naive-ui';

const props = withDefaults(
  defineProps<{
    resource: PlainTextResourceRead;
    reduced?: boolean;
  }>(),
  {
    reduced: false,
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

const contents = computed(() =>
  props.resource.contents?.map((c) => ({
    ...c,
    lines: (props.reduced && props.resource.config?.general?.reducedViewOneline
      ? [c.text.replace(/(\r\n|\r|\n)+/g, ' ')]
      : c.text.split(/(\r\n|\r|\n)+/g).filter((l) => l.trim().length > 0)
    ).map((l, i) => ({
      label: !props.reduced
        ? getLineLabel(i, props.resource.config?.lineLabelling?.labellingType)
        : null,
      text: l,
    })),
  }))
);

const fontStyle = {
  fontFamily: props.resource.config?.general?.font || 'Tekst Content Font',
};
</script>

<template>
  <div :style="fontStyle">
    <div
      v-for="content in contents"
      :key="content.id"
      class="plain-text-content"
      :title="content.comment || undefined"
    >
      <n-flex v-for="(line, index) in content.lines" :key="index" align="baseline">
        <div
          v-if="resource.config?.lineLabelling?.enabled && line.label != null"
          class="text-color-accent ui-font text-small"
        >
          {{ line.label }}
        </div>
        <div>{{ line.text }}</div>
      </n-flex>
    </div>
  </div>
</template>

<style scoped>
.plain-text-content {
  margin-top: var(--content-gap);
}
.plain-text-content:first-child {
  margin-top: inherit;
}
</style>

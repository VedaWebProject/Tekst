<script setup lang="ts">
import { NIcon, NFlex, NButton, NListItem, NThing } from 'naive-ui';
import { ArrowBackIcon, ArrowForwardIcon, CorrectionNoteIcon } from '@/icons';

defineProps<{
  otherCount: number;
  smallScreen: boolean;
  loading?: boolean;
  prevDisabled?: boolean;
  nextDisabled?: boolean;
  indent?: boolean;
}>();

const emit = defineEmits(['prevClick', 'nextClick']);
</script>

<template>
  <n-list-item
    v-if="!!otherCount"
    :style="{ 'padding-left': indent ? 'var(--layout-gap)' : undefined }"
  >
    <n-thing :content-indented="!smallScreen" description-style="font-size: var(--font-size-tiny)">
      <template #avatar>
        <n-icon :component="CorrectionNoteIcon" size="large" />
      </template>
      <template #header>
        {{ $t('contents.corrections.otherTitle') }}
      </template>
      <template #header-extra>
        <n-flex align="center" :wrap="false" style="height: 100%">
          <n-button
            secondary
            size="small"
            :focusable="false"
            :disabled="loading || prevDisabled"
            :loading="loading"
            :title="$t('contents.corrections.otherGotoPrev')"
            @click="emit('prevClick')"
          >
            <template #icon>
              <n-icon :component="ArrowBackIcon" />
            </template>
          </n-button>
          <n-button
            secondary
            size="small"
            :focusable="false"
            :disabled="loading || nextDisabled"
            :loading="loading"
            :title="$t('contents.corrections.otherGotoNext')"
            @click="emit('nextClick')"
          >
            <template #icon>
              <n-icon :component="ArrowForwardIcon" />
            </template>
          </n-button>
        </n-flex>
      </template>
      <template #description>
        <span class="translucent text-tiny">
          {{ $t('contents.corrections.otherMsg', { count: otherCount }) }}
        </span>
      </template>
    </n-thing>
  </n-list-item>
</template>

<script setup lang="ts">
import { ArrowBackIcon, ArrowForwardIcon } from '@/icons';
import { NButton, NFlex, NIcon, NListItem, NThing } from 'naive-ui';

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
    :style="{ 'padding-left': indent ? 'var(--gap-lg)' : undefined }"
  >
    <n-thing :content-indented="!smallScreen" description-style="font-size: var(--font-size-tiny)">
      <template #header>
        {{ $t('contents.corrections.otherTitle') }}
      </template>
      <template #header-extra>
        <n-flex align="center" :wrap="false" style="height: 100%">
          <n-button
            secondary
            type="primary"
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
            type="primary"
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

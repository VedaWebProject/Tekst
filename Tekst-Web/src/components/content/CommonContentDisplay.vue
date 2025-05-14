<script setup lang="ts">
import { CommentIcon } from '@/icons';
import { NAlert, NIcon } from 'naive-ui';

defineProps<{
  authorsComment?: string | null;
  editorsComment?: string | null;
  showComments?: boolean;
  contentFont?: string;
}>();
</script>

<template>
  <div class="common-content-display">
    <slot></slot>

    <n-alert
      v-if="showComments && !!authorsComment"
      :title="$t('resources.types.common.contentFields.authorsComment')"
      class="mt-md"
    >
      <template #icon>
        <n-icon :component="CommentIcon" :size="16" />
      </template>
      <div class="pre-wrap text-small" :style="{ fontFamily: contentFont }">
        {{ authorsComment }}
      </div>
    </n-alert>

    <n-alert
      v-if="showComments && !!editorsComment"
      :title="$t('resources.types.common.contentFields.editorsComment')"
      class="mt-md"
    >
      <template #icon>
        <n-icon :component="CommentIcon" :size="16" />
      </template>
      <div class="pre-wrap text-small" :style="{ fontFamily: contentFont }">
        {{ editorsComment }}
      </div>
    </n-alert>
  </div>
</template>

<style scoped>
.common-content-display:not(:last-child) {
  padding-bottom: var(--gap-md);
  margin-bottom: var(--gap-md);
  border-bottom: 1px solid var(--main-bg-color);
}

.common-content-display:last-child {
  margin-bottom: 4px;
}
</style>

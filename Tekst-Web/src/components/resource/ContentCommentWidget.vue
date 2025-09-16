<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { CommentIcon } from '@/icons';
import { NBadge } from 'naive-ui';
import { computed } from 'vue';

const props = defineProps<{
  resource: AnyResourceRead;
  full?: boolean;
}>();

const showComments = defineModel<boolean>('showComments');
const emit = defineEmits(['done']);

const authorsComments = computed(
  () => props.resource.contents?.map((c) => c.authorsComment).filter(Boolean) || []
);
const editorsComments = computed(
  () => props.resource.contents?.map((c) => c.editorsComments).filter(Boolean) || []
);
const hasComments = computed(
  () => !!authorsComments.value.length || !!editorsComments.value.length
);
</script>

<template>
  <n-badge v-if="hasComments" :show="!showComments" dot :offset="[-5, 10]">
    <content-container-header-widget
      :full="full"
      :title="$t('common.comment', 2)"
      :icon-component="CommentIcon"
      :toggled="showComments"
      @click="
        () => {
          showComments = !showComments;
          emit('done');
        }
      "
    />
  </n-badge>
</template>

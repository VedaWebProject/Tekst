<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { CommentIcon } from '@/icons';
import { computed } from 'vue';

const props = defineProps<{
  resource: AnyResourceRead;
  full?: boolean;
}>();

const showComments = defineModel<boolean>('showComments');
const emit = defineEmits(['done']);

const hasComments = computed(() => !!props.resource.contents?.some((c) => !!c.comments?.length));
</script>

<template>
  <content-container-header-widget
    v-if="hasComments"
    :full="full"
    :title="$t('common.comment', 2)"
    :icon-component="CommentIcon"
    :toggled="showComments"
    :highlight="hasComments && !showComments"
    @click="
      () => {
        showComments = !showComments;
        emit('done');
      }
    "
  />
</template>

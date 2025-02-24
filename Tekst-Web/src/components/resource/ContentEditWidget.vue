<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { EditIcon } from '@/icons';
import { useBrowseStore } from '@/stores';
import { useRouter } from 'vue-router';

const props = defineProps<{
  resource: AnyResourceRead;
  full?: boolean;
}>();

const emit = defineEmits(['done']);
const router = useRouter();
const browse = useBrowseStore();

function handleClick() {
  router.push({
    name: 'resourceContents',
    params: {
      textSlug: router.currentRoute.value.params.textSlug,
      resId: props.resource.id,
      locId: browse.locationPath[props.resource.level || 0]?.id,
    },
  });
  emit('done');
}
</script>

<template>
  <content-container-header-widget
    v-if="resource.writable"
    :full="full"
    :title="$t('browse.contents.widgets.contentEdit.title')"
    :icon-component="EditIcon"
    @click="handleClick"
  />
</template>

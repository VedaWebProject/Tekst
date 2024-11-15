<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { EditIcon } from '@/icons';
import { useAuthStore, useBrowseStore } from '@/stores';
import { computed } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps<{
  resource: AnyResourceRead;
  full?: boolean;
}>();

const emit = defineEmits(['done']);

const auth = useAuthStore();
const router = useRouter();
const browse = useBrowseStore();

const show = computed(
  () =>
    auth.user &&
    ((props.resource.ownerId && auth.user.id === props.resource.ownerId) ||
      props.resource.sharedWrite.includes(auth.user.id) ||
      (props.resource.public && auth.user.isSuperuser))
);

function handleClick() {
  router.push({
    name: 'resourceContents',
    params: {
      text: router.currentRoute.value.params.text,
      id: props.resource.id,
      pos: browse.position,
    },
  });
  emit('done');
}
</script>

<template>
  <content-container-header-widget
    v-if="show"
    :full="full"
    :title="$t('browse.contents.widgets.contentEdit.title')"
    :icon-component="EditIcon"
    @click="handleClick"
  />
</template>

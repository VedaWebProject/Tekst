<script setup lang="ts">
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { computed } from 'vue';
import type { AnyResourceRead } from '@/api';
import { useAuthStore, useBrowseStore } from '@/stores';
import { useRouter } from 'vue-router';
import { EditIcon } from '@/icons';

const props = defineProps<{
  resource: AnyResourceRead;
}>();

const auth = useAuthStore();
const router = useRouter();
const browse = useBrowseStore();

const show = computed(
  () =>
    !!props.resource.contents?.length &&
    auth.user &&
    ((props.resource.ownerId && auth.user.id === props.resource.ownerId) ||
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
}
</script>

<template>
  <content-container-header-widget
    v-if="show"
    :title="$t('browse.contents.widgets.contentEdit.title')"
    :icon-component="EditIcon"
    @click="handleClick"
  />
</template>

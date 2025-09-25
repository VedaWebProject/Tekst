<script setup lang="ts">
import { GET, type AnyResourceRead } from '@/api';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { SkipNextIcon, SkipPreviousIcon } from '@/icons';
import { useBrowseStore } from '@/stores';
import { useRouter } from 'vue-router';

const props = defineProps<{
  resource: AnyResourceRead;
  full?: boolean;
  direction: 'before' | 'after';
}>();

const emit = defineEmits(['done']);
const router = useRouter();
const browse = useBrowseStore();
const { message } = useMessages();

function gotoLocation(locId?: string) {
  if (!locId) return;
  router.replace({
    params: {
      locId: locId,
    },
  });
}

async function handleClick() {
  const { data, error } = await GET('/browse/nearest-content-location', {
    params: {
      query: {
        loc: browse.locationPathHead?.id || '',
        res: props.resource.id,
        dir: props.direction,
      },
    },
  });
  if (!error) {
    gotoLocation(data.id);
  } else {
    message.info($t('browse.location.msgNoNearest'));
  }
  emit('done');
}
</script>

<template>
  <content-container-header-widget
    :full="full"
    :title="
      direction === 'before' ? $t('contents.tipBtnPrevChange') : $t('contents.tipBtnNextChange')
    "
    :icon-component="direction === 'before' ? SkipPreviousIcon : SkipNextIcon"
    @click="handleClick"
  />
</template>

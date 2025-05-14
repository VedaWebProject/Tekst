<script setup lang="ts">
import type { LocationRead } from '@/api';
import BookmarksWidget from '@/components/browse/BookmarksWidget.vue';
import LocationSelectModal from '@/components/modals/LocationSelectModal.vue';
import { $t } from '@/i18n';
import { ArrowBackIcon, ArrowForwardIcon, BookIcon } from '@/icons';
import router from '@/router';
import { useAuthStore, useBrowseStore } from '@/stores';
import { isInputFocused, isOverlayOpen } from '@/utils';
import { useMagicKeys, whenever } from '@vueuse/core';
import { NBadge, NButton, NFlex, NIcon } from 'naive-ui';
import { ref } from 'vue';

withDefaults(
  defineProps<{
    buttonSize?: 'small' | 'medium' | 'large';
  }>(),
  {
    buttonSize: 'large',
  }
);

const emit = defineEmits(['navigate']);

const auth = useAuthStore();
const browse = useBrowseStore();

const { ArrowLeft, ArrowRight } = useMagicKeys();

const showLocationSelectModal = ref(false);

function gotoPosition(locId?: string) {
  if (!locId) return;
  router.replace({
    params: {
      locId: locId,
    },
  });
  emit('navigate');
}

function handleLocationSelect(locationPath: LocationRead[]) {
  gotoPosition(locationPath[locationPath.length - 1]?.id);
}

// react to keyboard for in-/decreasing location
whenever(ArrowLeft, () => {
  if (!isOverlayOpen() && !isInputFocused()) gotoPosition(browse.prevLocationId);
});
whenever(ArrowRight, () => {
  if (!isOverlayOpen() && !isInputFocused()) gotoPosition(browse.nextLocationId);
});
</script>

<template>
  <!-- text location toolbar buttons -->
  <n-flex justify="space-between" align="center" :wrap="false">
    <n-button
      type="primary"
      :focusable="false"
      :title="$t('browse.toolbar.tipPreviousLocation')"
      :size="buttonSize"
      :bordered="false"
      :disabled="!browse.prevLocationId"
      @click="() => gotoPosition(browse.prevLocationId)"
    >
      <template #icon>
        <n-icon :component="ArrowBackIcon" />
      </template>
    </n-button>

    <n-badge value="!" :show="!browse.isOnDefaultLevel && !browse.loadingLocationData">
      <n-button
        type="primary"
        :title="
          $t('browse.toolbar.tipSelectLocation') +
          (!browse.isOnDefaultLevel ? ' (' + $t('browse.toolbar.tipNotOnDefaultLevel') + ')' : '')
        "
        :focusable="false"
        :size="buttonSize"
        :bordered="false"
        @click="showLocationSelectModal = true"
      >
        <template #icon>
          <n-icon :component="BookIcon" />
        </template>
      </n-button>
    </n-badge>

    <bookmarks-widget v-if="!!auth.user" :button-size="buttonSize" />

    <n-button
      type="primary"
      :focusable="false"
      :title="$t('browse.toolbar.tipNextLocation')"
      :size="buttonSize"
      :bordered="false"
      :disabled="!browse.nextLocationId"
      @click="() => gotoPosition(browse.nextLocationId)"
    >
      <template #icon>
        <n-icon :component="ArrowForwardIcon" />
      </template>
    </n-button>
  </n-flex>

  <location-select-modal
    v-model:show="showLocationSelectModal"
    :current-location-path="browse.locationPath"
    @submit="handleLocationSelect"
  />
</template>

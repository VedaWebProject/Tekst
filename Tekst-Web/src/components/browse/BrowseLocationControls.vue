<script setup lang="ts">
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore, useBrowseStore } from '@/stores';
import { NBadge, NButton, NIcon, NFlex } from 'naive-ui';
import type { LocationRead } from '@/api';
import router from '@/router';
import { useMagicKeys, whenever } from '@vueuse/core';
import { $t } from '@/i18n';
import LocationSelectModal from '@/components/modals/LocationSelectModal.vue';
import BookmarksWidget from '@/components/browse/BookmarksWidget.vue';

import { ArrowBackIcon, ArrowForwardIcon, BookIcon } from '@/icons';
import { isInputFocused, isOverlayOpen } from '@/utils';

withDefaults(
  defineProps<{
    buttonSize?: 'small' | 'medium' | 'large';
  }>(),
  {
    buttonSize: 'large',
  }
);

const auth = useAuthStore();
const browse = useBrowseStore();
const route = useRoute();

const { ArrowLeft, ArrowRight } = useMagicKeys();

const showLocationSelectModal = ref(false);

function gotoPosition(direction: 'prev' | 'next') {
  const targetPos = browse.position + (direction === 'prev' ? -1 : 1);
  router.replace({
    ...route,
    query: {
      ...route.query,
      pos: targetPos >= 0 ? targetPos : 0,
    },
  });
}

function handleLocationSelect(locationPath: LocationRead[]) {
  const selectedLocation = locationPath[locationPath.length - 1];
  if (!selectedLocation) return;
  router.push({
    name: 'browse',
    params: { ...route.params },
    query: {
      lvl: selectedLocation.level,
      pos: selectedLocation.position,
    },
  });
}

// react to keyboard for in-/decreasing location
whenever(ArrowLeft, () => {
  if (!isOverlayOpen() && !isInputFocused()) gotoPosition('prev');
});
whenever(ArrowRight, () => {
  if (!isOverlayOpen() && !isInputFocused()) gotoPosition('next');
});
</script>

<template>
  <!-- text location toolbar buttons -->
  <n-flex justify="space-between" align="center" :wrap="false">
    <n-button
      type="primary"
      :disabled="browse.position === 0"
      :focusable="false"
      :title="$t('browse.toolbar.tipPreviousLocation')"
      :size="buttonSize"
      :bordered="false"
      @click="() => gotoPosition('prev')"
    >
      <template #icon>
        <n-icon :component="ArrowBackIcon" />
      </template>
    </n-button>

    <n-badge
      :show="!browse.isOnDefaultLevel && !browse.loadingLocationData"
      value="!"
      color="var(--accent-color-spotlight)"
    >
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

    <bookmarks-widget v-if="auth.loggedIn" :button-size="buttonSize" />

    <n-button
      type="primary"
      :focusable="false"
      :title="$t('browse.toolbar.tipNextLocation')"
      :size="buttonSize"
      :bordered="false"
      @click="() => gotoPosition('next')"
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

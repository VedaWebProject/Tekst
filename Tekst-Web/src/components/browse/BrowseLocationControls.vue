<script setup lang="ts">
import type { LocationRead } from '@/api';
import BookmarksWidget from '@/components/browse/BookmarksWidget.vue';
import LocationSelectModal from '@/components/modals/LocationSelectModal.vue';
import { $t } from '@/i18n';
import { ArrowBackIcon, ArrowForwardIcon, BookIcon, WarningIcon } from '@/icons';
import router from '@/router';
import { useAuthStore, useBrowseStore } from '@/stores';
import { isInputFocused, isOverlayOpen } from '@/utils';
import { useMagicKeys, whenever } from '@vueuse/core';
import { NBadge, NButton, NFlex, NIcon } from 'naive-ui';
import { ref } from 'vue';
import { useRoute } from 'vue-router';

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
const route = useRoute();

const { ArrowLeft, ArrowRight } = useMagicKeys();

const showLocationSelectModal = ref(false);

function gotoPosition(direction: 'prev' | 'next') {
  const targetLocId = direction === 'prev' ? browse.prevLocationId : browse.nextLocationId;
  if (!targetLocId) return;
  router.replace({
    name: 'browse',
    params: {
      ...route.params,
      locId: targetLocId,
    },
  });
  emit('navigate');
}

function handleLocationSelect(locationPath: LocationRead[]) {
  const selectedLocation = locationPath[locationPath.length - 1];
  if (!selectedLocation) return;
  router.push({
    name: 'browse',
    params: { ...route.params },
    query: {
      loc: selectedLocation.id,
    },
  });
  emit('navigate');
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
      :focusable="false"
      :title="$t('browse.toolbar.tipPreviousLocation')"
      :size="buttonSize"
      :bordered="false"
      :disabled="!browse.prevLocationId"
      @click="() => gotoPosition('prev')"
    >
      <template #icon>
        <n-icon :component="ArrowBackIcon" />
      </template>
    </n-button>

    <n-badge
      :show="!browse.isOnDefaultLevel && !browse.loadingLocationData"
      color="var(--accent-color-spotlight)"
    >
      <template #value>
        <n-icon :component="WarningIcon" />
      </template>
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
      :disabled="!browse.nextLocationId"
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

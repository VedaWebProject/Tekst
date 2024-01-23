<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useBrowseStore } from '@/stores';
import { NButton } from 'naive-ui';
import type { LocationRead } from '@/api';
import router from '@/router';
import { useMagicKeys, whenever } from '@vueuse/core';
import { $t } from '@/i18n';
import LocationSelectModal from '@/components/modals/LocationSelectModal.vue';

import ArrowBackIosOutlined from '@vicons/material/ArrowBackIosOutlined';
import ArrowForwardIosOutlined from '@vicons/material/ArrowForwardIosOutlined';
import MenuBookOutlined from '@vicons/material/MenuBookOutlined';

withDefaults(
  defineProps<{
    buttonSize?: 'small' | 'medium' | 'large';
  }>(),
  { buttonSize: 'large' }
);

const browse = useBrowseStore();
const route = useRoute();
const position = computed<number>(() => parseInt(route.query.pos?.toString() || '0'));

const { ArrowLeft, ArrowRight } = useMagicKeys();

const showLocationSelectModal = ref(false);

function getPrevNextRoute(step: number) {
  return {
    ...route,
    query: {
      ...route.query,
      pos: position.value >= 0 ? position.value + step : 0,
    },
  };
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
whenever(ArrowRight, () => {
  router.replace(getPrevNextRoute(1));
});
whenever(ArrowLeft, () => {
  router.replace(getPrevNextRoute(-1));
});

const btnBgColor = '#00000015';
const btnColor = '#fff';
</script>

<template>
  <!-- text location toolbar buttons -->
  <div class="text-location">
    <router-link
      v-slot="{
        // @ts-ignore
        navigate,
      }"
      :to="getPrevNextRoute(-1)"
      custom
    >
      <n-button
        :disabled="browse.position === 0"
        :focusable="false"
        :title="$t('browse.toolbar.tipPreviousLocation')"
        :size="buttonSize"
        :color="btnBgColor"
        :style="{ color: btnColor }"
        @click="navigate"
      >
        <template #icon>
          <ArrowBackIosOutlined />
        </template>
      </n-button>
    </router-link>

    <n-button
      :title="$t('browse.toolbar.tipSelectLocation')"
      :focusable="false"
      :size="buttonSize"
      :color="btnBgColor"
      :style="{ color: btnColor }"
      @click="showLocationSelectModal = true"
    >
      <template #icon>
        <MenuBookOutlined />
      </template>
    </n-button>

    <router-link v-slot="{ navigate }" :to="getPrevNextRoute(1)" custom>
      <n-button
        :focusable="false"
        :title="$t('browse.toolbar.tipNextLocation')"
        :size="buttonSize"
        :color="btnBgColor"
        :style="{ color: btnColor }"
        @click="navigate"
      >
        <template #icon>
          <ArrowForwardIosOutlined />
        </template>
      </n-button>
    </router-link>
  </div>

  <LocationSelectModal
    v-model:show="showLocationSelectModal"
    :location-path="browse.locationPath"
    @update:location-path="handleLocationSelect"
  />
</template>

<style scoped>
.text-location {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.location-select-item {
  margin-bottom: 0.5rem;
}

.location-select-item.disabled {
  opacity: 0.5;
}
</style>

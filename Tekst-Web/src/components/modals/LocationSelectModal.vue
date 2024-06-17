<script setup lang="ts">
import { ref } from 'vue';
import { NButton } from 'naive-ui';
import type { LocationRead } from '@/api';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { $t } from '@/i18n';
import GenericModal from '@/components/generic/GenericModal.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import LocationSelectForm from '@/forms/LocationSelectForm.vue';

import { BookIcon } from '@/icons';
import { watch } from 'vue';

const props = withDefaults(
  defineProps<{
    currentLocationPath: LocationRead[];
    showLevelSelect?: boolean;
  }>(),
  {
    showLevelSelect: true,
  }
);

const show = defineModel<boolean>('show');
const emit = defineEmits(['submit']);

const locationPath = ref<LocationRead[]>(props.currentLocationPath);

watch(
  () => props.currentLocationPath,
  (newLocationPath) => {
    locationPath.value = newLocationPath;
  }
);

function submit() {
  emit('submit', locationPath.value);
  show.value = false;
}
</script>

<template>
  <generic-modal v-model:show="show">
    <template #header>
      <icon-heading level="2" :icon="BookIcon" style="margin: 0">
        {{ $t('browse.location.modalHeading') }}
        <help-button-widget help-key="browseLocationControls" />
      </icon-heading>
    </template>

    <location-select-form v-model="locationPath" :show-level-select="showLevelSelect" />

    <button-shelf top-gap>
      <n-button type="primary" :disabled="!locationPath.length" @click="submit">
        {{ $t('browse.location.submitBtn') }}
      </n-button>
    </button-shelf>
  </generic-modal>
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

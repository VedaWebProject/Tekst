<script setup lang="ts">
import type { LocationRead } from '@/api';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import LocationSelectForm from '@/forms/LocationSelectForm.vue';
import { $t } from '@/i18n';
import { NButton } from 'naive-ui';
import { ref } from 'vue';

import { BookIcon } from '@/icons';
import { watch } from 'vue';

const props = withDefaults(
  defineProps<{
    currentLocationPath: LocationRead[];
    allowLevelChange?: boolean;
  }>(),
  {
    allowLevelChange: true,
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
      <icon-heading level="2" :icon="BookIcon" class="m-0">
        {{ $t('common.location') }}
        <help-button-widget help-key="browseLocationControls" />
      </icon-heading>
    </template>

    <location-select-form v-model="locationPath" :allow-level-change="allowLevelChange" />

    <button-shelf top-gap>
      <n-button type="primary" :disabled="!locationPath.length" @click="submit">
        {{ $t('browse.location.goTo') }}
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
</style>

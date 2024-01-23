<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useStateStore } from '@/stores';
import { NButton, NSelect, NFormItem, NForm, NDivider } from 'naive-ui';
import type { LocationRead, TextRead } from '@/api';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { GET } from '@/api';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import GenericModal from '@/components/generic/GenericModal.vue';
import IconHeading from '@/components/generic/IconHeading.vue';

import MenuBookOutlined from '@vicons/material/MenuBookOutlined';

const props = withDefaults(
  defineProps<{
    locationPath: LocationRead[];
    showLevelSelect?: boolean;
    show?: boolean;
  }>(),
  {
    showLevelSelect: true,
    show: false,
  }
);

const emit = defineEmits(['update:show', 'update:locationPath']);

const state = useStateStore();
const { message } = useMessages();

watch(
  () => props.show,
  (show) => show && initSelectModels()
);

const locationLevel = ref(props.locationPath.length - 1);
const locationLevelOptions = computed(() =>
  state.textLevelLabels.map((l, i) => ({
    value: i,
    label: l,
  }))
);
// sync browse level in location controls state with actual browse level (if possible)
watch(
  () => props.locationPath.length,
  (after) => {
    locationLevel.value = after - 1;
  }
);
// react to browse level selection changes
watch(locationLevel, (after, before) => {
  if (props.show) {
    if (after > before) {
      updateSelectModelsFromLvl(before);
    }
    applyBrowseLevel();
  }
});

// interface for location select options (local state)
interface LocationSelectModel {
  loading: boolean;
  selected: string | null;
  disabled: boolean;
  locations: LocationRead[];
}
const locationSelectModels = ref<LocationSelectModel[]>(getEmptyModels());

// generate location select options from select model locations
const locationSelectOptions = computed(() =>
  locationSelectModels.value.map((lsm) =>
    lsm.locations.map((n) => ({
      label: n.label,
      value: n.id,
    }))
  )
);

// generate fresh location select models when text changes
watch(
  () => state.text,
  (after) => (locationSelectModels.value = getEmptyModels(after))
);

function getEmptyModels(text: TextRead | undefined = state.text): LocationSelectModel[] {
  if (!text) return [];
  return (
    text.levels.map((_, i) => ({
      loading: false,
      selected: null,
      locations: [],
      options: [],
      disabled: props.showLevelSelect && i > locationLevel.value,
    })) || []
  );
}

async function updateSelectModelsFromLvl(lvl: number) {
  // abort if the highest enabled level was changed (nothing to do)
  if (lvl >= locationSelectModels.value.length - 1) {
    return;
  }
  // set loading state
  locationSelectModels.value.forEach((lsm, i) => {
    // only apply to higher levels
    if (i > lvl) {
      lsm.loading = true;
    }
  });
  // load location path options from location selected at lvl as root
  const { data: locations, error } = await GET('/browse/locations/{id}/path/options-by-root', {
    params: { path: { id: locationSelectModels.value[lvl].selected || '' } },
  });
  if (error) {
    message.error($t('errors.unexpected'), error);
    return;
  }
  // set locations for all following levels
  locationSelectModels.value.forEach((lsm, i) => {
    // only apply to higher levels
    if (i > lvl) {
      // only do this if we're <= current browse level
      if (i <= locationLevel.value) {
        // set locations
        lsm.locations = locations.shift() || [];
        // set selection
        lsm.selected = lsm.locations[0]?.id || null;
      }
      // set to no loading
      lsm.loading = false;
    }
  });
}

function applyBrowseLevel() {
  locationSelectModels.value.forEach((lsm, i) => {
    lsm.disabled = props.showLevelSelect && i > locationLevel.value;
    lsm.locations = lsm.disabled ? [] : lsm.locations;
    lsm.selected = lsm.disabled ? null : lsm.selected;
  });
}

async function initSelectModels() {
  // set all live models to loading
  locationSelectModels.value.forEach((lsm) => {
    lsm.loading = true;
  });

  // fetch locations from head to root
  const { data: locationsOptions, error } = await GET(
    '/browse/locations/{id}/path/options-by-head',
    {
      params: { path: { id: props.locationPath[locationLevel.value].id ?? '' } },
    }
  );

  if (error) {
    message.error($t('errors.unexpected'), error);
    return;
  }
  // apply browse level
  applyBrowseLevel();

  // manipulate each location select model
  let index = 0;
  for (const lsm of locationSelectModels.value) {
    // set options and selection
    if (index <= locationLevel.value) {
      // remember locations for these options
      lsm.locations = locationsOptions[index];
      // set selection
      lsm.selected = props.locationPath?.[index]?.id || null;
    }
    index++;
    lsm.loading = false;
  }
}

function handleLocationSelect() {
  emit(
    'update:locationPath',
    locationSelectModels.value
      .filter((_, i) => i <= locationLevel.value)
      .map((lsm) => lsm.locations.find((n) => n.id === lsm.selected))
  );
  emit('update:show', false);
}
</script>

<template>
  <GenericModal :show="show" @update:show="emit('update:show', $event)">
    <template #header>
      <IconHeading level="2" :icon="MenuBookOutlined" style="margin: 0">
        {{ $t('browse.location.modalHeading') }}
        <HelpButtonWidget help-key="browseLocationControls" />
      </IconHeading>
    </template>

    <n-form
      label-placement="left"
      label-width="auto"
      :show-feedback="false"
      :show-require-mark="false"
    >
      <template v-if="showLevelSelect">
        <n-form-item :label="$t('browse.location.level')">
          <n-select v-model:value="locationLevel" :options="locationLevelOptions" />
        </n-form-item>

        <n-divider />
      </template>

      <n-form-item
        v-for="(levelLoc, index) in locationSelectModels"
        :key="`${index}_loc_select`"
        :label="state.textLevelLabels[index]"
        class="location-select-item"
        :class="levelLoc.disabled && 'disabled'"
      >
        <n-select
          v-model:value="levelLoc.selected"
          :options="locationSelectOptions[index]"
          filterable
          placeholder="–"
          :loading="levelLoc.loading"
          :disabled="
            levelLoc.loading || levelLoc.disabled || locationSelectOptions[index].length === 0
          "
          @update:value="() => updateSelectModelsFromLvl(index)"
        />
      </n-form-item>
    </n-form>
    <ButtonShelf top-gap>
      <n-button secondary :focusable="false" @click="emit('update:show', false)">
        {{ $t('general.cancelAction') }}
      </n-button>
      <n-button type="primary" @click="handleLocationSelect">
        {{ $t('general.selectAction') }}
      </n-button>
    </ButtonShelf>
  </GenericModal>
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

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useStateStore } from '@/stores';
import { NSelect, NFormItem, NForm, NDivider } from 'naive-ui';
import type { LocationRead, TextRead } from '@/api';
import { GET } from '@/api';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';

const props = withDefaults(
  defineProps<{
    showLevelSelect?: boolean;
  }>(),
  {
    showLevelSelect: true,
  }
);

const model = defineModel<LocationRead[]>({ required: true });

const state = useStateStore();
const { message } = useMessages();

const lvl = ref(Math.max(0, model.value.length - 1));
const lvlOptions = computed(() =>
  state.textLevelLabels.map((l, i) => ({
    value: i,
    label: l,
  }))
);
// react to level selection changes
watch(lvl, (after, before) => {
  if (after > before) {
    updateSelectModels(before);
  }
  applyBrowseLevel();
});

// interface for location select options (internal component state)
interface LocationSelectModel {
  loading: boolean;
  selected: string | null;
  disabled: boolean;
  locations: LocationRead[];
}
const locationSelectModels = ref<LocationSelectModel[]>(getEmptyModels());
const loading = computed(() => locationSelectModels.value.some((lsm) => lsm.loading));

// generate location select options from select model locations
const locationSelectOptions = computed(() =>
  locationSelectModels.value.map((lsm) =>
    lsm.locations.map((n) => ({
      label: n.label,
      value: n.id,
    }))
  )
);

function getEmptyModels(text: TextRead | undefined = state.text): LocationSelectModel[] {
  if (!text) return [];
  return (
    text.levels.map((_, i) => ({
      loading: false,
      selected: null,
      locations: [],
      options: [],
      disabled: props.showLevelSelect && i > lvl.value,
    })) || []
  );
}

async function updateSelectModels(fromLvl: number = 0) {
  // abort if the highest enabled level was changed (nothing to do)
  if (fromLvl >= locationSelectModels.value.length - 1) {
    updateModel();
    return;
  }
  // set loading state
  locationSelectModels.value.forEach((lsm, i) => {
    // only apply to higher levels
    if (i > fromLvl) {
      lsm.loading = true;
    }
  });
  // cancel if requested level has no selected location
  if (!locationSelectModels.value[fromLvl].selected) {
    return;
  }
  // load location path options from location selected at lvl as root
  const { data: locations, error } = await GET('/browse/locations/{id}/path/options-by-root', {
    params: { path: { id: locationSelectModels.value[fromLvl].selected || '' } },
  });
  if (error) {
    updateModel();
    return;
  }
  // set locations for all following levels
  locationSelectModels.value.forEach((lsm, i) => {
    // only apply to higher levels
    if (i > fromLvl) {
      // only do this if we're <= current browse level
      if (i <= lvl.value) {
        // set locations
        lsm.locations = locations.shift() || [];
        // set selection
        lsm.selected = lsm.locations[0]?.id || null;
      }
      // set to no loading
      lsm.loading = false;
    }
  });
  updateModel();
}

function applyBrowseLevel() {
  locationSelectModels.value.forEach((lsm, i) => {
    lsm.disabled = props.showLevelSelect && i > lvl.value;
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
  const reqLocId = model.value[lvl.value]?.id;
  if (!reqLocId) {
    return;
  }
  const { data: locationsOptions, error } = await GET(
    '/browse/locations/{id}/path/options-by-head',
    {
      params: { path: { id: reqLocId } },
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
    if (index <= lvl.value) {
      // remember locations for these options
      lsm.locations = locationsOptions[index];
      // set selection
      lsm.selected = model.value[index]?.id || null;
    }
    index++;
    lsm.loading = false;
  }
}

function updateModel() {
  model.value = locationSelectModels.value
    .filter((_, i) => i <= lvl.value)
    .map((lsm) => lsm.locations.find((n) => n.id === lsm.selected) || lsm.locations[0]);
}

onMounted(() => {
  initSelectModels();
});
</script>

<template>
  <n-form
    label-placement="left"
    label-width="auto"
    :show-feedback="false"
    :show-require-mark="false"
  >
    <template v-if="props.showLevelSelect">
      <n-form-item :label="$t('browse.location.level')">
        <n-select
          v-model:value="lvl"
          :options="lvlOptions"
          :disabled="loading"
          :loading="loading"
          @update:value="updateSelectModels"
        />
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
        :loading="loading"
        :disabled="loading || levelLoc.disabled || locationSelectOptions[index].length === 0"
        @update:value="() => updateSelectModels(index)"
      />
    </n-form-item>
  </n-form>
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

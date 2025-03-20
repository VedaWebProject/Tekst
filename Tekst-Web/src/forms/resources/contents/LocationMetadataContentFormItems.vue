<script setup lang="ts">
import type {
  KeyValueAggregations,
  LocationMetadataContentCreate,
  LocationMetadataResourceRead,
} from '@/api';
import { dynInputCreateBtnProps } from '@/common';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { contentFormRules } from '@/forms/formRules';
import { useResourcesStore } from '@/stores';
import { cloneDeep } from 'lodash-es';
import { NDynamicInput, NFlex, NFormItem, NSelect, type SelectOption } from 'naive-ui';
import { computed, h, onMounted, ref } from 'vue';
import { defaultContentModels } from './defaultContentModels';

const props = defineProps<{
  resource: LocationMetadataResourceRead;
}>();

const model = defineModel<LocationMetadataContentCreate>({ required: true });

const resources = useResourcesStore();

const metaValueStyle = {
  fontFamily: props.resource.config.general.font || 'Tekst Content Font',
};

const aggregations = ref<KeyValueAggregations>([]);
const entriesOptions = computed(() => {
  // all possible keys, containing unique keys collected in
  // aggregations and from the current model state
  const keys = [
    ...new Set([
      ...aggregations.value.map((agg) => agg.key),
      ...model.value.entries.map((entry) => entry.key).flat(),
    ]),
  ];
  return (
    model.value.entries.map((entry) => ({
      keysOptions: keys
        .filter((k) => !model.value.entries.map((e) => e.key).includes(k))
        .map((k) => ({
          label: k,
          value: k,
        })),
      valuesOptions:
        aggregations.value
          .find((agg) => agg.key === entry.key)
          ?.values?.map((v) => ({ label: v, value: v })) || [],
    })) || []
  );
});

function renderValueLabel(option: SelectOption) {
  return h(
    'div',
    {
      style: metaValueStyle,
    },
    option.label as string
  );
}

onMounted(async () => {
  aggregations.value = await resources.getAggregations(props.resource.id);
});
</script>

<template>
  <n-form-item
    :label="$t('resources.types.locationMetadata.contentFields.entries')"
    :show-feedback="false"
  >
    <n-dynamic-input
      v-model:value="model.entries"
      :create-button-props="dynInputCreateBtnProps"
      @create="() => cloneDeep(defaultContentModels.locationMetadata.entries[0])"
    >
      <template #default="{ index }">
        <n-flex align="flex-start" :wrap="false" style="flex: 2">
          <n-form-item
            style="flex: 2 100px"
            :show-label="false"
            :path="`entries[${index}].key`"
            :rule="contentFormRules.locationMetadata.key"
            ignore-path-change
          >
            <n-select
              v-model:value="model.entries[index].key"
              filterable
              tag
              clearable
              :options="entriesOptions[index].keysOptions"
              :placeholder="$t('general.key')"
              @update:value="() => (model.entries[index].value = [])"
            />
          </n-form-item>
          <n-form-item
            style="flex: 2 100px"
            :show-label="false"
            :path="`entries[${index}].value`"
            :rule="contentFormRules.locationMetadata.value"
            ignore-path-change
          >
            <n-select
              v-model:value="model.entries[index].value"
              multiple
              filterable
              tag
              clearable
              :disabled="!model.entries[index].key"
              :options="entriesOptions[index].valuesOptions"
              :placeholder="$t('general.value')"
              :style="metaValueStyle"
              :render-label="renderValueLabel"
            />
          </n-form-item>
        </n-flex>
      </template>
      <template #action="{ index, create, remove }">
        <dynamic-input-controls
          secondary
          :movable="false"
          :insert-disabled="model.entries.length >= 128"
          :remove-disabled="model.entries.length <= 1"
          @remove="() => remove(index)"
          @insert="() => create(index)"
        />
      </template>
      <template #create-button-default>
        {{ $t('general.addAction') }}
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>

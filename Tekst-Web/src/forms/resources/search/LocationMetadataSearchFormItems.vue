<script setup lang="ts">
import type {
  KeyValueAggregations,
  LocationMetadataResourceRead,
  LocationMetadataSearchQuery,
} from '@/api';
import { dynInputCreateBtnProps } from '@/common';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { searchFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { useResourcesStore, useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { NDynamicInput, NFlex, NFormItem, NSelect, NSwitch } from 'naive-ui';
import { computed, onMounted, ref } from 'vue';

const props = defineProps<{
  resource: LocationMetadataResourceRead;
  queryIndex: number;
}>();
const model = defineModel<LocationMetadataSearchQuery>({ required: true });

const state = useStateStore();
const resources = useResourcesStore();

const metaValueStyle = {
  fontFamily: props.resource.config.general.font || 'Tekst Content Font',
};

const aggregations = ref<KeyValueAggregations>([]);
const entryOptions = computed(() => {
  const anyValueOption = {
    label: () => $t('resources.types.locationMetadata.searchFields.any'),
    value: '',
  };
  return (
    model.value.entries?.map((entry) => ({
      keysOptions: aggregations.value.map((agg) => ({
        label:
          pickTranslation(
            props.resource.config.special.itemDisplay.displayProps.find((dp) => dp.name === agg.key)
              ?.translations,
            state.locale
          ) || agg.key,
        value: agg.key,
      })),
      valuesOptions: [
        anyValueOption,
        ...(aggregations.value
          .find(
            // find possible values for the selected key
            (agg) => agg.key === entry.k
          )
          ?.values?.filter(
            // filter out already selected values
            (v) =>
              !model.value.entries
                ?.filter((en) => en.k === entry.k)
                .map((en) => en.v)
                ?.includes(v)
          )
          .map(
            // map anno key-value pairs to options
            (v) => ({ label: v, value: v, style: metaValueStyle })
          ) || []),
      ],
    })) || []
  );
});

function getEntryValueSelectStyle(value?: string) {
  return value ? metaValueStyle : undefined;
}

onMounted(async () => {
  aggregations.value = await resources.getAggregations(props.resource.id);
});
</script>

<template>
  <!-- ENTRIES -->
  <n-form-item
    :label="$t('resources.types.locationMetadata.contentFields.entries')"
    :show-feedback="!model.entries?.length"
    style="flex: 2 400px"
  >
    <n-dynamic-input
      v-model:value="model.entries"
      :create-button-props="dynInputCreateBtnProps"
      @create="() => ({ k: undefined, v: undefined })"
    >
      <template #default="{ value, index }">
        <n-flex wrap align="flex-start" style="flex: 2">
          <!-- KEY -->
          <n-form-item
            style="flex: 2 200px"
            :show-label="false"
            ignore-path-change
            :path="`queries[${queryIndex}].rts.entries[${index}].k`"
            :rule="searchFormRules.textAnnotation.annotationKey"
          >
            <n-select
              v-model:value="value.k"
              filterable
              clearable
              :options="entryOptions[index].keysOptions"
              :placeholder="$t('common.key')"
              @update:value="() => (value.v = '')"
            />
          </n-form-item>

          <n-flex :wrap="false" align="center" style="flex: 2 248px">
            <!-- VALUE -->
            <n-form-item
              :show-label="false"
              ignore-path-change
              :path="`queries[${queryIndex}].rts.entries[${index}].v`"
              :rule="searchFormRules.locationMetadata.value"
              style="flex: 2 200px"
            >
              <n-select
                v-model:value="value.v"
                tag
                filterable
                clearable
                :disabled="!value.k"
                :style="getEntryValueSelectStyle(value.v)"
                :options="entryOptions[index].valuesOptions"
                :placeholder="$t('common.value')"
              />
            </n-form-item>

            <!-- VALUE QUERY WILDCARDS -->
            <n-form-item :show-label="false" ignore-path-change style="flex-basis: 48px">
              <n-switch
                v-model:value="value.wc"
                :round="false"
                class="b text-small"
                :title="$t('search.advancedSearch.wc')"
              >
                <template #checked>*</template>
                <template #unchecked>*</template>
              </n-switch>
            </n-form-item>
          </n-flex>
        </n-flex>
      </template>
      <template #action="{ index, create, remove }">
        <dynamic-input-controls
          :movable="false"
          :insert-disabled="(model.entries?.length || 0) >= 64"
          @remove="() => remove(index)"
          @insert="() => create(index)"
        />
      </template>
      <template #create-button-default>
        {{ $t('common.select') }}
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>

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
import { AsteriskIcon } from '@/icons';
import { useResourcesStore, useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { NButton, NDynamicInput, NFlex, NFormItem, NIcon, NSelect } from 'naive-ui';
import { computed, onMounted, ref } from 'vue';

const props = defineProps<{
  resource: LocationMetadataResourceRead;
  queryIndex: number;
}>();
const model = defineModel<LocationMetadataSearchQuery>({ required: true });

const state = useStateStore();
const resources = useResourcesStore();

const metaValueStyle = {
  fontFamily: props.resource.config.general.font || 'var(--font-family-content)',
};

const aggregations = ref<KeyValueAggregations>([]);
const entryOptions = computed(() => {
  const anyValueOption = {
    label: () => `[${$t('search.advancedSearch.values.exists')}]`,
    value: '',
  };
  return (
    model.value.entries?.map((entry) => ({
      keysOptions: aggregations.value.map((agg) => ({
        label:
          pickTranslation(
            props.resource.config.special.entriesIntegration.itemProps.find(
              (props) => props.key === agg.key
            )?.translations,
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
  model.value.entries = model.value.entries || [{ k: '', v: undefined, wc: false }];
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
            <n-form-item ignore-path-change :show-label="false">
              <n-button
                secondary
                :type="value.wc ? 'success' : undefined"
                :disabled="!value.k"
                :title="$t('search.advancedSearch.wc')"
                @click="value.wc = !value.wc"
              >
                <template #icon>
                  <n-icon :component="AsteriskIcon" />
                </template>
              </n-button>
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

<script setup lang="ts">
import type {
  KeyValueAggregations,
  TextAnnotationResourceRead,
  TextAnnotationSearchQuery,
} from '@/api';
import { dynInputCreateBtnProps } from '@/common';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { searchFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { useResourcesStore, useStateStore } from '@/stores';
import { groupAndSortItems, pickTranslation } from '@/utils';
import { NDynamicInput, NFlex, NFormItem, NSelect, NSwitch } from 'naive-ui';
import { computed, onMounted, ref } from 'vue';

const props = defineProps<{
  resource: TextAnnotationResourceRead;
  queryIndex: number;
}>();
const model = defineModel<TextAnnotationSearchQuery>({ required: true });

const state = useStateStore();
const resources = useResourcesStore();

const annoValueStyle = {
  fontFamily: props.resource.config.general.font || 'var(--font-family-content)',
};

const aggregations = ref<KeyValueAggregations>([]);
const annoOptions = computed(() => {
  const itemCfg = props.resource.config.special.annotations.annoIntegration;

  // generate general key options
  const keysOptions = groupAndSortItems(
    aggregations.value.map((agg) => ({ key: agg.key, value: agg.values })),
    itemCfg
  ).map((group, i) => ({
    label:
      pickTranslation(
        itemCfg.groups.find((g) => g.key === group.group)?.translations,
        state.locale
      ) ||
      group.group ||
      $t('common.other'),
    type: 'group',
    key: `$group_${i}_${group.group || 'ungrouped'}`,
    children: group.items.map((item) => {
      const lbl =
        pickTranslation(
          itemCfg.itemProps.find((p) => p.key === item.key)?.translations,
          state.locale
        ) || item.key;
      return {
        label: lbl || item.key,
        value: item.key,
      };
    }),
  }));

  // generate key and value select options
  const options = (model.value.anno || []).map((a) => ({
    keysOptions: keysOptions.map((group) => ({
      ...group,
      // disable children that are already in use
      children: group.children.map((c) => ({
        ...c,
        disabled: model.value.anno?.map((an) => an.k).includes(c.value),
      })),
    })),
    valuesOptions: [
      // "any value" option
      {
        label: () => $t('resources.types.textAnnotation.searchFields.any'),
        value: '',
      },
      // existing values from aggregations
      ...(aggregations.value
        // find possible values for the selected key
        .find((agg) => agg.key === a.k)
        ?.values?.filter(
          // filter out already selected values
          (v) =>
            !model.value.anno
              ?.filter((an) => an.k === a.k)
              .map((an) => an.v)
              ?.includes(v)
        )
        // map anno key-value pairs to options
        .map((v) => ({ label: v, value: v, style: annoValueStyle })) || []),
    ],
  }));

  return options;
});

function getAnnoValueSelectStyle(value?: string) {
  return value ? annoValueStyle : undefined;
}

onMounted(async () => {
  model.value.anno = model.value.anno || [{ k: '', v: undefined, wc: false }];
  aggregations.value = await resources.getAggregations(props.resource.id);
});
</script>

<template>
  <!-- ANNOTATIONS -->
  <n-form-item
    :label="$t('resources.types.textAnnotation.contentFields.annotations')"
    :show-feedback="!model.anno?.length"
    style="flex: 2 400px"
  >
    <n-dynamic-input
      v-model:value="model.anno"
      :create-button-props="dynInputCreateBtnProps"
      @create="() => ({ k: undefined, v: undefined })"
    >
      <template #default="{ value: annotationItem, index: annotationItemIndex }">
        <n-flex wrap align="flex-start" style="flex: 2">
          <!-- KEY -->
          <n-form-item
            style="flex: 2 200px"
            :show-label="false"
            ignore-path-change
            :path="`queries[${queryIndex}].rts.anno[${annotationItemIndex}].k`"
            :rule="searchFormRules.textAnnotation.annotationKey"
          >
            <n-select
              v-model:value="annotationItem.k"
              filterable
              clearable
              :options="annoOptions[annotationItemIndex].keysOptions"
              :placeholder="$t('resources.types.textAnnotation.contentFields.annotationKey')"
              @update:value="() => (annotationItem.v = '')"
            />
          </n-form-item>

          <n-flex :wrap="false" align="center" style="flex: 2 248px">
            <!-- VALUE -->
            <n-form-item
              :show-label="false"
              ignore-path-change
              :path="`queries[${queryIndex}].rts.anno[${annotationItemIndex}].v`"
              :rule="searchFormRules.textAnnotation.annotationValue"
              style="flex: 2 200px"
            >
              <n-select
                v-model:value="annotationItem.v"
                filterable
                clearable
                tag
                multiple
                :disabled="!annotationItem.k"
                :style="getAnnoValueSelectStyle(annotationItem.v)"
                :options="annoOptions[annotationItemIndex].valuesOptions"
                :placeholder="$t('common.value')"
              />
            </n-form-item>

            <!-- VALUE QUERY WILDCARDS -->
            <n-form-item :show-label="false" ignore-path-change style="flex-basis: 48px">
              <n-switch
                v-model:value="annotationItem.wc"
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
      <template
        #action="{
          index: annotationActionIndex,
          create: createAnnotation,
          remove: removeAnnotation,
        }"
      >
        <dynamic-input-controls
          :movable="false"
          :insert-disabled="annotationActionIndex >= 63"
          @remove="() => removeAnnotation(annotationActionIndex)"
          @insert="() => createAnnotation(annotationActionIndex)"
        />
      </template>
      <template #create-button-default>
        {{ $t('common.select') }}
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>

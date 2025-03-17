<script setup lang="ts">
import type {
  KeyValueAggregations,
  TextAnnotationResourceRead,
  TextAnnotationSearchQuery,
} from '@/api';
import { dynInputCreateBtnProps } from '@/common';
import NInputOsk from '@/components/NInputOsk.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { searchFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { useResourcesStore } from '@/stores';
import { NDynamicInput, NFlex, NFormItem, NSelect, NSwitch } from 'naive-ui';
import { computed, onMounted, ref } from 'vue';

const props = defineProps<{
  resource: TextAnnotationResourceRead;
  queryIndex: number;
}>();
const model = defineModel<TextAnnotationSearchQuery>({ required: true });

const resources = useResourcesStore();

const annoValueStyle = {
  fontFamily: props.resource.config.general.font || 'Tekst Content Font',
};

const aggregations = ref<KeyValueAggregations>([]);
const annoOptions = computed(() => {
  const keysOptions = aggregations.value.map((agg) => ({ label: agg.key, value: agg.key }));
  const anyValueOption = {
    label: () => $t('resources.types.textAnnotation.searchFields.any'),
    value: '',
  };
  return (
    model.value.anno?.map((a) => ({
      keysOptions,
      valuesOptions: [
        anyValueOption,
        ...(aggregations.value
          .find(
            // find possible values for the selected key
            (agg) => agg.key === a.k
          )
          ?.values?.filter(
            // filter out already selected values
            (v) =>
              !model.value.anno
                ?.filter((an) => an.k === a.k)
                .map((an) => an.v)
                ?.includes(v)
          )
          .map(
            // map anno key-value pairs to options
            (v) => ({ label: v, value: v, style: annoValueStyle })
          ) || []),
      ],
    })) || []
  );
});

function getAnnoValueSelectStyle(value?: string) {
  return value ? annoValueStyle : undefined;
}

onMounted(async () => {
  aggregations.value = await resources.getAggregations(props.resource.id);
});
</script>

<template>
  <n-flex :wrap="false" align="center" style="flex: 1 248px">
    <!-- TOKEN -->
    <n-form-item
      :label="$t('resources.types.textAnnotation.contentFields.token')"
      ignore-path-change
      :path="`queries[${queryIndex}].rts.token`"
      :rule="searchFormRules.textAnnotation.token"
      style="flex: 2"
    >
      <n-input-osk
        v-model="model.token"
        :font="resource.config.general.font || undefined"
        :osk-key="resource.config.common.osk || undefined"
        :placeholder="$t('resources.types.textAnnotation.contentFields.token')"
      />
    </n-form-item>
    <!-- TOKEN QUERY WILDCARDS -->
    <n-form-item ignore-path-change style="flex-basis: 48px">
      <n-switch
        v-model:value="model.twc"
        :round="false"
        class="b text-small"
        :title="$t('search.advancedSearch.wc')"
      >
        <template #checked>*</template>
        <template #unchecked>*</template>
      </n-switch>
    </n-form-item>
  </n-flex>

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
                tag
                filterable
                clearable
                :disabled="!annotationItem.k"
                :style="getAnnoValueSelectStyle(annotationItem.v)"
                :options="annoOptions[annotationItemIndex].valuesOptions"
                :placeholder="$t('general.value')"
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
        {{ $t('general.selectAction') }}
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>

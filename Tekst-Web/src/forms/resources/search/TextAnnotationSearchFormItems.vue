<script setup lang="ts">
import type { TextAnnotationResourceRead, TextAnnotationSearchQuery } from '@/api';
import NInputOsk from '@/components/NInputOsk.vue';
import { NInput, NSelect, NFormItem, NDynamicInput } from 'naive-ui';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { searchFormRules } from '@/forms/formRules';

const props = defineProps<{
  value: TextAnnotationSearchQuery;
  resource: TextAnnotationResourceRead;
  queryIndex: number;
}>();

const emit = defineEmits(['update:value']);

function handleUpdate(field: string, value: any) {
  emit('update:value', {
    ...props.value,
    [field]: value,
  });
}

function getAnnotationKeyOptions() {
  return (
    props.resource.aggregations
      ?.filter((agg) => !props.value.anno?.find((ann) => ann.k === agg.key))
      .map((agg) => ({ label: agg.key, value: agg.key })) || []
  );
}

function getAnnotationValueOptions(key: string) {
  if (!key) return [];
  return (
    props.resource.aggregations
      ?.find((agg) => agg.key === key)
      ?.values?.map((v) => ({ label: v, value: v })) || []
  );
}
</script>

<template>
  <!-- TOKEN -->
  <n-form-item
    :label="$t('resources.types.textAnnotation.contentFields.token')"
    ignore-path-change
    :path="`queries[${queryIndex}].rts.token`"
    :rule="searchFormRules.textAnnotation.token"
    style="flex-grow: 1; flex-basis: 200px"
  >
    <n-input-osk
      :value="value.token"
      :font="resource.config?.general?.font || undefined"
      :placeholder="$t('resources.types.textAnnotation.contentFields.token')"
      @update:value="(v) => handleUpdate('token', v)"
    />
  </n-form-item>

  <!-- ANNOTATIONS -->
  <n-form-item
    :label="$t('resources.types.textAnnotation.contentFields.annotations')"
    :show-feedback="false"
    style="flex-grow: 2; flex-basis: 400px"
  >
    <n-dynamic-input
      :value="value.anno"
      @update-value="(v) => handleUpdate('anno', v)"
      @create="() => ({ k: undefined, v: undefined })"
    >
      <template #default="{ value: annotationItem, index: annotationItemIndex }">
        <div
          style="
            display: flex;
            flex-wrap: wrap;
            flex-grow: 2;
            gap: var(--content-gap);
            align-items: flex-start;
          "
        >
          <n-form-item
            style="flex-grow: 2; flex-basis: 200px"
            :show-label="false"
            ignore-path-change
            :path="`queries[${queryIndex}].rts.anno[${annotationItemIndex}].k`"
            :rule="searchFormRules.textAnnotation.annotationKey"
          >
            <n-select
              v-model:value="annotationItem.k"
              filterable
              clearable
              :options="getAnnotationKeyOptions()"
              :placeholder="$t('resources.types.textAnnotation.contentFields.annotationKey')"
              @update:value="
                (v) =>
                  (annotationItem.v =
                    resource.aggregations?.find((agg) => agg.key === annotationItem.k)
                      ?.values?.[0] || undefined)
              "
            />
          </n-form-item>
          <n-form-item
            style="flex-grow: 2; flex-basis: 200px"
            :show-label="false"
            ignore-path-change
            :path="`queries[${queryIndex}].rts.anno[${annotationItemIndex}].v`"
            :rule="searchFormRules.textAnnotation.annotationValue"
          >
            <n-select
              v-if="!!resource.aggregations?.find((agg) => agg.key === annotationItem.k)?.values"
              v-model:value="annotationItem.v"
              filterable
              clearable
              :options="getAnnotationValueOptions(annotationItem.k)"
              :placeholder="$t('resources.types.textAnnotation.contentFields.annotationValue')"
            />
            <n-input
              v-else
              v-model:value="annotationItem.v"
              :placeholder="$t('resources.types.textAnnotation.contentFields.annotationValue')"
            />
          </n-form-item>
        </div>
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
    </n-dynamic-input>
  </n-form-item>
</template>

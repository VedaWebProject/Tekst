<script setup lang="ts">
import type { TextAnnotationContentCreate, TextAnnotationResourceRead } from '@/api';
import NInputOsk from '@/components/NInputOsk.vue';
import { NSelect, NFormItem, NDynamicInput } from 'naive-ui';
import { contentFormRules } from '@/forms/formRules';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';

const props = defineProps<{
  model: TextAnnotationContentCreate;
  resource: TextAnnotationResourceRead;
}>();

const emit = defineEmits(['update:model']);

function handleUpdate(field: string, value: any) {
  emit('update:model', {
    ...props.model,
    [field]: value,
  });
}

function getAnnotationKeyOptions() {
  return props.resource.aggregationsIndex?.map((agg) => ({ label: agg.key, value: agg.key })) || [];
}

function getAnnotationValueOptions(key?: string) {
  if (!key) return [];
  return (
    props.resource.aggregationsIndex
      ?.find((agg) => agg.key === key)
      ?.values.map((v) => ({ label: v, value: v })) || []
  );
}
</script>

<template>
  <!-- TOKENS -->
  <n-form-item :show-label="false" :show-feedback="false">
    <n-dynamic-input
      :value="model.tokens"
      :min="1"
      :max="1024"
      @create="() => ({ token: undefined, annotations: [] })"
      @update:value="(value) => handleUpdate('tokens', value)"
    >
      <template #default="{ value: tokenItem, index: tokenItemIndex }">
        <div
          style="
            display: flex;
            align-items: flex-start;
            gap: var(--content-gap);
            flex-grow: 2;
            flex-wrap: wrap;
          "
        >
          <!-- TOKEN -->
          <n-form-item
            :label="$t('resources.types.textAnnotation.contentFields.token')"
            :path="`tokens[${tokenItemIndex}].token`"
            :rule="contentFormRules.textAnnotation.token"
            ignore-path-change
            style="flex-grow: 1; flex-basis: 200px"
          >
            <n-input-osk
              v-model:value="tokenItem.token"
              :font="resource.config?.general?.font || undefined"
              :placeholder="$t('resources.types.textAnnotation.contentFields.token')"
            />
          </n-form-item>
          <!-- ANNOTATIONS -->
          <n-form-item
            :label="$t('resources.types.textAnnotation.contentFields.annotations')"
            :show-feedback="false"
            :path="`tokens[${tokenItemIndex}].annotations`"
            style="flex-grow: 2; flex-basis: 400px"
          >
            <n-dynamic-input
              v-model:value="tokenItem.annotations"
              @create="() => ({ key: undefined, value: undefined })"
            >
              <template #default="{ value: annotationItem, index: annotationItemIndex }">
                <div
                  style="
                    display: flex;
                    flex-wrap: nowrap;
                    flex-grow: 2;
                    gap: var(--content-gap);
                    align-items: flex-start;
                  "
                >
                  <n-form-item
                    style="flex-grow: 2; flex-basis: 100px"
                    :show-label="false"
                    :path="`tokens[${tokenItemIndex}].annotations[${annotationItemIndex}].key`"
                    :rule="contentFormRules.textAnnotation.annotationKey"
                    ignore-path-change
                  >
                    <n-select
                      v-model:value="annotationItem.key"
                      filterable
                      tag
                      clearable
                      :options="getAnnotationKeyOptions()"
                      :placeholder="
                        $t('resources.types.textAnnotation.contentFields.annotationKey')
                      "
                    />
                  </n-form-item>
                  <n-form-item
                    style="flex-grow: 2; flex-basis: 100px"
                    :show-label="false"
                    :path="`tokens[${tokenItemIndex}].annotations[${annotationItemIndex}].value`"
                    :rule="contentFormRules.textAnnotation.annotationValue"
                    ignore-path-change
                  >
                    <n-select
                      v-model:value="annotationItem.value"
                      filterable
                      tag
                      clearable
                      :disabled="!annotationItem.key"
                      :options="getAnnotationValueOptions(annotationItem.key)"
                      :placeholder="
                        $t('resources.types.textAnnotation.contentFields.annotationValue')
                      "
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
                  secondary
                  :movable="false"
                  :insert-disabled="annotationActionIndex >= 127"
                  @remove="() => removeAnnotation(annotationActionIndex)"
                  @insert="() => createAnnotation(annotationActionIndex)"
                />
              </template>
            </n-dynamic-input>
          </n-form-item>
        </div>
      </template>
      <template
        #action="{
          index: tokenActionIndex,
          create: createTokenItem,
          remove: removeTokenItem,
          move: moveTokenItem,
        }"
      >
        <dynamic-input-controls
          top-offset
          :move-up-disabled="tokenActionIndex === 0"
          :move-down-disabled="tokenActionIndex === model.tokens.length - 1"
          :remove-disabled="model.tokens.length <= 1"
          :insert-disabled="model.tokens.length >= 1024"
          @move-up="() => moveTokenItem('up', tokenActionIndex)"
          @move-down="() => moveTokenItem('down', tokenActionIndex)"
          @remove="() => removeTokenItem(tokenActionIndex)"
          @insert="() => createTokenItem(tokenActionIndex)"
        />
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>

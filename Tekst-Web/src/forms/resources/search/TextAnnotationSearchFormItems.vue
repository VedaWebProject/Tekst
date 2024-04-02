<script setup lang="ts">
import type { TextAnnotationResourceRead, TextAnnotationSearchQuery } from '@/api';
import NInputOsk from '@/components/NInputOsk.vue';
import { NSelect, NFormItem, NDynamicInput } from 'naive-ui';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';

const props = defineProps<{
  value: TextAnnotationSearchQuery;
  resource: TextAnnotationResourceRead;
}>();

const emit = defineEmits(['update:value']);

function handleUpdate(field: string, value: any) {
  emit('update:value', {
    ...props.value,
    [field]: value,
  });
}
</script>

<template>
  <!-- TOKEN -->
  <n-form-item
    :label="$t('resources.types.textAnnotation.contentFields.token')"
    ignore-path-change
    style="flex-grow: 1; flex-basis: 200px"
  >
    <n-input-osk
      :value="value.token"
      :font="resource.config?.general?.font || undefined"
      :placeholder="$t('resources.types.textAnnotation.contentFields.token')"
      :maxlength="512"
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
      item-style="margin-bottom: var(--content-gap)"
      @update-value="(v) => handleUpdate('anno', v)"
      @create="() => ({ key: undefined, value: undefined })"
    >
      <template #default="{ value: annotationItem }">
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
            :show-feedback="false"
            ignore-path-change
          >
            <n-select
              v-model:value="annotationItem.key"
              filterable
              clearable
              :options="[]"
              :placeholder="$t('resources.types.textAnnotation.contentFields.annotationKey')"
            />
          </n-form-item>
          <n-form-item
            style="flex-grow: 2; flex-basis: 200px"
            :show-label="false"
            :show-feedback="false"
            ignore-path-change
          >
            <n-select
              v-model:value="annotationItem.value"
              filterable
              clearable
              :disabled="!annotationItem.key"
              :options="[]"
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

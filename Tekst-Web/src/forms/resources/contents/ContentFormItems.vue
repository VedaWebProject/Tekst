<script setup lang="ts">
import type { AnyContentCreate, AnyResourceRead } from '@/api';
import { contentFormRules } from '@/forms/formRules';
import resourceContentFormItems from '@/forms/resources/contents/mappings';
import { NCollapse, NCollapseItem, NFormItem, NInput } from 'naive-ui';

defineProps<{
  resource: AnyResourceRead;
}>();

const model = defineModel<AnyContentCreate>({ required: true });

function handleUpdate(field: string, value: unknown) {
  model.value = {
    ...model.value,
    [field]: value,
  };
}
</script>

<template>
  <template v-if="model">
    <component
      :is="resourceContentFormItems[model.resourceType]"
      v-model="model"
      :resource="resource"
    />
    <n-collapse class="mb-lg">
      <n-collapse-item :title="$t('resources.types.common.label')" name="common">
        <!-- COMMENT -->
        <n-form-item
          :label="$t('resources.types.common.contentFields.comment')"
          path="comment"
          :rule="contentFormRules.common.comment"
        >
          <n-input
            type="textarea"
            :rows="3"
            :value="model.comment"
            :placeholder="$t('resources.types.common.contentFields.comment')"
            @update:value="(v) => handleUpdate('comment', v)"
          />
        </n-form-item>
        <!-- NOTES -->
        <n-form-item
          :label="$t('resources.types.common.contentFields.notes')"
          path="notes"
          :rule="contentFormRules.common.notes"
        >
          <n-input
            type="textarea"
            :rows="2"
            :value="model.notes"
            :placeholder="$t('resources.types.common.contentFields.notes')"
            @update:value="(v) => handleUpdate('notes', v)"
          />
        </n-form-item>
      </n-collapse-item>
    </n-collapse>
  </template>
</template>

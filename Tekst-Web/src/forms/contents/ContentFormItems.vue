<script setup lang="ts">
import type { AnyContentCreate } from '@/api';
import { NCollapse, NCollapseItem, NInput, NFormItem } from 'naive-ui';
import resourceContentFormItems from '@/forms/contents/mappings';

const props = defineProps<{
  model?: AnyContentCreate;
}>();

const emit = defineEmits(['update:model']);

function handleUpdate(field: string, value: any) {
  emit('update:model', {
    ...props.model,
    [field]: value,
  });
}
</script>

<template>
  <template v-if="model">
    <component
      :is="resourceContentFormItems[model.resourceType]"
      :model="model"
      @update:model="(m: Record<string, any>) => emit('update:model', { ...props.model, ...m })"
    />
    <n-collapse style="margin-bottom: var(--layout-gap)">
      <n-collapse-item :title="$t('resources.types.common.label')" name="common">
        <!-- COMMENT -->
        <n-form-item :label="$t('resources.types.common.contentFields.comment')" path="comment">
          <n-input
            type="textarea"
            :rows="3"
            :value="model.comment"
            :placeholder="$t('resources.types.common.contentFields.comment')"
            @update:value="(v) => handleUpdate('comment', v)"
          />
        </n-form-item>
        <!-- NOTES -->
        <n-form-item :label="$t('resources.types.common.contentFields.notes')" path="notes">
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

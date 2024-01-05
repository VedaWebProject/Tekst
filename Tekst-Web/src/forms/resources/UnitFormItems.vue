<script setup lang="ts">
import type { AnyUnitCreate } from '@/api';
import { NCollapse, NCollapseItem, NInput, NFormItem } from 'naive-ui';
import resourceUnitFormItems from '@/forms/resources/mappings';

const props = defineProps<{
  model?: AnyUnitCreate;
}>();

const emits = defineEmits(['update:model']);

function handleUpdate(field: string, value: any) {
  emits('update:model', {
    ...props.model,
    [field]: value,
  });
}
</script>

<template>
  <template v-if="model">
    <component
      :is="resourceUnitFormItems[model.resourceType]"
      :model="model"
      @update:model="(m: Record<string, any>) => emits('update:model', { ...props.model, ...m })"
    />
    <n-collapse style="margin-bottom: var(--layout-gap)">
      <n-collapse-item :title="$t('resources.types.common.label')" name="common">
        <!-- COMMENT -->
        <n-form-item :label="$t('resources.types.common.unitFields.comment')" path="comment">
          <n-input
            type="textarea"
            :rows="2"
            :value="model.comment"
            :placeholder="$t('resources.types.common.unitFields.comment')"
            @update:value="(v) => handleUpdate('comment', v)"
          />
        </n-form-item>
      </n-collapse-item>
    </n-collapse>
  </template>
</template>

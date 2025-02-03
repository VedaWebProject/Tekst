<script setup lang="ts">
import type { AnyContentCreate, AnyResourceRead } from '@/api';
import { contentFormRules } from '@/forms/formRules';
import resourceContentFormItems from '@/forms/resources/contents/mappings';
import { NBadge, NCollapse, NCollapseItem, NFormItem, NInput } from 'naive-ui';

defineProps<{
  resource: AnyResourceRead;
}>();

const model = defineModel<AnyContentCreate>({ required: true });
</script>

<template>
  <template v-if="model">
    <component
      :is="resourceContentFormItems[model.resourceType]"
      v-model="model"
      :resource="resource"
    />
    <n-collapse class="mb-lg">
      <n-collapse-item name="meta">
        <template #header>
          <n-badge value="!" :show="!!model.comment || !!model.notes" :offset="[10, 2]">
            {{ $t('resources.types.common.label') }}
          </n-badge>
        </template>
        <!-- COMMENT -->
        <n-form-item
          :label="$t('resources.types.common.contentFields.comment')"
          path="comment"
          :rule="contentFormRules.common.comment"
        >
          <n-input
            v-model:value="model.comment"
            type="textarea"
            :rows="3"
            :placeholder="$t('resources.types.common.contentFields.comment')"
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
            v-model:value="model.notes"
            :placeholder="$t('resources.types.common.contentFields.notes')"
          />
        </n-form-item>
      </n-collapse-item>
    </n-collapse>
  </template>
</template>

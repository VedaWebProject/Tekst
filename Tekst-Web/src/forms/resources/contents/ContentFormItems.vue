<script setup lang="ts">
import type { AnyContentCreate, AnyResourceRead } from '@/api';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
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
    <!-- CONTENT -->
    <form-section-heading :label="$t('common.content')" />
    <component
      :is="resourceContentFormItems[model.resourceType]"
      v-model="model"
      :resource="resource"
    />
    <!-- CONTENT METADATA FIELDS -->
    <n-collapse class="content-meta">
      <n-collapse-item name="meta">
        <template #header>
          <form-section-heading style="flex: 2">
            <n-badge value="!" :show="!!model.comment || !!model.notes" :offset="[8, 2]">
              {{ $t('common.meta') }}
            </n-badge>
          </form-section-heading>
        </template>
        <!-- COMMENT -->
        <n-form-item
          :label="$t('common.comment')"
          path="comment"
          :rule="contentFormRules.common.comment"
        >
          <n-input
            v-model:value="model.comment"
            type="textarea"
            :rows="3"
            :placeholder="$t('common.comment')"
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

<style scoped>
.content-meta.n-collapse
  :deep(.n-collapse-item .n-collapse-item__content-wrapper .n-collapse-item__content-inner) {
  padding-top: 0;
}
</style>

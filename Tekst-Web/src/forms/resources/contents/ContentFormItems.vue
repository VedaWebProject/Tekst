<script setup lang="ts">
import type { AnyContentCreate, AnyResourceRead } from '@/api';
import FormSection from '@/components/FormSection.vue';
import { contentFormRules } from '@/forms/formRules';
import resourceContentFormItems from '@/forms/resources/contents/mappings';
import { NBadge, NCollapse, NCollapseItem, NFormItem, NInput } from 'naive-ui';

const props = defineProps<{
  resource: AnyResourceRead;
}>();

const model = defineModel<AnyContentCreate>({ required: true });

const contentFontStyle = {
  fontFamily: props.resource.config.general.font || 'var(--font-family-content)',
};
</script>

<template>
  <form-section v-if="model" :title="$t('common.content')">
    <!-- CONTENT -->
    <component
      :is="resourceContentFormItems[model.resourceType]"
      v-model="model"
      :resource="resource"
    />
    <!-- CONTENT METADATA FIELDS -->
    <n-collapse class="content-meta">
      <n-collapse-item name="meta">
        <template #header>
          <n-badge
            value="!"
            :show="!!model.authorsComment || !!model.editorsComment"
            :offset="[8, 2]"
          >
            {{ $t('common.meta') }}
          </n-badge>
        </template>
        <!-- AUTHORS COMMENT -->
        <n-form-item
          :label="$t('resources.types.common.contentFields.authorsComment')"
          path="authorsComment"
          :rule="contentFormRules.common.authorsComment"
        >
          <n-input
            v-model:value="model.authorsComment"
            type="textarea"
            :rows="3"
            :maxlength="50000"
            show-count
            :placeholder="$t('common.comment')"
            :style="contentFontStyle"
          />
        </n-form-item>
        <!-- EDITORS COMMENT -->
        <n-form-item
          :label="$t('resources.types.common.contentFields.editorsComment')"
          path="notes"
          :rule="contentFormRules.common.editorsComment"
        >
          <n-input
            v-model:value="model.editorsComment"
            type="textarea"
            :rows="2"
            :maxlength="5000"
            show-count
            :placeholder="$t('resources.types.common.contentFields.editorsComment')"
            :style="contentFontStyle"
          />
        </n-form-item>
      </n-collapse-item>
    </n-collapse>
  </form-section>
</template>

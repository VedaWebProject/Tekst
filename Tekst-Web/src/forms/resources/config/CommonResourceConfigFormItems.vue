<script setup lang="ts">
import type { CommonResourceConfig } from '@/api';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { NSpace, NFormItem, NInputNumber, NSelect } from 'naive-ui';
import { useStateStore } from '@/stores';
import { usePlatformData } from '@/composables/platformData';
import { computed } from 'vue';
import { pickTranslation } from '@/utils';
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import { commonResourceConfigFormRules } from '@/forms/formRules';

const props = withDefaults(
  defineProps<{
    model?: CommonResourceConfig;
  }>(),
  {
    model: () => ({}),
  }
);

const emit = defineEmits(['update:model']);

const state = useStateStore();
const { pfData } = usePlatformData();

const categoryOptions = computed(
  () =>
    pfData.value?.settings.resourceCategories?.map((c) => ({
      label: pickTranslation(c.translations, state.locale) || c.key,
      value: c.key,
    })) || []
);

function handleUpdate(field: string, value: any) {
  emit('update:model', {
    ...props.model,
    [field]: value,
  });
}
</script>

<template>
  <h4>{{ $t('resources.settings.config.common.heading') }}</h4>

  <!-- CATEGORY -->
  <n-form-item :label="$t('resources.settings.config.common.category')">
    <n-select
      :value="model.category"
      clearable
      :placeholder="$t('browse.uncategorized')"
      :options="categoryOptions"
      @update:value="(v) => handleUpdate('category', v)"
    />
  </n-form-item>

  <!-- SORT ORDER -->
  <n-form-item
    :label="$t('resources.settings.config.common.sortOrder')"
    path="config.common.sortOrder"
    :rule="commonResourceConfigFormRules.sortOrder"
  >
    <n-input-number
      :min="0"
      :max="999999"
      :value="model.sortOrder"
      style="width: 100%"
      @update:value="(v) => handleUpdate('sortOrder', v)"
    />
    <help-button-widget help-key="resourceSortOrder" gap-left />
  </n-form-item>

  <n-form-item :show-label="false" :show-feedback="false">
    <n-space vertical>
      <!-- DEFAULT ACTIVE -->
      <labelled-switch
        :value="model.defaultActive"
        :label="$t('resources.settings.config.common.defaultActive')"
        @update:value="(v) => handleUpdate('defaultActive', v)"
      />
      <!-- SHOW ON PARENT LEVEL -->
      <n-space :wrap="false" align="center">
        <labelled-switch
          :value="model.showOnParentLevel"
          :label="$t('resources.settings.config.common.showOnParentLevel')"
          @update:value="(u) => handleUpdate('showOnParentLevel', u)"
        />
        <help-button-widget help-key="resourceConfigCombinedSiblings" />
      </n-space>
    </n-space>
  </n-form-item>
</template>

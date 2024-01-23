<script setup lang="ts">
import type { AnyResourceConfig } from '@/api';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { NSpace, NFormItem, NCheckbox, NInputNumber, NSelect } from 'naive-ui';
import specialConfigFormItems from '@/forms/resources/mappings';
import { useStateStore } from '@/stores';
import { usePlatformData } from '@/composables/platformData';
import { computed } from 'vue';
import { pickTranslation } from '@/utils';

const props = withDefaults(
  defineProps<{
    model?: AnyResourceConfig;
    resourceType: string;
    loading?: boolean;
  }>(),
  {
    model: () => ({
      showOnParentLevel: false,
    }),
  }
);

const emits = defineEmits(['update:model']);

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
  emits('update:model', {
    ...props.model,
    [field]: value,
  });
}
</script>

<template>
  <!---- GENERAL RESOURCE CONFIG ---->
  <h3>{{ $t('resources.settings.config.headingConfig') }}</h3>
  <h4>{{ $t('resources.headingGeneral') }}</h4>

  <!-- CATEGORY -->
  <n-form-item :label="$t('models.resource.category')">
    <n-select
      :value="model.category"
      clearable
      :placeholder="$t('browse.uncategorized')"
      :options="categoryOptions"
      @update:value="(v) => handleUpdate('category', v)"
    />
  </n-form-item>

  <!-- SORT ORDER -->
  <n-form-item path="sortOrder" :label="$t('models.resource.sortOrder')">
    <n-input-number
      :min="0"
      :value="model.sortOrder"
      style="width: 100%"
      @update:value="(v) => handleUpdate('sortOrder', v)"
    />
    <HelpButtonWidget help-key="resourceSortOrder" gap-left />
  </n-form-item>

  <n-form-item :label="$t('resources.settings.config.visibility')" :show-feedback="false">
    <!-- DEFAULT ACTIVE -->
    <n-space vertical>
      <n-checkbox
        :checked="model.defaultActive"
        @update:checked="(u) => handleUpdate('defaultActive', u)"
      >
        {{ $t('resources.settings.config.defaultActive') }}
      </n-checkbox>
      <n-space>
        <n-checkbox
          :checked="model.showOnParentLevel"
          @update:checked="(u) => handleUpdate('showOnParentLevel', u)"
        >
          {{ $t('resources.settings.config.showOnParentLevel') }}
        </n-checkbox>
        <HelpButtonWidget help-key="resourceConfigCombinedSiblings" />
      </n-space>
    </n-space>
  </n-form-item>

  <!---- RESOURCE TYPE-SPECIFIC CONFIG ---->
  <template v-for="(configModel, key) in model" :key="key">
    <component
      :is="specialConfigFormItems[key]"
      v-if="key in specialConfigFormItems"
      :model="configModel"
      @update:model="(u: any) => handleUpdate(key, u)"
    />
  </template>
</template>

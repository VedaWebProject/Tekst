<script setup lang="ts">
import { prioritizedMetadataKeys, type AnyResourceRead } from '@/api';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { resourceSettingsFormRules } from '@/forms/formRules';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';
import { $t } from '@/i18n';
import { TranslateIcon } from '@/icons';
import { NDynamicInput, NFlex, NFormItem, NIcon, NInput, NSelect } from 'naive-ui';
import { computed, h } from 'vue';

const model = defineModel<AnyResourceRead>({ required: true });

const metadataKeysOptions = computed(() =>
  prioritizedMetadataKeys.map((k) => ({
    label: () =>
      h('div', { style: 'display: flex; align-items: center; gap: 4px; padding: 4px' }, [
        h(NIcon, { component: TranslateIcon }),
        $t(`models.meta.${k}`),
      ]),
    value: k,
    disabled: model.value.meta && !!model.value.meta.find((m) => m.key === k),
  }))
);
</script>

<template>
  <form-section-heading :label="$t('resources.settings.coreInfo')" />

  <!-- TITLE -->
  <translation-form-item
    v-model="model.title"
    parent-form-path-prefix="title"
    :main-form-label="$t('models.resource.title')"
    :translation-form-label="$t('models.resource.title')"
    :translation-form-rule="resourceSettingsFormRules.titleTranslation"
    :min-items="1"
  />

  <!-- DESCRIPTION -->
  <translation-form-item
    v-model="model.description"
    parent-form-path-prefix="description"
    :main-form-label="$t('models.resource.description')"
    :translation-form-label="$t('models.resource.description')"
    :translation-form-rule="resourceSettingsFormRules.descriptionTranslation"
  />

  <!-- CITATION -->
  <n-form-item path="citation" :label="$t('models.resource.citation')">
    <n-input
      v-model:value="model.citation"
      type="text"
      :placeholder="$t('models.resource.citation')"
      @keydown.enter.prevent
    />
  </n-form-item>

  <!-- COMMENT -->
  <translation-form-item
    v-model="model.comment"
    parent-form-path-prefix="comment"
    multiline
    :max-translation-length="2000"
    :main-form-label="$t('general.comment')"
    :translation-form-label="$t('general.comment')"
    :translation-form-rule="resourceSettingsFormRules.commentTranslation"
  />

  <!-- METADATA -->
  <form-section-heading :label="$t('models.meta.modelLabel')" />
  <n-form-item :show-label="false">
    <n-dynamic-input
      v-model:value="model.meta"
      :min="0"
      :max="64"
      @create="() => ({ key: '', value: '' })"
    >
      <template #default="{ index, value: metaEntryValue }">
        <n-flex align="flex-start" wrap style="flex: 2">
          <n-form-item
            ignore-path-change
            :show-label="false"
            :path="`meta[${index}].key`"
            :rule="resourceSettingsFormRules.metaKey"
            style="flex-grow: 1; min-width: 100px"
            required
          >
            <n-select
              v-model:value="metaEntryValue.key"
              filterable
              tag
              clearable
              :options="metadataKeysOptions"
            />
          </n-form-item>
          <n-form-item
            ignore-path-changechange
            :show-label="false"
            :path="`meta[${index}].value`"
            :rule="resourceSettingsFormRules.metaValue"
            style="flex-grow: 2; min-width: 100px"
            required
          >
            <n-input
              v-model:value="metaEntryValue.value"
              :placeholder="$t('general.key')"
              @keydown.enter.prevent
            />
          </n-form-item>
        </n-flex>
      </template>
      <template #action="{ index, create, remove, move }">
        <dynamic-input-controls
          :move-up-disabled="index === 0"
          :move-down-disabled="index === model.meta.length - 1"
          :insert-disabled="model.meta.length >= 64"
          @move-up="() => move('up', index)"
          @move-down="() => move('down', index)"
          @remove="() => remove(index)"
          @insert="() => create(index)"
        />
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>

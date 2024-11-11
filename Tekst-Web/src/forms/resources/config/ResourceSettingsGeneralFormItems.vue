<script setup lang="ts">
import {
  prioritizedMetadataKeys,
  type AnyResourceRead,
} from '@/api';
import { resourceSettingsFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';
import { computed, h } from 'vue';
import {
  NSelect,
  NIcon,
  NDynamicInput,
  NFormItem,
  NInput,
  NFlex,
} from 'naive-ui';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { TranslateIcon } from '@/icons';

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

function handleUpdate(field: string, value: unknown) {
  model.value = {
    ...model.value,
    [field]: value,
  };
}
</script>

<template>
  <!-- TITLE -->
  <translation-form-item
    :model-value="model.title"
    parent-form-path-prefix="title"
    :main-form-label="$t('models.resource.title')"
    :translation-form-label="$t('models.resource.title')"
    :translation-form-rule="resourceSettingsFormRules.titleTranslation"
    :min-items="1"
    @update:model-value="(v) => handleUpdate('title', v)"
  />

  <!-- DESCRIPTION -->
  <translation-form-item
    :model-value="model.description"
    parent-form-path-prefix="description"
    :main-form-label="$t('models.resource.description')"
    :translation-form-label="$t('models.resource.description')"
    :translation-form-rule="resourceSettingsFormRules.descriptionTranslation"
    @update:model-value="(v) => handleUpdate('description', v)"
  />

  <!-- CITATION -->
  <n-form-item path="citation" :label="$t('models.resource.citation')">
    <n-input
      :value="model.citation"
      type="text"
      :placeholder="$t('models.resource.citation')"
      @keydown.enter.prevent
      @update:value="(v) => handleUpdate('citation', v)"
    />
  </n-form-item>

  <!-- COMMENT -->
  <translation-form-item
    :model-value="model.comment"
    parent-form-path-prefix="comment"
    multiline
    :max-translation-length="2000"
    :main-form-label="$t('general.comment')"
    :translation-form-label="$t('general.comment')"
    :translation-form-rule="resourceSettingsFormRules.commentTranslation"
    @update:model-value="(v) => handleUpdate('comment', v)"
  />

  <!-- METADATA -->
  <n-form-item :label="$t('models.meta.modelLabel')" :show-feedback="false">
    <n-dynamic-input
      :value="model.meta"
      :min="0"
      :max="64"
      @create="() => ({ key: '', value: '' })"
      @update:value="(v) => handleUpdate('meta', v)"
    >
      <template #default="{ index, value: metaEntryValue }">
        <n-flex align="flex-start" wrap style="flex-grow: 2">
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
              :placeholder="$t('models.meta.value')"
              @keydown.enter.prevent
            />
          </n-form-item>
        </n-flex>
      </template>
      <template #action="{ index: indexAction, create, remove, move }">
        <dynamic-input-controls
          :move-up-disabled="indexAction === 0"
          :move-down-disabled="indexAction === model.meta.length - 1"
          :insert-disabled="model.meta.length >= 64"
          @move-up="() => move('up', indexAction)"
          @move-down="() => move('down', indexAction)"
          @remove="() => remove(indexAction)"
          @insert="() => create(indexAction)"
        />
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>

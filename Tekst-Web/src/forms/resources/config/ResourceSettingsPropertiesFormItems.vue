<script setup lang="ts">
import { type AnyResourceRead } from '@/api';
import { dynInputCreateBtnProps } from '@/common';
import CollapsibleContent from '@/components/CollapsibleContent.vue';
import FormSection from '@/components/FormSection.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { resourceSettingsFormRules } from '@/forms/formRules';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';
import { $t } from '@/i18n';
import { TranslateIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { NDynamicInput, NFlex, NFormItem, NIcon, NInput, NSelect } from 'naive-ui';
import { computed, h } from 'vue';

const model = defineModel<AnyResourceRead>({ required: true });

const state = useStateStore();

const metadataKeysOptions = computed(() =>
  state.pf?.state.resMetaTranslations.map((rmt) => ({
    label: () =>
      h('div', { style: 'display: flex; align-items: center; gap: 4px; padding: 4px' }, [
        h(NIcon, { component: TranslateIcon }),
        pickTranslation(rmt.translations, state.locale),
      ]),
    value: rmt.key,
    disabled: model.value.meta && !!model.value.meta.find((m) => m.key === rmt.key),
  }))
);
</script>

<template>
  <form-section :title="$t('resources.settings.coreInfo')">
    <!-- TITLE -->
    <translation-form-item
      v-model="model.title"
      parent-form-path-prefix="title"
      :main-form-label="$t('common.title')"
      :translation-form-label="$t('common.title')"
      :translation-form-rules="resourceSettingsFormRules.titleTranslation"
      :min-items="1"
    />

    <!-- SUBTITLE -->
    <translation-form-item
      v-model="model.subtitle"
      parent-form-path-prefix="subtitle"
      :main-form-label="$t('common.subtitle')"
      :translation-form-label="$t('common.subtitle')"
      :translation-form-rules="resourceSettingsFormRules.subtitleTranslation"
    />
  </form-section>

  <!-- CITATION -->
  <form-section :title="$t('models.resource.citation')">
    <n-form-item path="citation" :show-label="false">
      <n-input
        v-model:value="model.citation"
        :placeholder="$t('models.resource.citation')"
        @keydown.enter.prevent
      />
    </n-form-item>
  </form-section>

  <!-- DESCRIPTION -->
  <form-section :title="$t('common.description')">
    <collapsible-content :height-tresh-px="240">
      <translation-form-item
        v-model="model.description"
        input-type="html"
        parent-form-path-prefix="description"
        :max-translation-length="102400"
        :translation-form-label="$t('common.description')"
        :translation-form-rules="resourceSettingsFormRules.descriptionTranslation"
      />
    </collapsible-content>
  </form-section>

  <!-- LICENSE -->
  <form-section :title="$t('models.resource.license')">
    <n-form-item path="license" :label="$t('common.name')">
      <n-input
        v-model:value="model.license"
        :placeholder="$t('common.name')"
        @keydown.enter.prevent
      />
    </n-form-item>
    <n-form-item path="licenseUrl" :label="$t('common.url')">
      <n-input
        v-model:value="model.licenseUrl"
        :placeholder="$t('common.url')"
        @keydown.enter.prevent
      />
    </n-form-item>
  </form-section>

  <!-- METADATA -->
  <form-section :title="$t('models.meta.modelLabel')">
    <n-form-item :show-label="false" :show-feedback="false">
      <n-dynamic-input
        v-model:value="model.meta"
        :min="0"
        :max="64"
        :create-button-props="dynInputCreateBtnProps"
        @create="() => ({ key: undefined, value: undefined })"
      >
        <template #default="{ index, value: metaEntryValue }">
          <n-flex align="flex-start" wrap style="flex: 2">
            <n-form-item
              ignore-path-change
              :show-label="false"
              :path="`meta[${index}].key`"
              :rule="resourceSettingsFormRules.metaKey"
              style="flex: 1 100px"
              required
            >
              <n-select
                v-model:value="metaEntryValue.key"
                filterable
                tag
                clearable
                :placeholder="$t('common.key')"
                :options="metadataKeysOptions"
              />
            </n-form-item>
            <n-form-item
              ignore-path-changechange
              :show-label="false"
              :path="`meta[${index}].value`"
              :rule="resourceSettingsFormRules.metaValue"
              style="flex: 2; min-width: 100px"
              required
            >
              <n-input
                v-model:value="metaEntryValue.value"
                :placeholder="$t('common.value')"
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
        <template #create-button-default>
          {{ $t('common.add') }}
        </template>
      </n-dynamic-input>
    </n-form-item>
  </form-section>
</template>

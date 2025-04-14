<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import type { components } from '@/api/schema';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import {
  commonResourceConfigFormRules,
  typeSpecificResourceConfigFormRules,
} from '@/forms/formRules';
import ItemIntegrationConfigFormItems from '@/forms/resources/config/ItemIntegrationConfigFormItems.vue';
import { useResourcesStore } from '@/stores';
import { NFlex, NFormItem, NInput } from 'naive-ui';
import { onMounted, ref } from 'vue';

const props = defineProps<{ resource: AnyResourceRead }>();

const model = defineModel<components['schemas']['AnnotationsConfig']>({
  required: true,
});

const resources = useResourcesStore();
const existingItemKeys = ref<string[]>([]);

onMounted(async () => {
  existingItemKeys.value = (await resources.getAggregations(props.resource.id)).map(
    (agg) => agg.key
  );
});
</script>

<template>
  <form-section-heading
    :label="$t('resources.settings.config.annotations.annoDisplayHeading', 2)"
  />

  <!-- ANNOTATION DISPLAY TEMPLATE -->
  <n-form-item
    :rule="typeSpecificResourceConfigFormRules.textAnnotation.displayTemplate"
    path="config.special.annotations.displayTemplate"
  >
    <template #label>
      <n-flex align="center">
        {{ $t('resources.settings.config.annotations.displayTemplate', 2) }}
        <help-button-widget help-key="textAnnotationDisplayTemplate" />
      </n-flex>
    </template>
    <n-input
      v-model:value="model.displayTemplate"
      type="textarea"
      rows="3"
      style="font-family: monospace"
    />
  </n-form-item>

  <!-- MULTI VALUE DELIMITER -->
  <n-form-item
    :label="$t('resources.settings.config.annotations.multiValueDelimiter')"
    :rule="typeSpecificResourceConfigFormRules.textAnnotation.multiValueDelimiter"
    path="config.special.annotations.multiValueDelimiter"
  >
    <n-input v-model:value="model.multiValueDelimiter" />
  </n-form-item>

  <!-- ANNOTATION INTEGRATION -->
  <item-integration-config-form-items
    v-model="model.annoIntegration"
    groups-model-path="config.special.annotations.annoIntegration.groups"
    item-props-model-path="config.special.annotations.annoIntegration.itemProps"
    :item-name-rules="commonResourceConfigFormRules.itemName"
    :group-name-label="$t('common.key')"
    :item-name-label="$t('common.key')"
    :existing-item-keys="existingItemKeys"
    :groups-heading="$t('common.group', 2)"
  />
</template>

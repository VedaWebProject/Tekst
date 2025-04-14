<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import type { components } from '@/api/schema';
import { commonResourceConfigFormRules } from '@/forms/formRules';
import ItemIntegrationConfigFormItems from '@/forms/resources/config/ItemIntegrationConfigFormItems.vue';
import { useResourcesStore } from '@/stores';
import { onMounted, ref } from 'vue';

const props = defineProps<{ resource: AnyResourceRead }>();
const model = defineModel<components['schemas']['ItemIntegrationConfig']>({
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
  <!-- ENTRIES INTEGRATION -->
  <item-integration-config-form-items
    v-model="model"
    groups-model-path="config.special.entriesIntegration.groups"
    item-props-model-path="config.special.entriesIntegration.itemProps"
    :item-name-rules="commonResourceConfigFormRules.itemName"
    :group-name-label="$t('common.key')"
    :item-name-label="$t('common.key')"
    :existing-item-keys="existingItemKeys"
    :groups-heading="$t('common.group', 2)"
  />
</template>

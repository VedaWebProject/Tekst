<script setup lang="ts">
import type { LocationMetadataResourceRead } from '@/api';
import type { components } from '@/api/schema';
import { commonResourceConfigFormRules } from '@/forms/formRules';
import ItemsDisplayConfigFormItems from '@/forms/resources/config/ItemsDisplayConfigFormItems.vue';
import { useResourcesStore } from '@/stores';
import { onMounted, ref } from 'vue';

const props = defineProps<{ resource: LocationMetadataResourceRead }>();

const model = defineModel<components['schemas']['LocationMetadataSpecialConfig']>({
  required: true,
});

const resources = useResourcesStore();

const existingItemNames = ref<string[]>([]);

onMounted(async () => {
  existingItemNames.value = (await resources.getAggregations(props.resource.id)).map(
    (agg) => agg.key
  );
});
</script>

<template>
  <!-- ITEM DISPLAY CONFIG -->
  <items-display-config-form-items
    v-model:groups="model.groups"
    v-model:display-props="model.displayProps"
    groups-model-path="config.locationMetadata.groups"
    displayPropsModelPath="config.locationMetadata.displayProps"
    :max-groups="64"
    :max-display-props="128"
    :item-name-rules="commonResourceConfigFormRules.itemName"
    :group-name-label="$t('general.key')"
    :item-name-label="$t('general.key')"
    :existing-item-names="existingItemNames"
    :groups-heading="$t('resources.settings.config.locationMetadata.itemGroups')"
    :display-props-heading="$t('resources.settings.config.locationMetadata.itemDisplay')"
  />
</template>

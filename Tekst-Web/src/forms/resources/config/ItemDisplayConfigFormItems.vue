<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import type { components } from '@/api/schema';
import { commonResourceConfigFormRules } from '@/forms/formRules';
import ItemsDisplayConfigFormItems from '@/forms/resources/config/ItemsDisplayConfigFormItems.vue';
import { useResourcesStore } from '@/stores';
import { onMounted, ref } from 'vue';

const props = defineProps<{ resource: AnyResourceRead }>();
const model = defineModel<components['schemas']['ItemDisplayConfig']>({
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
    groups-model-path="config.special.itemDisplay.groups"
    displayPropsModelPath="config.special.itemDisplay.displayProps"
    :max-groups="64"
    :max-display-props="128"
    :item-name-rules="commonResourceConfigFormRules.itemName"
    :group-name-label="$t('common.key')"
    :item-name-label="$t('common.key')"
    :existing-item-names="existingItemNames"
    :groups-heading="$t('resources.settings.config.itemDisplay.groups')"
    :display-props-heading="$t('resources.settings.config.itemDisplay.displayProps')"
  />
</template>

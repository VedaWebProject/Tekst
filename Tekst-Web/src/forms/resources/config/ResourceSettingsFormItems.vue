<script setup lang="ts">
import { type AnyResourceRead } from '@/api';
import AccessShareConfigFormItems from '@/forms/resources/config/AccessShareConfigFormItems.vue';
import CommonResourceConfigFormItems from '@/forms/resources/config/CommonResourceConfigFormItems.vue';
import GeneralResourceConfigFormItems from '@/forms/resources/config/GeneralResourceConfigFormItems.vue';
import ResourceSettingsPropertiesFormItems from '@/forms/resources/config/ResourceSettingsPropertiesFormItems.vue';
import SpecialResourceConfigFormItems from '@/forms/resources/config/SpecialResourceConfigFormItems.vue';
import { $t } from '@/i18n';
import { useStateStore } from '@/stores';
import { NTabPane, NTabs, type TabsInst } from 'naive-ui';
import { ref, watch } from 'vue';

const model = defineModel<AnyResourceRead>({ required: true });

const state = useStateStore();

const tabsRef = ref<TabsInst>();

watch(
  () => state.locale,
  () => {
    setTimeout(() => {
      tabsRef.value?.syncBarPosition();
    }, 100);
  }
);
</script>

<template>
  <n-tabs
    ref="tabsRef"
    type="bar"
    tab-style="font-size: var(--font-size-medium)"
    pane-class="mt-md"
  >
    <n-tab-pane :tab="$t('resources.settings.props')" name="properties">
      <!-- PROPERTIES -->
      <resource-settings-properties-form-items v-model="model" />
    </n-tab-pane>

    <n-tab-pane :tab="$t('resources.settings.config.heading')" name="configCommon">
      <!-- COMMON CONFIG -->
      <common-resource-config-form-items
        v-model="model.config.common"
        :resource-type="model.resourceType"
      />
    </n-tab-pane>

    <n-tab-pane
      :tab="$t('resources.types.' + model.resourceType + '.label')"
      name="configTypeSpecific"
    >
      <!-- GENERAL CONFIG -->
      <general-resource-config-form-items
        v-model="model.config.general"
        :resource-type="model.resourceType"
      />
      <!-- RESOURCE SPECIAL CONFIG -->
      <special-resource-config-form-items
        v-model="model.config"
        :resource-type="model.resourceType"
      />
    </n-tab-pane>

    <!-- ACCESS SHARES -->
    <n-tab-pane :tab="$t('models.resource.share')" name="access">
      <access-share-config-form-items
        v-model:shared-read="model.sharedRead"
        v-model:shared-write="model.sharedWrite"
        :resource="model"
      />
    </n-tab-pane>
  </n-tabs>
</template>

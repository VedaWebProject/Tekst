<script setup lang="ts">
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import { usePlatformData } from '@/composables/platformData';
import { useStateStore } from '@/stores';
import { NForm, NFormItem, NSelect } from 'naive-ui';
import { computed } from 'vue';

const state = useStateStore();
const { pfData } = usePlatformData();
const textOptions = computed(() =>
  pfData.value?.texts.map((t) => ({ label: t.title, value: t.id }))
);
</script>

<template>
  <n-form :model="state.searchSettingsQuick">
    <!-- TEXTS -->
    <n-form-item path="defaultOperator" :label="$t('search.settings.quick.texts')">
      <n-select
        v-model:value="state.searchSettingsQuick.texts"
        :options="textOptions"
        :placeholder="$t('search.settings.quick.textsPlaceholder')"
        clearable
        multiple
      />
    </n-form-item>

    <!-- DEFAULT OPERATOR -->
    <n-form-item path="texts" :show-label="false" :show-feedback="false">
      <labelled-switch
        v-model:value="state.searchSettingsQuick.defaultOperator"
        checked-value="AND"
        unchecked-value="OR"
        :label="$t('search.settings.quick.defaultOperator')"
      />
    </n-form-item>
  </n-form>
</template>

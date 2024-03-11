<script setup lang="ts">
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import { useStateStore } from '@/stores';
import { NForm, NFormItem } from 'naive-ui';

const state = useStateStore();
</script>

<template>
  <n-form :model="state.searchSettingsGeneral">
    <!-- STRICT SEARCH MODE -->
    <n-form-item path="strict" :show-label="false" :show-feedback="false">
      <labelled-switch
        v-model:value="state.searchSettingsGeneral.strict"
        :label="$t('search.settings.general.strict')"
      />
    </n-form-item>
  </n-form>
</template>

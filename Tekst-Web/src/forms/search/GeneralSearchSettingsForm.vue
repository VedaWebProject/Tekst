<script setup lang="ts">
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import { useSearchStore } from '@/stores';
import { NForm, NFormItem } from 'naive-ui';

const search = useSearchStore();
</script>

<template>
  <n-form :model="search.settingsGeneral">
    <!-- STRICT SEARCH MODE -->
    <n-form-item path="strict" :show-label="false" :show-feedback="false">
      <labelled-switch
        v-model:value="search.settingsGeneral.strict"
        :label="$t('search.settings.general.strict')"
      />
    </n-form-item>
  </n-form>
</template>

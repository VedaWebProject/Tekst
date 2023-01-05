<script setup lang="ts">
import { i18n, setI18nLanguage } from '@/i18n';
import { NButton, NDropdown } from 'naive-ui';
import CaretDownOutlined from '@vicons/antd/CaretDownOutlined';
import { Icon } from '@vicons/utils';
import { ref } from 'vue';

const selectedLanguage = ref(i18n.global.locale);
const options = i18n.global.availableLocales.map((l) => {
  return { label: l.toUpperCase(), key: l };
});
</script>

<template>
  <n-dropdown trigger="click" :options="options" @select="setI18nLanguage">
    <n-button>
      {{ selectedLanguage.toUpperCase() }}
      <Icon style="margin-left: 4px">
        <CaretDownOutlined />
      </Icon>
    </n-button>
  </n-dropdown>
</template>

<style scoped></style>

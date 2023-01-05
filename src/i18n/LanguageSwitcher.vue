<script setup lang="ts">
import { i18n, setI18nLanguage } from '@/i18n';
import { ref } from 'vue';

const selectedLanguage = ref(i18n.global.locale);
</script>

<template>
  <select v-model="selectedLanguage" @change="setI18nLanguage(selectedLanguage)">
    <option
      v-for="lang in $i18n.availableLocales"
      :value="lang"
      :selected="lang === selectedLanguage"
      :key="lang"
    >
      {{ lang }}
    </option>
  </select>
</template>

<style scoped></style>

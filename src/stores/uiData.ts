import { ref } from 'vue';
import { defineStore } from 'pinia';

export const useUiDataStore = defineStore('uiData', () => {
  const data: { [key: string]: any } = ref({});
  return { data };
});

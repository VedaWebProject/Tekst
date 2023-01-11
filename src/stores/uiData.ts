import { ref } from 'vue';
import { defineStore } from 'pinia';
import _get from 'lodash.get';

export interface UiData {
  [key: string]: any;
}

export const useUiDataStore = defineStore('uiData', () => {
  const data: UiData = ref({});

  async function loadUiData() {
    return fetch(`${import.meta.env.TEXTRIG_SERVER_API}/uidata`)
      .then((response) => response.json())
      .then((uiData: UiData) => {
        data.value = uiData;
      });
  }

  function get(uiDataPath: string) {
    return _get(data.value, uiDataPath, '');
  }

  return { loadUiData, get };
});

import { ref } from 'vue';
import { defineStore } from 'pinia';
import _get from 'lodash.get';
import { UidataApi } from 'textrig-ts-client';

export const useUiDataStore = defineStore('uiData', () => {
  const data = ref({});
  const uiDataApi = new UidataApi();

  async function loadUiData() {
    return uiDataApi.uidata().then((uiData) => {
      data.value = uiData;
    });
  }

  function get(uiDataPath: string) {
    return _get(data.value, uiDataPath, '');
  }

  return { loadUiData, get };
});

import { ref } from 'vue';
import { defineStore } from 'pinia';
import _get from 'lodash.get';
import { UidataApi } from 'textrig-ts-client';

export const useUiDataStore = defineStore('uiData', () => {
  const data = ref({});
  const uiDataApi = new UidataApi();

  async function loadPlatformData() {
    return uiDataApi.getPlatformData().then((platformData) => {
      data.value = platformData;
    });
  }

  function get(uiDataPath: string) {
    return _get(data.value, uiDataPath, '');
  }

  return { loadPlatformData, get };
});

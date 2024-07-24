import type {
  AdvancedSearchSettings,
  GeneralSearchSettings,
  QuickSearchSettings,
  SearchRequestBody,
} from '@/api';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { Base64 } from 'js-base64';
import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useResourcesStore } from './resources';
import { useStateStore } from './state';

export const useSearchStore = defineStore('search', () => {
  const state = useStateStore();
  const router = useRouter();
  const { message } = useMessages();
  const resources = useResourcesStore();

  const lastReq = ref<SearchRequestBody>();

  const settingsGeneral = ref<GeneralSearchSettings>({
    strict: false,
  });
  const settingsQuick = ref<QuickSearchSettings>({
    op: 'OR',
  });
  const settingsAdvanced = ref<AdvancedSearchSettings>({});

  function encodeQueryParam(requestBody?: SearchRequestBody): string | undefined {
    if (!requestBody) return undefined;
    try {
      return Base64.encode(JSON.stringify(requestBody), true);
    } catch {
      message.error($t('errors.unexpected'));
      return undefined;
    }
  }

  function decodeQueryParam(): SearchRequestBody | undefined {
    const queryParam = router.currentRoute.value.query.q?.toString();
    try {
      const decoded: SearchRequestBody = queryParam
        ? JSON.parse(Base64.decode(queryParam))
        : undefined;
      if (!decoded || !['quick', 'advanced'].includes(decoded.type)) {
        throw new Error();
      }
      return decoded;
    } catch {
      message.error($t('search.results.msgInvalidRequest'));
      return undefined;
    }
  }

  watch(
    () => resources.dataHash,
    () => {
      lastReq.value = undefined;
    }
  );

  // set quick search settings text selection to current text on working text change
  watch(
    () => state.text?.id,
    (after) => {
      if (after) {
        settingsQuick.value.txt = [after];
      }
    },
    { immediate: true }
  );

  return {
    settingsGeneral,
    settingsQuick,
    settingsAdvanced,
    encodeQueryParam,
    decodeQueryParam,
    lastReq,
  };
});

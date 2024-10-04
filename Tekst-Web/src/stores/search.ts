import {
  POST,
  type AdvancedSearchSettings,
  type GeneralSearchSettings,
  type QuickSearchSettings,
  type SearchRequestBody,
  type SearchResults,
  type SortingPreset,
} from '@/api';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { Base64 } from 'js-base64';
import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useStateStore } from './state';
import { usePlatformData } from '@/composables/platformData';
import _cloneDeep from 'lodash.clonedeep';

export const useSearchStore = defineStore('search', () => {
  const state = useStateStore();
  const { pfData } = usePlatformData();
  const router = useRouter();
  const { message } = useMessages();

  const req = ref<SearchRequestBody>();

  const settingsGeneral = ref<GeneralSearchSettings>({
    strict: false,
  });
  const settingsQuick = ref<QuickSearchSettings>({
    op: 'OR',
    re: false,
  });
  const settingsAdvanced = ref<AdvancedSearchSettings>({});

  const paginationDefaults = () => ({ pg: 1, pgs: 10 });
  const pagination = ref(paginationDefaults());
  const sorting = ref<SortingPreset>();

  const loading = ref(false);
  const error = ref(false);
  const results = ref<SearchResults>();

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
      if (!decoded) throw new Error();
      pagination.value = {
        pg: decoded.gen.pgn?.pg || paginationDefaults().pg,
        pgs: decoded.gen.pgn?.pgs || paginationDefaults().pgs,
      };
      sorting.value = decoded.gen.sort || undefined;
      if (decoded.type === 'quick') {
        settingsQuick.value = decoded.qck;
      } else if (decoded.type === 'advanced') {
        settingsAdvanced.value = decoded.adv;
      } else {
        throw new Error();
      }
      return decoded;
    } catch {
      return undefined;
    }
  }

  function processQuery() {
    pagination.value.pg = 1;
    try {
      const q = decodeQueryParam();
      if (!q || !['quick', 'advanced'].includes(q.type)) {
        throw new Error();
      }
      return q;
    } catch {
      message.error($t('search.results.msgInvalidRequest'));
    }
  }

  async function search(resetPage?: boolean, query?: SearchRequestBody) {
    loading.value = true;
    error.value = false;
    results.value = undefined;
    if (query) {
      settingsGeneral.value.pgn = pagination.value;
      settingsGeneral.value.sort = sorting.value;
      req.value = {
        ...query,
        gen: settingsGeneral.value,
      };
    } else {
      req.value = processQuery();
    }
    if (!req.value) {
      error.value = true;
      loading.value = false;
      return;
    }
    // change to search results view
    router.push({
      name: 'searchResults',
      query: {
        q: encodeQueryParam(req.value),
      },
    });
    // reset page
    if (resetPage) {
      pagination.value.pg = paginationDefaults().pg;
    }
    // search
    const { data, error: e } = await POST('/search', {
      body: {
        ...req.value,
        gen: settingsGeneral.value,
      },
    });
    if (!e) {
      results.value = data;
    } else {
      error.value = true;
    }
    loading.value = false;
  }

  function handleSortingChange() {
    search(true, {
      ...req.value,
      gen: {
        ...req.value?.gen,
        sort: sorting.value,
      },
    } as SearchRequestBody);
  }

  function turnPage(direction: 'previous' | 'next') {
    if (!results.value) return;
    const currPage = pagination.value.pg;
    pagination.value.pg =
      direction === 'previous'
        ? Math.max(1, pagination.value.pg - 1)
        : Math.min(
            pagination.value.pg + 1,
            Math.floor(results.value.totalHits / pagination.value.pg) + 1
          );
    currPage !== pagination.value.pg && search();
  }

  function browse() {
    const q = _cloneDeep(req.value);
    if (!q) return;
    q.gen.pgn = { pg: 1, pgs: 100 };
    console.log(q);
  }

  // set quick search settings text selection to all texts on working text change
  watch(
    () => state.text?.id,
    () => {
      settingsQuick.value.txt = pfData.value?.texts.map((t) => t.id);
    },
    { immediate: true }
  );

  return {
    settingsGeneral,
    settingsQuick,
    settingsAdvanced,
    handleSortingChange,
    req,
    sorting,
    pagination,
    search,
    turnPage,
    loading,
    error,
    results,
    browse,
  };
});

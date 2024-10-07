import {
  POST,
  type SearchResults,
  type SortingPreset,
  type SearchPagination,
  type ResourceSearchQuery,
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

type GeneralSearchSettings = {
  pgn: SearchPagination;
  sort: SortingPreset;
  strict: boolean;
};

type QuickSearchSettings = {
  op: 'OR' | 'AND';
  re: boolean;
  txt?: string[];
};

type AdvancedSearchSettings = {};

type QuickSearchRequest = {
  type: 'quick';
  q: string;
  gen: GeneralSearchSettings;
  qck: QuickSearchSettings;
};

type AdvancedSearchRequest = {
  type: 'advanced';
  q: ResourceSearchQuery[];
  gen: GeneralSearchSettings;
  adv: AdvancedSearchSettings;
};

type SearchRequest = QuickSearchRequest | AdvancedSearchRequest;

const DEFAULT_SEARCH_SETTINGS = {
  gen: {
    pgn: { pg: 1, pgs: 10 },
    sort: 'relevance',
    strict: false,
  } as GeneralSearchSettings,
  qck: {
    op: 'OR',
    re: false,
  } as QuickSearchSettings,
  adv: {} as AdvancedSearchSettings,
};

const DEFAULT_SEARCH_REQUEST_BODY: QuickSearchRequest = {
  type: 'quick',
  q: '',
  gen: DEFAULT_SEARCH_SETTINGS.gen,
  qck: DEFAULT_SEARCH_SETTINGS.qck,
};

export const useSearchStore = defineStore('search', () => {
  const state = useStateStore();
  const { pfData } = usePlatformData();
  const router = useRouter();
  const { message } = useMessages();

  const settingsGeneral = ref<GeneralSearchSettings>(DEFAULT_SEARCH_SETTINGS.gen);
  const settingsQuick = ref<QuickSearchSettings>(DEFAULT_SEARCH_SETTINGS.qck);
  const settingsAdvanced = ref<AdvancedSearchSettings>(DEFAULT_SEARCH_SETTINGS.adv);
  const currentRequest = ref<SearchRequest>();

  const loading = ref(false);
  const error = ref(false);
  const results = ref<SearchResults>();

  function encodeReqInUrl(requestBody?: SearchRequest): string | undefined {
    if (!requestBody) return undefined;
    try {
      return Base64.encode(JSON.stringify(requestBody), true);
    } catch {
      message.error($t('errors.unexpected'));
      return undefined;
    }
  }

  function decodeReqFromUrl(): SearchRequest {
    try {
      const q = router.currentRoute.value.query.q?.toString();
      const decoded: SearchRequest = q ? JSON.parse(Base64.decode(q)) : undefined;
      if (!decoded) throw new Error();
      settingsGeneral.value = decoded.gen || DEFAULT_SEARCH_SETTINGS.gen;
      settingsGeneral.value.pgn.pg = 1;
      settingsGeneral.value.pgn.pgs = 10;
      if (decoded.type === 'quick') {
        settingsQuick.value = decoded.qck || DEFAULT_SEARCH_SETTINGS.qck;
      } else if (decoded.type === 'advanced') {
        settingsAdvanced.value = decoded.adv || DEFAULT_SEARCH_SETTINGS.adv;
      } else {
        return DEFAULT_SEARCH_REQUEST_BODY;
      }
      return decoded;
    } catch {
      return DEFAULT_SEARCH_REQUEST_BODY;
    }
  }

  async function searchQuick(
    q: string,
    pg: number = settingsGeneral.value.pgn.pg,
    pgs: number = settingsGeneral.value.pgn.pgs
  ) {
    const req: QuickSearchRequest = {
      type: 'quick',
      q,
      gen: { ...settingsGeneral.value, pgn: { pg, pgs } },
      qck: settingsQuick.value,
    };
    gotoSearchResultsView(req);
    await _search(req);
  }

  async function searchAdvanced(
    q: ResourceSearchQuery[],
    pg: number = settingsGeneral.value.pgn.pg,
    pgs: number = settingsGeneral.value.pgn.pgs
  ) {
    const req: AdvancedSearchRequest = {
      type: 'advanced',
      q,
      gen: { ...settingsGeneral.value, pgn: { pg, pgs } },
      adv: settingsAdvanced.value,
    };
    gotoSearchResultsView(req);
    await _search(req);
  }

  async function searchFromUrl() {
    if (currentRequest.value) return;
    await _search(decodeReqFromUrl());
  }

  async function searchSecondary() {
    await _search({
      ...(currentRequest.value || DEFAULT_SEARCH_REQUEST_BODY),
      gen: settingsGeneral.value,
    });
  }

  function gotoSearchResultsView(req: SearchRequest) {
    router.push({
      name: 'searchResults',
      query: {
        q: encodeReqInUrl(req),
      },
    });
  }

  async function _search(req: SearchRequest) {
    loading.value = true;
    error.value = false;
    results.value = undefined;
    currentRequest.value = req;
    // search
    const { data, error: e } = await POST('/search', {
      body: req,
    });
    if (!e) {
      results.value = data;
    } else {
      error.value = true;
    }
    loading.value = false;
  }

  function turnPage(direction: 'previous' | 'next') {
    if (!results.value) return;
    const currPage = settingsGeneral.value.pgn.pg;
    settingsGeneral.value.pgn.pg =
      direction === 'previous'
        ? Math.max(1, settingsGeneral.value.pgn.pg - 1)
        : Math.min(
            settingsGeneral.value.pgn.pg + 1,
            Math.floor(results.value.totalHits / settingsGeneral.value.pgn.pg) + 1
          );
    currPage !== settingsGeneral.value.pgn.pg && searchSecondary();
  }

  function browse() {
    const q = _cloneDeep(currentRequest.value);
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
    searchQuick,
    searchAdvanced,
    searchFromUrl,
    searchSecondary,
    turnPage,
    currentRequest,
    loading,
    error,
    results,
    browse,
  };
});

import type { PublicUserSearchFilters, UserReadPublic } from '@/api';
import { GET } from '@/api';
import { useDebounceFn } from '@vueuse/core';
import { ref, watch, type Ref } from 'vue';

export function usePublicUserSearch(queryRef: Ref<PublicUserSearchFilters>) {
  const users = ref<UserReadPublic[]>([]);
  const error = ref(false);
  const loading = ref(false);
  const total = ref(0);

  async function load(query: PublicUserSearchFilters) {
    users.value = [];
    total.value = 0;
    error.value = false;

    if (!query.q && !query.emptyOk) {
      loading.value = false;
      return;
    }

    loading.value = true;

    const { data, error: err } = await GET('/users/public', { params: { query: query } });

    if (!err) {
      users.value = data.users || [];
      total.value = data.total || 0;
    } else {
      error.value = true;
    }
    loading.value = false;
  }

  const debouncedLoad = useDebounceFn(load, 500);

  watch(
    queryRef,
    (newQuery) => {
      loading.value = true;
      debouncedLoad(newQuery);
    },
    { immediate: true, deep: true }
  );

  return {
    users,
    total,
    loading,
    error,
    load,
  };
}

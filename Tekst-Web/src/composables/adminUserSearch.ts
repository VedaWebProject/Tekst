import type { UserRead, UserSearchFilters } from '@/api';
import { GET } from '@/api';
import { useDebounceFn } from '@vueuse/core';
import { ref, watch, type Ref } from 'vue';

export function useAdminUserSearch(filtersRef: Ref<UserSearchFilters>) {
  const users = ref<Array<UserRead>>([]);
  const total = ref(0);
  const error = ref(false);
  const loading = ref(false);

  async function load(filters: UserSearchFilters) {
    loading.value = true;
    users.value = [];
    total.value = 0;
    error.value = false;

    const { data, error: e } = await GET('/users', {
      params: {
        query: filters,
      },
    });

    if (!e) {
      users.value = data.users || [];
      total.value = data.total || 0;
    } else {
      error.value = true;
    }
    loading.value = false;
  }

  const debouncedLoad = useDebounceFn(load, 500);

  watch(
    filtersRef,
    (newFilters) => {
      loading.value = true;
      debouncedLoad(newFilters);
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

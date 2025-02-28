import { GET, type UserReadPublic } from '@/api';
import { isRef, ref, unref, watchEffect, type Ref } from 'vue';

const _cache = new Map<string, UserReadPublic>();

export function useUser(usernameOrId: string | Ref<string>) {
  const user = ref<UserReadPublic | null>(null);
  const error = ref(false);

  async function fetchUserData() {
    error.value = false;
    const unoid = unref(usernameOrId);
    if (!unoid) {
      error.value = true;
      return;
    }
    user.value = _cache.get(unoid) || null;
    if (!!user.value) return;

    const { data, error: err } = await GET('/users/public/{user}', {
      params: { path: { user: unoid } },
    });

    if (!err) {
      _cache.set(unoid, data);
      user.value = data;
    } else {
      error.value = true;
    }
  }

  if (isRef(usernameOrId)) {
    watchEffect(fetchUserData);
  } else {
    fetchUserData();
  }

  return { user, error };
}

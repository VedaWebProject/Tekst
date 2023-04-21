import { ref, isRef, unref, watchEffect, type Ref } from 'vue';
import { configureApi } from './openApiConfig';
import { PlatformApi, type UserReadPublic } from '@/openapi';
import type { AxiosResponse } from 'axios';

export function useProfile(username: string | Ref) {
  const user = ref<UserReadPublic | null>(null);
  const error = ref(false);
  const platformApi = configureApi(PlatformApi);

  function fetchProfileData() {
    user.value = null;
    error.value = false;
    platformApi
      .getPublicUserInfo({ username: unref(username) })
      .then((response: AxiosResponse<UserReadPublic, any>) => response.data)
      .then((u: UserReadPublic) => (user.value = u))
      .catch(() => (error.value = true));
  }

  if (isRef(username)) {
    watchEffect(fetchProfileData);
  } else {
    fetchProfileData();
  }

  return { user, error };
}

import { ref } from 'vue';
import { GET } from '@/api';
import type { LockKey } from '@/api';
import { useTimeoutPoll } from '@vueuse/core';

export function useLocks(
  lockKey: LockKey,
  options?: {
    initiallyLocked?: boolean;
    interval?: number;
    immediate?: boolean;
    stopWhenUnlocked?: boolean;
    onUnlocked?: () => void;
  }
) {
  const locked = ref(!!options?.initiallyLocked);
  const { resume, pause } = useTimeoutPoll(
    async () => {
      const { data } = await GET('/admin/locks/{key}', {
        params: {
          path: {
            key: lockKey,
          },
        },
      });
      locked.value = !!data;
      if (!locked.value) {
        if (options?.stopWhenUnlocked) {
          pause();
        }
        options?.onUnlocked?.();
      }
    },
    options?.interval || 2000,
    { immediate: options?.immediate }
  );

  return { locked, start: resume, stop: pause };
}

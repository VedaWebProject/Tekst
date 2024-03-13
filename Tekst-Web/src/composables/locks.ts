import { ref } from 'vue';
import { GET } from '@/api';
import type { LockKey } from '@/api';
import { useTimeoutPoll } from '@vueuse/core';

export function useLocks(options?: { interval?: number; immediate?: boolean }) {
  const locks = ref<{ [key: string]: boolean }>({});
  const { resume, pause } = useTimeoutPoll(
    async () => {
      const { data, error } = await GET('/platform/locks');
      if (!error) {
        locks.value = data;
      }
    },
    options?.interval || 3000,
    { immediate: options?.immediate }
  );

  return { locks, start: resume, stop: pause };
}

export function useLock(
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
      const { data } = await GET('/platform/locks/{key}', {
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
    options?.interval || 3000,
    { immediate: options?.immediate }
  );

  return { locked, start: resume, stop: pause };
}

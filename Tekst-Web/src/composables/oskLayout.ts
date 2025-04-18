import { STATIC_PATH } from '@/common';
import { $t } from '@/i18n';
import { ref, unref, watchEffect, type Ref } from 'vue';
import { useMessages } from './messages';

type OskLayout = { char: string; shift?: string }[][][];
const _cache = new Map<string, OskLayout>();

export function useOskLayout(oskKey: Ref<string | null | undefined>) {
  const oskLayout = ref<OskLayout>();
  const error = ref(false);
  const loading = ref(false);

  async function load(key?: string | null) {
    loading.value = true;
    error.value = false;

    if (!key) {
      oskLayout.value = undefined;
      error.value = true;
      loading.value = false;
      return;
    }

    if (_cache.has(key)) {
      oskLayout.value = _cache.get(key);
      loading.value = false;
      return;
    }

    const path = `${STATIC_PATH}/osk/${key}.json`;

    try {
      const response = await fetch(path);
      const data = await response.json();
      _cache.set(key, data);
      oskLayout.value = data;
    } catch {
      oskLayout.value = undefined;
      error.value = true;
      const { message } = useMessages();
      message.error($t('osk.msgErrorLoading', { layout: key }), path);
    } finally {
      loading.value = false;
    }
  }

  watchEffect(() => {
    load(unref(oskKey));
  });

  return {
    oskLayout,
    loading,
    error,
  };
}

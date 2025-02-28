import { STATIC_PATH } from '@/common';
import { $t } from '@/i18n';
import { ref, unref, watchEffect, type Ref } from 'vue';
import { useMessages } from './messages';

export function useOskLayout(oskModeKey: Ref<string | null | undefined>) {
  const oskLayout = ref<{ char: string; shift?: string }[][][]>();
  const error = ref(false);
  const loading = ref(false);

  async function load(key?: string | null) {
    oskLayout.value = undefined;

    if (key == null) {
      loading.value = false;
      error.value = true;
      return;
    }

    loading.value = true;
    error.value = false;
    const path = `${STATIC_PATH}/osk/${key}.json`;

    try {
      const response = await fetch(path);
      oskLayout.value = await response.json();
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
    loading.value = true;
    load(unref(oskModeKey));
  });

  return {
    oskLayout,
    loading,
    error,
  };
}

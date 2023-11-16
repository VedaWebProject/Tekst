import { ref } from 'vue';
import { $t } from '@/i18n';
import { useRoute, useRouter } from 'vue-router';
import { useStateStore } from '@/stores';
import { useAsyncQueue } from '@vueuse/core';
import { useMessages } from '@/messages';
import { usePlatformData } from '@/platformData';
import { computed } from 'vue';

interface InitStep {
  info: () => string;
  action: (success: boolean) => Promise<boolean>;
}

export function useInitializeApp() {
  // resources
  const state = useStateStore();
  const { message } = useMessages();
  const { pfData, loadPlatformData, getSegment } = usePlatformData();
  const route = useRoute();
  const router = useRouter();

  const initialized = ref(false);
  const error = computed(() => result.map((r) => r.data).includes(false));

  const initSteps: InitStep[] = [
    // set global loading state, start process
    {
      info: () => '',
      action: async () => {
        state.startGlobalLoading();
        return true;
      },
    },
    // load platform data from server
    {
      info: () => $t('init.platformData'),
      action: async (success: boolean) => {
        try {
          await loadPlatformData();
          return success;
        } catch (e) {
          message.warning($t('errors.platformData'));
          return false;
        }
      },
    },
    // set up initial working text
    {
      info: () => $t('init.workingText'),
      action: async (success: boolean) => {
        state.text =
          pfData.value?.texts.find((t) => t.slug === route.params.text) ||
          pfData.value?.texts.find((t) => t.slug == localStorage.getItem('text')) ||
          pfData.value?.texts.find((t) => t.id == pfData.value?.settings.defaultTextId) ||
          pfData.value?.texts[0];

        if (route.meta.isTextSpecific) {
          router.replace({
            name: route.name || 'browse',
            params: {
              ...route.params,
              text: state.text?.slug,
            },
            query: route.query,
          });
        }
        return success;
      },
    },
    // apply special system segments
    {
      info: () => $t('init.systemSegments'),
      action: async (success: boolean) => {
        // HTML body end
        const bodyEnd = await getSegment('systemBodyEnd');
        if (bodyEnd) document.body.insertAdjacentHTML('beforeend', bodyEnd.html);
        // HTML head end
        const headEnd = await getSegment('systemHeadEnd');
        if (headEnd) document.head.insertAdjacentHTML('beforeend', headEnd.html);
        return success;
      },
    },
    // finish global loading, end process
    {
      info: () => $t('init.ready'),
      action: async (success: boolean) => {
        initialized.value = true;
        state.globalLoadingProgress = 1;
        state.finishGlobalLoading(800, 200);
        return success;
      },
    },
  ];

  const { result } = useAsyncQueue(
    initSteps.map((step: InitStep, i: number) => (success: boolean) => {
      state.globalLoadingMsg = step.info();
      state.globalLoadingProgress = i / initSteps.length;
      return step.action(success);
    })
  );

  return {
    initialized,
    error,
  };
}

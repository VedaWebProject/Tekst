import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { useMessagesStore, usePlatformStore, useStateStore } from '@/stores';
import { useAsyncQueue } from '@vueuse/core';

interface InitStep {
  info: string;
  action: (success: boolean) => Promise<boolean>;
}

export function useInitializeApp() {
  // resources
  const state = useStateStore();
  const messages = useMessagesStore();
  const pf = usePlatformStore();
  const route = useRoute();
  const router = useRouter();
  const { t } = useI18n({ useScope: 'global' });

  const initialized = ref(false);

  const initSteps: InitStep[] = [
    // set global loading state, start process
    {
      info: '',
      action: async () => {
        state.startGlobalLoading();
        return true;
      },
    },
    // load i18n data from server
    {
      info: t('init.serverI18n'),
      action: async (success: boolean) => {
        try {
          await state.setLocale();
          return success;
        } catch (e) {
          messages.warning(t('errors.serverI18n'));
          console.error(e);
          return false;
        }
      },
    },
    // load platform data from server
    {
      info: t('init.platformData'),
      action: async (success: boolean) => {
        try {
          await pf.loadPlatformData();
          return success;
        } catch (e) {
          messages.warning(t('errors.platformData'));
          console.error(e);
          return false;
        }
      },
    },
    // set up initial working text
    {
      info: t('init.workingText'),
      action: async (success: boolean) => {
        state.text =
          pf.data?.texts.find((t) => t.slug === route.params.text) ||
          pf.data?.texts.find((t) => t.slug == localStorage.getItem('text')) ||
          pf.data?.texts.find((t) => t.id == pf.data?.settings.defaultTextId) ||
          pf.data?.texts[0];

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
    // finish global loading, end process
    {
      info: '',
      action: async (success: boolean) => {
        initialized.value = true;
        state.globalLoadingProgress = 1;
        state.finishGlobalLoading(200, 200);
        return success;
      },
    },
  ];

  const { result } = useAsyncQueue(
    initSteps.map((step: InitStep, i: number) => (success: boolean) => {
      state.globalLoadingMsg = step.info;
      state.globalLoadingProgress = i / initSteps.length;
      return step.action(success);
    })
  );

  return {
    initialized,
    error: !result,
  };
}

import { $t } from '@/i18n';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore, useResourcesStore, useStateStore } from '@/stores';
import { useAsyncQueue, useStyleTag } from '@vueuse/core';
import { useMessages } from '@/composables/messages';
import { usePlatformData } from '@/composables/platformData';
import { STATIC_PATH } from '@/common';

interface InitStep {
  info: () => string;
  action: (success: boolean) => Promise<boolean>;
}

export function useInitializeApp() {
  // resources
  const state = useStateStore();
  const auth = useAuthStore();
  const resources = useResourcesStore();
  const { message } = useMessages();
  const { pfData, loadPlatformData, getSegment } = usePlatformData();
  const route = useRoute();
  const router = useRouter();

  const initSteps: InitStep[] = [
    // set global loading state, load platform data from server
    {
      info: () => '',
      action: async (success: boolean = true) => {
        startInit();
        try {
          await loadPlatformData();
          await state.setLocale(localStorage.getItem('locale') || undefined);
          return success;
        } catch (e) {
          message.error($t('errors.loadData'));
          return false;
        }
      },
    },
    // load existing session
    {
      info: () => $t('init.loadSessionData'),
      action: async (success: boolean = true) => {
        await auth.loadExistingSession();
        return success;
      },
    },
    // load resources data from server
    {
      info: () => $t('init.loadResources'),
      action: async (success: boolean = true) => {
        try {
          await resources.load();
          return success;
        } catch (e) {
          message.error($t('errors.loadData'));
          return false;
        }
      },
    },
    // set up initial working text
    {
      info: () => $t('init.workingText'),
      action: async (success: boolean = true) => {
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
      action: async (success: boolean = true) => {
        // HTML body end
        const bodyEnd = await getSegment('systemBodyEnd');
        if (bodyEnd) document.body.insertAdjacentHTML('beforeend', bodyEnd.html);
        // HTML head end
        const headEnd = await getSegment('systemHeadEnd');
        if (headEnd) document.head.insertAdjacentHTML('beforeend', headEnd.html);
        return success;
      },
    },
    // load custom fontface definitions
    {
      info: () => $t('init.customFonts'),
      action: async (success: boolean = true) => {
        try {
          const response = await fetch(`${STATIC_PATH}/fonts.css`);
          useStyleTag(await response.text(), { id: 'custom-fonts' });
        } catch {
          // do sweet FA
        }
        // it's okay if this didn't work - the CSS file might or might not exist
        return success;
      },
    },
    // finish global loading, end process
    {
      info: () => $t('init.ready'),
      action: async (success: boolean = true) => {
        state.init.initialized = true;
        state.init.progress = 1;
        finishInit(800, 200);
        return success;
      },
    },
  ];

  function startInit() {
    state.init.loading = true;
  }

  async function finishInit(delayMs: number = 0, resetLoadingDataDelayMs: number = 0) {
    await new Promise((resolve) => setTimeout(resolve, delayMs));
    state.init.loading = false;
    await new Promise((resolve) => setTimeout(resolve, resetLoadingDataDelayMs));
    state.init.stepMsg = '';
    state.init.progress = 0;
  }

  useAsyncQueue(
    initSteps.map((step: InitStep, i: number) => async (success: boolean) => {
      state.init.stepMsg = step.info();
      state.init.progress = i / initSteps.length;
      state.init.error = state.init.error || success === false;
      await new Promise((resolve) => setTimeout(resolve, 200)); // misdemeanor
      return await step.action(success);
    })
  );
}

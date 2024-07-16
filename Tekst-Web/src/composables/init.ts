import { ref } from 'vue';
import { $t } from '@/i18n';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore, useResourcesStore, useStateStore } from '@/stores';
import { useAsyncQueue, useStyleTag } from '@vueuse/core';
import { useMessages } from '@/composables/messages';
import { usePlatformData } from '@/composables/platformData';
import { computed } from 'vue';
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

  const initialized = ref(false);
  const error = computed(() => result.map((r) => r.data).includes(false));

  const initSteps: InitStep[] = [
    // set global loading state, load platform data from server
    {
      info: () => '',
      action: async (success: boolean) => {
        state.startInitLoading();
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
      action: async (success: boolean) => {
        await auth.loadUserData();
        return success;
      },
    },
    // load resources data from server
    {
      info: () => $t('init.loadResources'),
      action: async (success: boolean) => {
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
    // load custom fontface definitions
    {
      info: () => $t('init.customFonts'),
      action: async (success: boolean) => {
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
      action: async (success: boolean) => {
        initialized.value = true;
        state.initLoadingProgress = 1;
        state.finishInitLoading(800, 200);
        return success;
      },
    },
  ];

  const { result } = useAsyncQueue(
    initSteps.map((step: InitStep, i: number) => async (success: boolean) => {
      state.initLoadingMsg = step.info();
      state.initLoadingProgress = i / initSteps.length;
      await new Promise((resolve) => setTimeout(resolve, 200)); // misdemeanor
      return await step.action(success);
    })
  );

  return {
    initialized,
    error,
  };
}

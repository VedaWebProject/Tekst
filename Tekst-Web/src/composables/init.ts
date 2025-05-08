import { GET } from '@/api';
import { useMessages } from '@/composables/messages';
import { usePlatformData } from '@/composables/platformData';
import env from '@/env';
import { $t } from '@/i18n';
import { useAuthStore, useResourcesStore, useStateStore } from '@/stores';
import { delay } from '@/utils';
import { useAsyncQueue, useStyleTag } from '@vueuse/core';
import { useRoute, useRouter } from 'vue-router';

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
  const { loadPlatformData, getSegment } = usePlatformData();
  const route = useRoute();
  const router = useRouter();

  const initSteps: InitStep[] = [
    // set global loading state, load client init data from server
    // (platform data, user, ...)
    {
      info: () => '',
      action: async (success: boolean = true) => {
        state.init.loading = true;
        // load client data
        const { data, error } = await GET('/platform/web-init');
        try {
          if (!error) {
            loadPlatformData(data.platform);
            auth.user = data.user || undefined;
            state.init.authChecked = true;
            await state.setLocale(data.user?.locale || undefined);
            return success;
          } else {
            throw Error();
          }
        } catch {
          await state.setLocale(); // load default locale for further messages
          message.error($t('errors.loadData'));
          return false;
        }
      },
    },
    // load resources data from server
    {
      info: () => $t('init.loadResources'),
      action: async (success: boolean = true) => {
        try {
          await resources.load();
          return success;
        } catch {
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
          state.textBySlug(route.params.textSlug?.toString()) ||
          state.textBySlug(state.textSlug) ||
          state.defaultText;
        if (route.params.hasOwnProperty('textSlug') && state.text?.slug !== route.params.textSlug) {
          router.replace({
            params: {
              textSlug: state.text?.slug,
            },
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
      info: () => $t('init.fonts'),
      action: async (success: boolean = true) => {
        try {
          const response = await fetch(`${env.STATIC_PATH}/fonts.css`);
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
        await delay(500); // delay end of init process for loading initial view in bg
        state.init.loading = false;
        state.init.stepMsg = '';
        state.init.progress = 0;
        return success;
      },
    },
  ];

  useAsyncQueue(
    initSteps.map((step: InitStep, i: number) => async (success: boolean) => {
      state.init.stepMsg = step.info();
      state.init.progress = (i + 1) / initSteps.length;
      state.init.error = state.init.error || success === false;
      return await step.action(success);
    })
  );
}

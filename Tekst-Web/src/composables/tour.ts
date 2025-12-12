import { usePlatformData } from '@/composables/platformData';
import { $t } from '@/i18n';
import { delay } from '@/utils';
import { driver, type Driver, type DriveStep } from 'driver.js';
import 'driver.js/dist/driver.css';
import { ref } from 'vue';
import { useRouter, type RouteLocationRaw } from 'vue-router';

type TourStep = DriveStep & {
  key?: string;
  index: number;
  route?: RouteLocationRaw;
  element?: string;
  title?: () => string;
  text?: () => string;
  before?: () => Promise<void>;
  after?: () => Promise<void>;
};

const pf = usePlatformData();
const platformName = pf.pfData.value?.state.platformName ?? 'Tekst';

const steps: TourStep[] = [
  {
    title: () => $t('tour.intro.title', { platformName }),
    text: () => $t('tour.intro.text', { platformName }),
  },
  {
    key: 'helpButtons',
    route: 'browse',
    title: () => $t('tour.helpButtons.title'),
    text: () => $t('tour.helpButtons.text'),
  },
  {
    route: 'browse',
    title: () => $t('tour.browseView.title'),
    text: () => $t('tour.browseView.text'),
  },
  {
    key: 'browseTextSelect',
    route: 'browse',
    title: () => $t('tour.browseTextSelect.title'),
    text: () => $t('tour.browseTextSelect.text'),
  },
  {
    key: 'browseNav',
    route: 'browse',
    title: () => $t('tour.browseNav.title'),
    text: () => $t('tour.browseNav.text'),
  },
  {
    key: 'browseFocus',
    route: 'browse',
    title: () => $t('tour.browseFocus.title'),
    text: () => $t('tour.browseFocus.text'),
  },
  {
    key: 'browseResourceSelect',
    route: 'browse',
    title: () => $t('tour.browseResourceSelect.title'),
    text: () => $t('tour.browseResourceSelect.text'),
  },
  {
    key: 'browseBackTop',
    route: 'browse',
    title: () => $t('tour.browseBackTop.title'),
    text: () => $t('tour.browseBackTop.text'),
    before: async () => window.scrollTo(0, document.body.scrollHeight),
  },
  {
    key: 'quickSearch',
    title: () => $t('tour.quickSearch.title'),
    text: () => $t('tour.quickSearch.text'),
    before: async () => window.scrollTo(0, 0),
  },
  {
    key: 'quickSearchSettings',
    title: () => $t('tour.quickSearchSettings.title'),
    text: () => $t('tour.quickSearchSettings.text'),
    before: async () => window.scrollTo(0, 0),
  },
  {
    key: 'quickSearchHelp',
    title: () => $t('tour.quickSearchHelp.title'),
    text: () => $t('tour.quickSearchHelp.text'),
    before: async () => window.scrollTo(0, 0),
  },
].map((s, i) => ({
  ...s,
  index: i,
  element: s.key ? `[data-tour-key="${s.key}"]` : undefined,
  popover: {
    title: s.title?.(),
    description: s.text?.(),
  },
}));

export function useGuidedTour() {
  const router = useRouter();

  const stepTransition = async (oldStep: TourStep, newStep?: TourStep) => {
    await oldStep.after?.();
    if (!newStep) return;
    if (newStep.route && router.currentRoute.value.name !== router.resolve(newStep.route).name) {
      await router.push(newStep.route);
    }
    await newStep.before?.();
    let waitedMs = 0;
    while (newStep.element != null && !document.querySelector(newStep.element)) {
      await delay(100);
      waitedMs += 100;
      if (waitedMs > 5000) {
        console.error(
          `Target element ${newStep.element?.toString()} not found for tour step "${newStep.popover?.title}"`
        );
        break;
      }
    }
  };

  const driverObj = ref<Driver>();

  const start = () => {
    driverObj.value = driver({
      steps,
      allowKeyboardControl: false,
      overlayColor: '#000',
      overlayOpacity: 0.5,
      showProgress: true,
      progressText: '{{current}}/{{total}}',
      disableActiveInteraction: true,
      showButtons: ['next', 'previous'],
      stageRadius: 8,
      nextBtnText: $t('tour.next'),
      prevBtnText: $t('tour.prev'),
      doneBtnText: $t('common.close'),
      onNextClick: async (_el, step, _opts) => {
        const tourStep = step as TourStep;
        await stepTransition(step as TourStep, steps[tourStep.index + 1]);
        driverObj.value?.moveNext();
      },
      onPrevClick: async (_el, step, _opts) => {
        const tourStep = step as TourStep;
        await stepTransition(step as TourStep, steps[tourStep.index - 1]);
        driverObj.value?.movePrevious();
      },
      onDestroyed: () => {
        driverObj.value = undefined;
      },
    });
    driverObj.value.drive();
  };

  return { start };
}

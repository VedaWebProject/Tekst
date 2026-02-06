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
  during?: () => Promise<void>;
  after?: () => Promise<void>;
};

const pf = usePlatformData();
const platformName = pf.pfData.value?.state.platformName ?? 'Tekst';

const _openHamburgerMenu = async () => {
  window.scrollTo(0, 0);
  const hamburgerBtn = document.getElementById('hamburger-btn');
  if (hamburgerBtn) {
    hamburgerBtn.click();
    await delay(250);
  }
};

const _closeHamburgerMenu = async () => {
  const drawerCloseButton = document.querySelector('.n-drawer-header__close') as HTMLElement | null;
  if (drawerCloseButton) {
    drawerCloseButton.click();
    await delay(250);
  }
};

const getSteps = () =>
  [
    {
      title: () => $t('tour.intro.title', { platformName }),
      text: () => $t('tour.intro.text', { platformName }),
    },
    {
      key: 'browseNavBtn',
      title: () => $t('tour.browseNavBtn.title'),
      text: () => $t('tour.browseNavBtn.text'),
      before: _openHamburgerMenu,
      after: _closeHamburgerMenu,
    },
    {
      route: { name: 'browse' },
      title: () => $t('tour.browseView.title'),
      text: () => $t('tour.browseView.text'),
    },
    {
      key: 'browseTextSelect',
      route: { name: 'browse' },
      title: () => $t('tour.browseTextSelect.title'),
      text: () => $t('tour.browseTextSelect.text'),
      before: async () => {
        window.scrollTo(0, 0);
      },
    },
    {
      key: 'browseNav',
      route: { name: 'browse' },
      title: () => $t('tour.browseNav.title'),
      text: () => $t('tour.browseNav.text'),
    },
    {
      key: 'browseFocus',
      route: { name: 'browse' },
      title: () => $t('tour.browseFocus.title'),
      text: () => $t('tour.browseFocus.text'),
      during: async () => {
        document.getElementById('focus-view-toggle')?.click();
        await delay(1000);
        document.getElementById('focus-view-toggle')?.click();
        await delay(1000);
        document.getElementById('focus-view-toggle')?.click();
        await delay(1000);
        document.getElementById('focus-view-toggle')?.click();
      },
    },
    {
      key: 'browseResourceDrawer',
      route: { name: 'browse' },
      title: () => $t('tour.browseResourceDrawer.title'),
      text: () => $t('tour.browseResourceDrawer.text'),
    },
    {
      route: { name: 'browse' },
      title: () => $t('tour.browseResourceDrawerOpen.title'),
      text: () => $t('tour.browseResourceDrawerOpen.text'),
      before: async () => {
        (
          document.querySelector('[data-tour-key="browseResourceDrawer"]') as HTMLElement | null
        )?.click();
        await delay(250);
      },
      after: async () => {
        (document.querySelector('.n-drawer-header__close') as HTMLElement | null)?.click();
        await delay(250);
      },
    },
    {
      key: 'quickSearch',
      title: () => $t('tour.quickSearch.title'),
      text: () => $t('tour.quickSearch.text'),
      before: async () => {
        window.scrollTo(0, 0);
      },
    },
    {
      key: 'quickSearchSettings',
      title: () => $t('tour.quickSearchSettings.title'),
      text: () => $t('tour.quickSearchSettings.text'),
      before: async () => {
        window.scrollTo(0, 0);
      },
    },
    {
      key: 'quickSearchHelp',
      title: () => $t('tour.quickSearchHelp.title'),
      text: () => $t('tour.quickSearchHelp.text'),
      before: async () => {
        window.scrollTo(0, 0);
      },
    },
    {
      key: 'helpButtons',
      title: () => $t('tour.helpButtons.title'),
      text: () => $t('tour.helpButtons.text'),
      before: async () => {
        window.scrollTo(0, 0);
      },
    },
    {
      route: { name: 'help' },
      title: () => $t('tour.helpOverview.title'),
      text: () => $t('tour.helpOverview.text'),
      before: async () => {
        window.scrollTo(0, 0);
      },
    },
    {
      key: 'searchNavBtn',
      title: () => $t('tour.searchNavBtn.title'),
      text: () => $t('tour.searchNavBtn.text'),
      before: _openHamburgerMenu,
      after: _closeHamburgerMenu,
    },
    {
      route: { name: 'search' },
      title: () => $t('tour.searchView.title'),
      text: () => $t('tour.searchView.text'),
    },
    {
      key: 'resourcesNavBtn',
      title: () => $t('tour.resourcesNavBtn.title'),
      text: () => $t('tour.resourcesNavBtn.text'),
      before: _openHamburgerMenu,
      after: _closeHamburgerMenu,
    },
    {
      route: { name: 'resources' },
      title: () => $t('tour.resourcesView.title'),
      text: () => $t('tour.resourcesView.text'),
    },
    {
      key: 'themeSwitcher',
      title: () => $t('tour.themeSwitcher.title'),
      text: () => $t('tour.themeSwitcher.text'),
      before: _openHamburgerMenu,
      during: async () => {
        document.getElementById('theme-mode-switcher')?.click();
        await delay(800);
        document.getElementById('theme-mode-switcher')?.click();
      },
      after: _closeHamburgerMenu,
    },
    {
      route: { name: 'browse' },
      title: () => $t('tour.outro.title'),
      text: () => $t('tour.outro.text'),
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

  const stepTransition = async (oldStep?: TourStep, newStep?: TourStep) => {
    await oldStep?.after?.();
    if (!newStep) return;
    if (newStep.route) {
      const targetRoute = router.resolve(newStep.route);
      if (router.currentRoute.value.name !== targetRoute.name) {
        await router.push(targetRoute);
      }
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
    const steps = getSteps();
    driverObj.value = driver({
      steps,
      allowKeyboardControl: true,
      overlayColor: '#000',
      overlayOpacity: 0.3,
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
        await stepTransition(tourStep, steps[tourStep.index + 1]);
        driverObj.value?.moveNext();
      },
      onPrevClick: async (_el, step, _opts) => {
        const tourStep = step as TourStep;
        await stepTransition(tourStep, steps[tourStep.index - 1]);
        driverObj.value?.movePrevious();
      },
      onDestroyed: () => {
        driverObj.value = undefined;
      },
      onHighlighted: async (_el, step, _opts) => {
        const tourStep = step as TourStep;
        await tourStep.during?.();
      },
    });
    stepTransition(undefined, steps[0]);
    driverObj.value.drive();
  };

  return { start };
}

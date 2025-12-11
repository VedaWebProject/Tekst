import type { RouteLocationRaw } from 'vue-router';
import { usePlatformData } from './composables/platformData';
import { $t } from './i18n';

type TourStep = {
  key: string;
  route?: RouteLocationRaw;
  title?: () => string;
  text?: () => string;
  before?: () => Promise<void>;
  after?: () => Promise<void>;
};

const pf = usePlatformData();
const platformName = pf.pfData.value?.state.platformName ?? 'Tekst';

const steps: TourStep[] = [
  {
    key: 'intro',
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
    key: 'browseView',
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
];

export default steps;

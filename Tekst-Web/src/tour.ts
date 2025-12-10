import { usePlatformData } from './composables/platformData';
import { $t } from './i18n';

type TourStep = {
  key: string;
  routeName?: string;
  title?: () => string;
  content?: () => string;
  before?: () => Promise<void>;
  after?: () => Promise<void>;
};

const pf = usePlatformData();
const platformName = pf.pfData.value?.state.platformName ?? 'Tekst';

const steps: TourStep[] = [
  {
    key: 'intro',
    routeName: 'home',
    title: () => $t('help.tour.introTitle', { platformName }),
    content: () => $t('help.tour.introText', { platformName }),
  },
  // {
  //   key: 'searchSettings',
  //   routeName: 'search',
  //   title: () => 'These are the search settings!',
  //   content: () => $t('errors.loginUserNotVerified'),
  //   before: async () => console.log('BEFORE STEP 1!'),
  //   after: async () => console.log('AFTER STEP 1!'),
  // },
];

export default steps;

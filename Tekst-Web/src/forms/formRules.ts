import { resourceTypes, type Translation } from '@/api';
import { $t, localeProfiles } from '@/i18n';
import type { FormItemRule } from 'naive-ui';

function requiredStringRule(
  inputLabel: () => string,
  trigger?: FormItemRule['trigger']
): FormItemRule {
  return {
    required: true,
    message: () =>
      $t('forms.rulesFeedback.isRequired', {
        x: inputLabel(),
      }),
    trigger,
  };
}

function minMaxCharsRule(
  min: number,
  max: number,
  trigger?: FormItemRule['trigger']
): FormItemRule {
  return {
    validator: (_: FormItemRule, value: string) =>
      (min <= 0 && !value) || (!!value && value.length >= min && value.length <= max),
    message: () => $t('forms.rulesFeedback.minMaxChars', { min, max }),
    trigger,
  };
}

export const commonFormRules: Record<string, FormItemRule[]> = {
  locale: [requiredStringRule(() => $t('common.language'), 'blur')],
};

export const accountFormRules: Record<string, FormItemRule[]> = {
  email: [
    requiredStringRule(() => $t('models.user.email'), 'input'),
    {
      validator: (_: FormItemRule, value: string) => !!value && /^.+@.+\.\w+$/.test(value),
      message: () => $t('models.user.formRulesFeedback.emailInvalid'),
      trigger: 'input',
    },
  ],
  username: [
    requiredStringRule(() => $t('models.user.username'), 'blur'),
    minMaxCharsRule(4, 16, 'blur'),
    {
      validator: (_: FormItemRule, value: string) => !!value && /^[a-zA-Z0-9\-_]*$/.test(value),
      message: () => $t('models.user.formRulesFeedback.usernameChars'),
      trigger: 'blur',
    },
  ],
  password: [
    requiredStringRule(() => $t('models.user.password'), 'blur'),
    {
      validator: (_: FormItemRule, value: string) => !!value && value.length >= 8,
      message: () => $t('forms.rulesFeedback.minChars', { min: 8 }),
      trigger: ['input', 'blur'],
    },
    {
      validator: (_: FormItemRule, value: string) =>
        !!value && /[a-z]/.test(value) && /[a-z]/.test(value) && /\d/.test(value),
      message: () => $t('models.user.formRulesFeedback.passwordChars'),
      trigger: ['input', 'blur'],
    },
  ],
  passwordRepeat: [
    {
      required: true,
      message: () => $t('models.user.formRulesFeedback.passwordRepReq'),
      trigger: 'blur',
    },
  ],
  name: [requiredStringRule(() => $t('common.name'), 'blur'), minMaxCharsRule(1, 64, 'blur')],
  affiliation: [
    requiredStringRule(() => $t('models.user.affiliation'), 'blur'),
    minMaxCharsRule(1, 180, 'blur'),
  ],
  avatarUrl: [minMaxCharsRule(0, 1024, 'blur')],
  bio: [minMaxCharsRule(0, 2000, 'blur')],
  loginEmail: [requiredStringRule(() => $t('models.user.email'), 'input')],
  loginPassword: [requiredStringRule(() => $t('models.user.password'), 'input')],
};

export const textFormRules: Record<string, FormItemRule[]> = {
  title: [requiredStringRule(() => $t('common.title'), 'blur'), minMaxCharsRule(1, 64, 'blur')],
  subtitleTranslation: [
    requiredStringRule(() => $t('common.subtitle'), 'blur'),
    minMaxCharsRule(1, 512, 'blur'),
  ],
  subtitleLocale: [requiredStringRule(() => $t('common.language'), 'blur')],
  slug: [
    requiredStringRule(() => $t('models.text.slug'), 'blur'),
    minMaxCharsRule(1, 16, 'blur'),
    {
      validator: (_: FormItemRule, value: string) => !!value && /^[a-z0-9]+$/.test(value),
      message: () => $t('models.text.formRulesFeedback.slugChars'),
      trigger: ['input', 'blur'],
    },
  ],
  levels: [
    {
      validator: (_: FormItemRule, value: Translation[]) =>
        !!value && Array.isArray(value) && value.length >= 1 && value.length <= 32,
      message: () => $t('forms.rulesFeedback.minMaxItems', { min: 1, max: 32 }),
      trigger: 'blur',
    },
  ],
  levelTranslation: [
    requiredStringRule(() => $t('common.level'), 'blur'),
    minMaxCharsRule(1, 32, 'blur'),
  ],
  defaultLevel: [
    {
      validator: (_: FormItemRule, value: number) => value != null && value >= 0,
      message: () => $t('models.text.formRulesFeedback.defaultLevelRange'),
      trigger: 'blur',
    },
  ],
  locDelim: [
    requiredStringRule(() => $t('models.text.locDelim'), 'blur'),
    minMaxCharsRule(1, 3, 'blur'),
  ],
  resourceCategoryKey: [
    requiredStringRule(() => $t('common.key'), 'blur'),
    minMaxCharsRule(1, 16, 'blur'),
  ],
  resourceCategoryTranslation: [
    requiredStringRule(() => $t('common.key'), 'blur'),
    minMaxCharsRule(1, 32, 'blur'),
  ],
};

export const locationFormRules: Record<string, FormItemRule[]> = {
  label: [requiredStringRule(() => $t('common.label'), 'blur'), minMaxCharsRule(1, 256, 'blur')],
  aliases: [
    {
      validator: (_: FormItemRule, value: string[] | null) =>
        value == null || (Array.isArray(value) && value.length <= 16),
      message: () => $t('forms.rulesFeedback.minMaxItems', { min: 0, max: 16 }),
      trigger: 'blur',
    },
  ],
};

export const correctionFormRules: Record<string, FormItemRule[]> = {
  note: [
    requiredStringRule(() => $t('browse.contents.widgets.correctionNote.lblNote'), 'blur'),
    minMaxCharsRule(1, 2000, 'blur'),
  ],
};

export const systemSegmentFormRules: Record<string, FormItemRule[]> = {
  title: [requiredStringRule(() => $t('common.title'), 'blur'), minMaxCharsRule(0, 32, 'blur')],
  key: [requiredStringRule(() => $t('common.key'), 'blur')],
  locale: [requiredStringRule(() => $t('common.language'), 'blur')],
  html: [
    requiredStringRule(() => $t('common.content'), 'blur'),
    minMaxCharsRule(1, 1048576, 'blur'),
  ],
};

export const infoSegmentFormRules: Record<string, FormItemRule[]> = {
  title: systemSegmentFormRules.title,
  key: [
    requiredStringRule(() => $t('common.key'), 'blur'),
    minMaxCharsRule(1, 32, 'blur'),
    {
      validator: (_: FormItemRule, value: string) => !!value && /^[a-zA-Z0-9\-_]+$/.test(value),
      message: () => $t('models.segment.formRulesFeedback.keyChars'),
      trigger: ['input', 'blur'],
    },
    {
      validator: (_: FormItemRule, value: string) => !!value && !value.startsWith('system'),
      message: () => $t('models.segment.formRulesFeedback.systemPrefixReserved'),
      trigger: 'blur',
    },
  ],
  locale: systemSegmentFormRules.locale,
  html: systemSegmentFormRules.html,
};

export const platformSettingsFormRules: Record<string, FormItemRule[]> = {
  platformName: [
    requiredStringRule(() => $t('models.platformSettings.platformName'), 'blur'),
    minMaxCharsRule(1, 32, 'blur'),
  ],
  platformSubtitleTranslation: [minMaxCharsRule(1, 128, 'blur')],
  availableLocales: [
    {
      validator: (_: FormItemRule, value: string[]) =>
        !!value &&
        value.length >= 1 &&
        value.length <= localeProfiles.length &&
        !value.find((v) => !localeProfiles.filter((lp) => lp.key === v).length),
      message: () => $t('forms.rulesFeedback.minMaxItems', { min: 1, max: localeProfiles.length }),
      trigger: 'blur',
    },
  ],
  navEntryTranslation: [minMaxCharsRule(1, 42, 'blur')],
  registerIntroTextTranslation: [minMaxCharsRule(1, 5000, 'blur')],
  oskModeKey: [requiredStringRule(() => $t('common.key'), 'blur'), minMaxCharsRule(1, 32, 'blur')],
  oskModeName: [
    requiredStringRule(() => $t('common.name'), 'blur'),
    minMaxCharsRule(1, 32, 'blur'),
  ],
  fontName: [requiredStringRule(() => $t('common.name'), 'blur'), minMaxCharsRule(1, 32, 'blur')],
};

export const resourceSettingsFormRules: Record<string, FormItemRule[]> = {
  titleTranslation: [
    requiredStringRule(() => $t('common.title'), 'blur'),
    minMaxCharsRule(1, 64, 'blur'),
  ],
  subtitleTranslation: [
    requiredStringRule(() => $t('common.subtitle'), 'blur'),
    minMaxCharsRule(1, 512, 'blur'),
  ],
  citation: [minMaxCharsRule(0, 4096, 'blur')],
  descriptionTranslation: [
    requiredStringRule(() => $t('common.description'), 'blur'),
    minMaxCharsRule(1, 102400, 'blur'),
  ],
  metaKey: [requiredStringRule(() => $t('common.key'), 'blur'), minMaxCharsRule(1, 16, 'blur')],
  metaValue: [
    requiredStringRule(() => $t('common.value'), 'blur'),
    minMaxCharsRule(1, 128, 'blur'),
  ],
  resourceType: [
    requiredStringRule(() => $t('models.resource.resourceType'), 'blur'),
    {
      validator: (_: FormItemRule, value: string) =>
        !!value && resourceTypes.map((rt) => rt.name).includes(value),
      message: () =>
        $t('forms.rulesFeedback.mustBeOneOf', {
          x: $t('models.resource.resourceType'),
          values: resourceTypes.map((rt) => rt.name).join(', '),
        }),
      trigger: 'blur',
    },
  ],
  level: [
    {
      required: true,
      type: 'number',
      message: () =>
        $t('forms.rulesFeedback.isRequired', {
          x: $t('common.level'),
        }),
      trigger: 'blur',
    },
  ],
};

export const commonResourceConfigFormRules: Record<string, FormItemRule[]> = {
  sortOrder: [
    {
      required: true,
      type: 'number',
      message: () =>
        $t('forms.rulesFeedback.isRequired', {
          x: $t('resources.settings.config.general.sortOrder'),
        }),
      trigger: 'blur',
    },
    {
      validator: (_: FormItemRule, value: number) =>
        Number.isInteger(value) && value >= 0 && value <= 1000,
      message: '0-1000',
      trigger: 'blur',
    },
  ],
  itemName: [requiredStringRule(() => $t('common.name')), minMaxCharsRule(1, 32, 'blur')],
  itemGroupNameRequired: [
    requiredStringRule(() => $t('common.group')),
    minMaxCharsRule(1, 32, 'blur'),
  ],
  itemGroupName: [minMaxCharsRule(0, 32, 'blur')],
  itemsDisplayTranslation: [
    requiredStringRule(() => $t('common.translation')),
    minMaxCharsRule(1, 128, 'blur'),
  ],
};

export const focusViewConfigFormRules: Record<string, FormItemRule[]> = {
  delimiter: [
    requiredStringRule(() => $t('resources.settings.config.focusView.delimiter'), 'blur'),
    minMaxCharsRule(1, 3, 'blur'),
  ],
};

export const searchReplacementsConfigFormRules: Record<string, FormItemRule[]> = {
  pattern: [
    requiredStringRule(() => $t('resources.settings.config.searchReplacements.pattern'), 'blur'),
    minMaxCharsRule(1, 64, 'blur'),
  ],
  replacement: [minMaxCharsRule(0, 64, 'blur')],
};

export const contentCssConfigFormRules: Record<string, FormItemRule[]> = {
  prop: [
    requiredStringRule(() => $t('resources.settings.config.contentCss.prop'), 'blur'),
    minMaxCharsRule(1, 256, 'blur'),
  ],
  value: [requiredStringRule(() => $t('common.value'), 'blur'), minMaxCharsRule(1, 256, 'blur')],
};

export const typeSpecificResourceConfigFormRules: Record<string, Record<string, FormItemRule[]>> = {
  textAnnotation: {
    displayTemplate: [minMaxCharsRule(0, 4096, 'blur')],
    multiValueDelimiter: [
      requiredStringRule(
        () => $t('resources.settings.config.annotations.multiValueDelimiter'),
        'blur'
      ),
      minMaxCharsRule(1, 3, 'blur'),
    ],
    annotationGroupKey: [
      requiredStringRule(() => $t('common.key', 1), 'blur'),
      minMaxCharsRule(1, 16, 'blur'),
    ],
    annotationGroupTranslation: [
      requiredStringRule(
        () => $t('resources.settings.config.annotations.annotationGroup', 1),
        'blur'
      ),
      minMaxCharsRule(1, 32, 'blur'),
    ],
  },
  apiCall: {
    dep: [requiredStringRule(() => $t('common.url'), 'blur'), minMaxCharsRule(1, 2083, 'blur')],
    js: [minMaxCharsRule(0, 102400, 'blur')],
  },
};

export const contentFormRules: Record<string, Record<string, FormItemRule[]>> = {
  common: {
    authorsComment: [minMaxCharsRule(0, 50000, 'blur')],
    editorsComment: [minMaxCharsRule(0, 5000, 'blur')],
    optionalUrl: [minMaxCharsRule(0, 2083, 'blur')],
    caption: [minMaxCharsRule(0, 8192, 'blur')],
  },
  plainText: {
    text: [
      requiredStringRule(() => $t('resources.types.plainText.contentFields.text'), 'blur'),
      minMaxCharsRule(1, 102400, 'blur'),
    ],
  },
  richText: {
    html: [
      requiredStringRule(() => $t('resources.types.richText.contentFields.html'), 'blur'),
      minMaxCharsRule(1, 102400, 'blur'),
    ],
  },
  textAnnotation: {
    token: [
      requiredStringRule(() => $t('resources.types.textAnnotation.contentFields.token'), 'blur'),
      minMaxCharsRule(1, 4096, 'blur'),
    ],
    annotationKey: [
      requiredStringRule(
        () => $t('resources.types.textAnnotation.contentFields.annotationKey'),
        'blur'
      ),
      minMaxCharsRule(1, 32, 'blur'),
    ],
    annotationValue: [
      {
        validator: (_: FormItemRule, value: string[]) => !!value && Array.isArray(value),
        message: () =>
          $t('forms.rulesFeedback.isRequired', {
            x: $t('common.value'),
          }),
        trigger: 'change',
      },
      {
        validator: (_: FormItemRule, value: string[]) =>
          !!value && value.length >= 1 && value.length <= 64,
        message: () => $t('forms.rulesFeedback.minMaxItems', { min: 1, max: 64 }),
        trigger: 'change',
      },
      {
        validator: (_: FormItemRule, value: string[]) =>
          !!value && value.every((item) => item.length >= 1 && item.length <= 256),
        message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 256 }),
        trigger: 'change',
      },
    ],
  },
  locationMetadata: {
    key: [requiredStringRule(() => $t('common.key'), 'blur'), minMaxCharsRule(1, 32, 'blur')],
    value: [
      {
        validator: (_: FormItemRule, value: string[]) => !!value && Array.isArray(value),
        message: () =>
          $t('forms.rulesFeedback.isRequired', {
            x: $t('common.value'),
          }),
        trigger: 'change',
      },
      {
        validator: (_: FormItemRule, value: string[]) =>
          !!value && value.length >= 1 && value.length <= 64,
        message: () => $t('forms.rulesFeedback.minMaxItems', { min: 1, max: 64 }),
        trigger: 'change',
      },
      {
        validator: (_: FormItemRule, value: string[]) =>
          !!value && value.every((item) => item.length >= 1 && item.length <= 256),
        message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 256 }),
        trigger: 'change',
      },
    ],
  },
  audio: {
    url: [requiredStringRule(() => $t('common.url'), 'blur'), minMaxCharsRule(1, 2083, 'blur')],
  },
  images: {
    url: [requiredStringRule(() => $t('common.url'), 'blur'), minMaxCharsRule(1, 2083, 'blur')],
  },
  externalReferences: {
    url: [requiredStringRule(() => $t('common.url'), 'blur'), minMaxCharsRule(1, 2083, 'blur')],
    title: [
      requiredStringRule(
        () => $t('resources.types.externalReferences.contentFields.title'),
        'blur'
      ),
      minMaxCharsRule(1, 128, 'blur'),
    ],
    description: [minMaxCharsRule(0, 4096, 'blur')],
    altRef: [minMaxCharsRule(0, 512, 'blur')],
  },
  apiCall: {
    key: [requiredStringRule(() => $t('common.key'), 'blur'), minMaxCharsRule(1, 32, 'blur')],
    endpoint: [
      requiredStringRule(() => $t('resources.types.apiCall.contentFields.endpoint'), 'blur'),
      minMaxCharsRule(1, 2083, 'blur'),
    ],
    contentType: [minMaxCharsRule(0, 64, 'blur')],
    queryString: [
      requiredStringRule(() => $t('resources.types.apiCall.contentFields.queryString'), 'blur'),
      minMaxCharsRule(1, 2083, 'blur'),
    ],
    body: [
      requiredStringRule(() => $t('resources.types.apiCall.contentFields.body'), 'blur'),
      minMaxCharsRule(1, 102400, 'blur'),
    ],
    transformContext: [
      minMaxCharsRule(0, 10240, 'blur'),
      {
        validator: (_: FormItemRule, value: string) => {
          try {
            if (!value) return true;
            JSON.parse(value);
            return true;
          } catch {
            return false;
          }
        },
        message: () => $t('resources.types.apiCall.contentFields.transformContextJsonError'),
        trigger: 'blur',
      },
    ],
  },
};

export const searchFormRules: Record<string, Record<string, FormItemRule[]>> = {
  common: {
    authorsComment: [minMaxCharsRule(0, 512, 'blur')],
  },
  plainText: {
    text: [minMaxCharsRule(0, 512, 'blur')],
  },
  richText: {
    html: [minMaxCharsRule(0, 512, 'blur')],
  },
  textAnnotation: {
    token: [minMaxCharsRule(0, 512, 'blur')],
    annotationKey: [
      requiredStringRule(
        () => $t('resources.types.textAnnotation.contentFields.annotationKey'),
        'blur'
      ),
      minMaxCharsRule(1, 32, 'blur'),
    ],
    annotationValue: [minMaxCharsRule(0, 256, 'blur')],
  },
  locationMetadata: {
    key: [requiredStringRule(() => $t('common.key'), 'blur'), minMaxCharsRule(1, 32, 'blur')],
    value: [minMaxCharsRule(0, 256, 'blur')],
  },
  audio: {
    caption: [minMaxCharsRule(0, 512, 'blur')],
  },
  images: {
    caption: [minMaxCharsRule(0, 512, 'blur')],
  },
  externalReferences: {
    caption: [minMaxCharsRule(0, 512, 'blur')],
  },
};

export const bookmarkFormRules: Record<string, FormItemRule[]> = {
  comment: [minMaxCharsRule(0, 1000, 'blur')],
};

export const wysiwygEditorFormRules: Record<string, FormItemRule[]> = {
  imageUrl: [minMaxCharsRule(0, 2083, undefined)],
  linkUrl: [minMaxCharsRule(0, 2083, undefined)],
};

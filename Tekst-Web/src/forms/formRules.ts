import type { FormItemRule } from 'naive-ui';
import { $t, localeProfiles } from '@/i18n';
import { resourceTypes } from '@/api';

function requiredRule(inputLabel: string, trigger?: FormItemRule['trigger']): FormItemRule {
  return {
    required: true,
    message: () =>
      $t('forms.rulesFeedback.isRequired', {
        x: inputLabel,
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
    validator: (rule: FormItemRule, value: string) =>
      (min <= 0 && !value) || (!!value && value.length >= min && value.length <= max),
    message: () => $t('forms.rulesFeedback.minMaxChars', { min, max }),
    trigger,
  };
}

export const translationFormRules: Record<string, FormItemRule[]> = {
  locale: [requiredRule($t('models.locale.modelLabel'), 'blur')],
};

export const accountFormRules: Record<string, FormItemRule[]> = {
  email: [
    requiredRule($t('models.user.email'), 'input'),
    {
      validator: (rule: FormItemRule, value: string) => !!value && /^.+@.+\.\w+$/.test(value),
      message: () => $t('models.user.formRulesFeedback.emailInvalid'),
      trigger: 'input',
    },
  ],
  username: [
    requiredRule($t('models.user.username'), 'blur'),
    minMaxCharsRule(4, 16, 'blur'),
    {
      validator: (rule: FormItemRule, value: string) => !!value && /^[a-zA-Z0-9\-_]*$/.test(value),
      message: () => $t('models.user.formRulesFeedback.usernameChars'),
      trigger: 'blur',
    },
  ],
  password: [
    requiredRule($t('models.user.password'), 'blur'),
    {
      validator: (rule: FormItemRule, value: string) => !!value && value.length >= 8,
      message: () => $t('forms.rulesFeedback.minChars', { min: 8 }),
      trigger: ['input', 'blur'],
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/.test(value),
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
  name: [requiredRule($t('models.user.name'), 'blur'), minMaxCharsRule(1, 64, 'blur')],
  affiliation: [
    requiredRule($t('models.user.affiliation'), 'blur'),
    minMaxCharsRule(4, 64, 'blur'),
  ],
  loginEmail: [requiredRule($t('models.user.email'), 'input')],
  loginPassword: [requiredRule($t('models.user.password'), 'input')],
};

export const textFormRules: Record<string, FormItemRule[]> = {
  title: [requiredRule($t('models.text.title'), 'blur'), minMaxCharsRule(1, 64, 'blur')],
  subtitleTranslation: [
    requiredRule($t('models.text.subtitle'), 'blur'),
    minMaxCharsRule(1, 128, 'blur'),
  ],
  subtitleLocale: [requiredRule($t('general.language'), 'blur')],
  slug: [
    requiredRule($t('models.text.slug'), 'blur'),
    minMaxCharsRule(1, 16, 'blur'),
    {
      validator: (rule: FormItemRule, value: string) => !!value && /^[a-z0-9]+$/.test(value),
      message: () => $t('models.text.formRulesFeedback.slugChars'),
      trigger: ['input', 'blur'],
    },
  ],
  levels: [
    {
      validator: (rule: FormItemRule, value: any[]) =>
        !!value && value.length >= 1 && value.length <= 32,
      message: () => $t('forms.rulesFeedback.minMaxItems', { min: 1, max: 32 }),
      trigger: 'blur',
    },
  ],
  levelTranslation: [requiredRule($t('models.text.level'), 'blur'), minMaxCharsRule(1, 32, 'blur')],
  defaultLevel: [
    {
      validator: (rule: FormItemRule, value: number) => value != null && value >= 0,
      message: () => $t('models.text.formRulesFeedback.defaultLevelRange'),
      trigger: 'blur',
    },
  ],
  locDelim: [requiredRule($t('models.text.locDelim'), 'blur'), minMaxCharsRule(1, 3, 'blur')],
};

export const locationFormRules: Record<string, FormItemRule[]> = {
  label: [requiredRule($t('models.location.label'), 'blur'), minMaxCharsRule(1, 256, 'blur')],
};

export const systemSegmentFormRules: Record<string, FormItemRule[]> = {
  title: [minMaxCharsRule(0, 32, 'blur')],
  key: [requiredRule($t('models.segment.key'), 'blur')],
  locale: [requiredRule($t('models.segment.locale'), 'blur')],
  html: [requiredRule($t('models.segment.html'), 'blur'), minMaxCharsRule(1, 1048576, 'blur')],
};

export const infoSegmentFormRules: Record<string, FormItemRule[]> = {
  title: [minMaxCharsRule(0, 32, 'blur')],
  key: [
    requiredRule($t('models.segment.key'), 'blur'),
    minMaxCharsRule(1, 32, 'blur'),
    {
      validator: (rule: FormItemRule, value: string) => !!value && /^[a-zA-Z0-9\-_]+$/.test(value),
      message: () => $t('models.segment.formRulesFeedback.keyChars'),
      trigger: ['input', 'blur'],
    },
    {
      validator: (rule: FormItemRule, value: string) => !!value && !value.startsWith('system'),
      message: () => $t('models.segment.formRulesFeedback.systemPrefixReserved'),
      trigger: 'blur',
    },
  ],
  locale: [requiredRule($t('models.segment.locale'), 'blur')],
  html: [requiredRule($t('models.segment.html'), 'blur'), minMaxCharsRule(1, 1048576, 'blur')],
};

export const platformSettingsFormRules: Record<string, FormItemRule[]> = {
  infoPlatformName: [
    requiredRule($t('models.platformSettings.infoPlatformName'), 'blur'),
    minMaxCharsRule(1, 32, 'blur'),
  ],
  infoSubtitleTranslation: [minMaxCharsRule(1, 128, 'blur')],
  infoTerms: [minMaxCharsRule(0, 512, 'blur')],
  infoContactName: [minMaxCharsRule(0, 64, 'blur')],
  infoContactEmail: [minMaxCharsRule(0, 64, 'blur')],
  infoContactUrl: [minMaxCharsRule(0, 512, 'blur')],
  defaultTextId: [requiredRule($t('models.platformSettings.defaultText'), 'blur')],
  availableLocales: [
    {
      validator: (rule: FormItemRule, value: string[]) =>
        !!value &&
        value.length >= 1 &&
        value.length <= localeProfiles.length &&
        !value.find((v) => !localeProfiles.filter((lp) => lp.key === v).length),
      message: () => $t('forms.rulesFeedback.minMaxItems', { min: 1, max: localeProfiles.length }),
      trigger: 'blur',
    },
  ],
  navInfoEntryTranslation: [minMaxCharsRule(1, 42, 'blur')],
  resourceCategoryKey: [
    requiredRule($t('models.platformSettings.resourceCategoryKey'), 'blur'),
    minMaxCharsRule(1, 16, 'blur'),
  ],
  resourceCategoryTranslation: [
    requiredRule($t('models.platformSettings.resourceCategoryTranslation'), 'blur'),
    minMaxCharsRule(1, 32, 'blur'),
  ],
};

export const resourceConfigFormRules: Record<string, FormItemRule[]> = {
  title: [requiredRule($t('models.resource.title'), 'blur'), minMaxCharsRule(1, 64, 'blur')],
  descriptionTranslation: [
    requiredRule($t('models.resource.description'), 'blur'),
    minMaxCharsRule(1, 512, 'blur'),
  ],
  citation: [minMaxCharsRule(0, 1000, 'blur')],
  commentTranslation: [minMaxCharsRule(0, 2000, 'blur')],
  metaKey: [requiredRule($t('models.meta.key'), 'blur'), minMaxCharsRule(1, 16, 'blur')],
  metaValue: [requiredRule($t('models.meta.value'), 'blur'), minMaxCharsRule(1, 128, 'blur')],
  resourceType: [
    requiredRule($t('models.resource.resourceType'), 'blur'),
    {
      validator: (rule: FormItemRule, value: string) => !!value && resourceTypes.includes(value),
      message: () =>
        $t('forms.rulesFeedback.mustBeOneOf', {
          x: $t('models.resource.resourceType'),
          values: resourceTypes.join(', '),
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
          x: $t('models.resource.level'),
        }),
      trigger: 'blur',
    },
  ],
};

const commonContentFormRules: Record<string, FormItemRule[]> = {
  comment: [minMaxCharsRule(0, 50000, 'blur')],
  notes: [minMaxCharsRule(0, 1000, 'blur')],
};

export const contentFormRules: Record<string, Record<string, FormItemRule[]>> = {
  plainText: {
    ...commonContentFormRules,
    text: [
      requiredRule($t('resources.types.plainText.contentFields.text'), 'blur'),
      minMaxCharsRule(1, 102400, 'blur'),
    ],
  },
  richText: {
    ...commonContentFormRules,
    html: [
      requiredRule($t('resources.types.richText.contentFields.html'), 'blur'),
      minMaxCharsRule(1, 102400, 'blur'),
    ],
  },
};

export const bookmarkFormRules: Record<string, FormItemRule[]> = {
  comment: [minMaxCharsRule(0, 1000, 'blur')],
};

export const wysiwygEditorFormRules: Record<string, FormItemRule[]> = {
  imageUrl: [minMaxCharsRule(0, 5000, undefined)],
  linkUrl: [minMaxCharsRule(0, 5000, undefined)],
};

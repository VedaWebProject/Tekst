import type { FormItemRule } from 'naive-ui';
import { $t, localeProfiles } from '@/i18n';
import { resourceTypes } from '@/api';

export const translationFormRules: Record<string, FormItemRule[]> = {
  locale: [
    {
      required: true,
      message: () => $t('forms.rulesFeedback.isRequired', { x: $t('models.locale.modelLabel') }),
      trigger: 'blur',
    },
  ],
};

export const accountFormRules: Record<string, FormItemRule[]> = {
  email: [
    {
      required: true,
      message: () => $t('forms.rulesFeedback.isRequired', { x: $t('models.user.email') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) => /^.+@.+\.\w+$/.test(value),
      message: () => $t('models.user.formRulesFeedback.emailInvalid'),
      trigger: 'blur',
    },
  ],
  username: [
    {
      required: true,
      message: () => $t('forms.rulesFeedback.isRequired', { x: $t('models.user.username') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 4 && value.length <= 16,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 4, max: 16 }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) => !!value && /^[a-zA-Z0-9\-_]*$/.test(value),
      message: () => $t('models.user.formRulesFeedback.usernameChars'),
      trigger: 'blur',
    },
  ],
  password: [
    {
      required: true,
      message: () => $t('forms.rulesFeedback.isRequired', { x: $t('models.user.password') }),
      trigger: 'blur',
    },
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
  name: [
    {
      required: true,
      message: () => $t('forms.rulesFeedback.isRequired', { x: $t('models.user.name') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 32,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 64 }),
      trigger: 'blur',
    },
  ],
  affiliation: [
    {
      required: true,
      message: () => $t('forms.rulesFeedback.isRequired', { x: $t('models.user.affiliation') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 4 && value.length <= 64,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 4, max: 64 }),
      trigger: 'blur',
    },
  ],
  loginEmail: [
    {
      required: true,
      message: () => $t('forms.rulesFeedback.isRequired', { x: $t('models.user.email') }),
      trigger: 'blur',
    },
  ],
  loginPassword: [
    {
      required: true,
      message: () => $t('forms.rulesFeedback.isRequired', { x: $t('models.user.password') }),
      trigger: 'blur',
    },
  ],
};

export const textFormRules: Record<string, FormItemRule[]> = {
  title: [
    {
      required: true,
      message: () => $t('forms.rulesFeedback.isRequired', { x: $t('models.text.title') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 64,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 64 }),
      trigger: 'blur',
    },
  ],
  subtitleTranslation: [
    {
      required: true,
      message: () => $t('forms.rulesFeedback.isRequired', { x: $t('models.text.subtitle') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 128,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 128 }),
      trigger: 'blur',
    },
  ],
  subtitleLocale: [
    {
      validator: (rule: FormItemRule, value: string) => !!value,
      message: () => $t('forms.rulesFeedback.isRequired', { x: $t('general.language') }),
      trigger: 'blur',
    },
  ],
  slug: [
    {
      required: true,
      message: () => $t('forms.rulesFeedback.isRequired', { x: $t('models.text.slug') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 16,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 16 }),
      trigger: 'blur',
    },
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
  levelTranslation: [
    {
      required: true,
      message: () => $t('forms.rulesFeedback.isRequired', { x: $t('models.text.level') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 32,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 32 }),
      trigger: 'blur',
    },
  ],
  defaultLevel: [
    {
      validator: (rule: FormItemRule, value: number) =>
        value !== undefined && value !== null && value >= 0,
      message: () => $t('models.text.formRulesFeedback.defaultLevelRange'),
      trigger: 'blur',
    },
  ],
  locDelim: [
    {
      required: true,
      message: () => $t('forms.rulesFeedback.isRequired', { x: $t('models.text.locDelim') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 3,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 3 }),
      trigger: 'blur',
    },
  ],
};

export const nodeFormRules: Record<string, FormItemRule[]> = {
  label: [
    {
      required: true,
      message: () => $t('forms.rulesFeedback.isRequired', { x: $t('models.node.label') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 256,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 256 }),
      trigger: 'blur',
    },
  ],
};

export const systemSegmentFormRules: Record<string, FormItemRule[]> = {
  title: [
    {
      validator: (rule: FormItemRule, value: string) => !value || value.length <= 32,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 0, max: 32 }),
      trigger: 'blur',
    },
  ],
  key: [
    {
      required: true,
      message: () => $t('forms.rulesFeedback.isRequired', { x: $t('models.segment.key') }),
      trigger: 'blur',
    },
  ],
  html: [
    {
      required: true,
      message: () => $t('forms.rulesFeedback.isRequired', { x: $t('models.segment.html') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 1048576,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 1048576 }),
      trigger: 'blur',
    },
  ],
};

export const infoSegmentFormRules: Record<string, FormItemRule[]> = {
  title: [
    {
      validator: (rule: FormItemRule, value: string) => !value || value.length <= 32,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 0, max: 32 }),
      trigger: 'blur',
    },
  ],
  key: [
    {
      required: true,
      message: () => $t('forms.rulesFeedback.isRequired', { x: $t('models.segment.key') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 32,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 32 }),
      trigger: 'blur',
    },
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
  html: [
    {
      required: true,
      message: () => $t('forms.rulesFeedback.isRequired', { x: $t('models.segment.html') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 1048576,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 1048576 }),
      trigger: 'blur',
    },
  ],
};

export const platformSettingsFormRules: Record<string, FormItemRule[]> = {
  infoPlatformName: [
    {
      required: true,
      message: () =>
        $t('forms.rulesFeedback.isRequired', {
          x: $t('models.platformSettings.infoPlatformName'),
        }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 32,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 32 }),
      trigger: 'blur',
    },
  ],
  infoSubtitleTranslation: [
    {
      validator: (rule: FormItemRule, value: string) => !value || value.length <= 128,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 0, max: 128 }),
      trigger: 'blur',
    },
  ],
  infoTerms: [
    {
      validator: (rule: FormItemRule, value: string) => !value || value.length <= 512,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 0, max: 512 }),
      trigger: 'blur',
    },
  ],
  infoContactName: [
    {
      validator: (rule: FormItemRule, value: string) =>
        !value || (value.length >= 1 && value.length <= 64),
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 64 }),
      trigger: 'blur',
    },
  ],
  infoContactEmail: [
    {
      validator: (rule: FormItemRule, value: string) =>
        !value || (value.length >= 1 && value.length <= 64),
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 64 }),
      trigger: 'blur',
    },
  ],
  infoContactUrl: [
    {
      validator: (rule: FormItemRule, value: string) => !value || value.length <= 512,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 0, max: 512 }),
      trigger: 'blur',
    },
  ],
  defaultTextId: [
    {
      required: true,
      message: () =>
        $t('forms.rulesFeedback.isRequired', { x: $t('models.platformSettings.defaultText') }),
      trigger: ['blur', 'change'],
    },
  ],
  availableLocales: [
    {
      validator: (rule: FormItemRule, value: string[]) =>
        !!value && value.length >= 1 && value.length <= localeProfiles.length,
      message: () => $t('forms.rulesFeedback.minMaxItems', { min: 1, max: localeProfiles.length }),
      trigger: 'blur',
    },
  ],
  navInfoEntryTranslation: [
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 42,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 42 }),
      trigger: 'blur',
    },
  ],
  resourceCategoryKey: [
    {
      required: true,
      message: () =>
        $t('forms.rulesFeedback.isRequired', {
          x: $t('models.platformSettings.resourceCategoryKey'),
        }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 16,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 16 }),
      trigger: 'blur',
    },
  ],
  resourceCategoryTranslation: [
    {
      required: true,
      message: () =>
        $t('forms.rulesFeedback.isRequired', {
          x: $t('models.platformSettings.resourceCategoryTranslation'),
        }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 32,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 32 }),
      trigger: 'blur',
    },
  ],
};

export const resourceFormRules: Record<string, FormItemRule[]> = {
  title: [
    {
      required: true,
      message: () =>
        $t('forms.rulesFeedback.isRequired', {
          x: $t('models.resource.title'),
        }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 64,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 64 }),
      trigger: 'blur',
    },
  ],
  descriptionTranslation: [
    {
      required: true,
      message: () => $t('forms.rulesFeedback.isRequired', { x: $t('models.resource.description') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 512,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 512 }),
      trigger: 'blur',
    },
  ],
  citation: [
    {
      validator: (rule: FormItemRule, value: string) =>
        !value || (value.length >= 1 && value.length <= 1000),
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 1000 }),
      trigger: 'blur',
    },
  ],
  commentTranslation: [
    {
      validator: (rule: FormItemRule, value: string) =>
        !value || (value.length >= 1 && value.length <= 2000),
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 2000 }),
      trigger: 'blur',
    },
  ],
  metaKey: [
    {
      required: true,
      message: () =>
        $t('forms.rulesFeedback.isRequired', {
          x: $t('models.meta.key'),
        }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 16,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 16 }),
      trigger: 'blur',
    },
  ],
  metaValue: [
    {
      required: true,
      message: () =>
        $t('forms.rulesFeedback.isRequired', {
          x: $t('models.meta.value'),
        }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 128,
      message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 128 }),
      trigger: 'blur',
    },
  ],
  resourceType: [
    {
      required: true,
      message: () =>
        $t('forms.rulesFeedback.isRequired', {
          x: $t('models.resource.resourceType'),
        }),
      trigger: 'blur',
    },
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
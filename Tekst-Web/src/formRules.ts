import type { FormItemRule } from 'naive-ui';
import { i18n } from './i18n';

const { t } = i18n.global;

const accountFormRules: Record<string, FormItemRule[]> = {
  email: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.user.email') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) => /^.+@.+\.\w+$/.test(value),
      message: () => t('models.user.formRulesFeedback.emailInvalid'),
      trigger: 'blur',
    },
  ],
  username: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.user.username') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 4 && value.length <= 16,
      message: () => t('forms.rulesFeedback.minMaxChars', { min: 4, max: 16 }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) => !!value && /^[a-zA-Z0-9\-_]*$/.test(value),
      message: () => t('models.user.formRulesFeedback.usernameChars'),
      trigger: 'blur',
    },
  ],
  password: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.user.password') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) => !!value && value.length >= 8,
      message: () => t('forms.rulesFeedback.minChars', { min: 8 }),
      trigger: ['input', 'blur'],
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/.test(value),
      message: () => t('models.user.formRulesFeedback.passwordChars'),
      trigger: ['input', 'blur'],
    },
  ],
  passwordRepeat: [
    {
      required: true,
      message: () => t('models.user.formRulesFeedback.passwordRepReq'),
      trigger: 'blur',
    },
  ],
  firstName: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.user.firstName') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 32,
      message: () => t('forms.rulesFeedback.minMaxChars', { min: 1, max: 32 }),
      trigger: 'blur',
    },
  ],
  lastName: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.user.lastName') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 32,
      message: () => t('forms.rulesFeedback.minMaxChars', { min: 1, max: 32 }),
      trigger: 'blur',
    },
  ],
  affiliation: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.user.affiliation') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 4 && value.length <= 64,
      message: () => t('forms.rulesFeedback.minMaxChars', { min: 4, max: 64 }),
      trigger: 'blur',
    },
  ],
  loginEmail: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.user.email') }),
      trigger: 'blur',
    },
  ],
  loginPassword: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.user.password') }),
      trigger: 'blur',
    },
  ],
};

const textFormRules: Record<string, FormItemRule[]> = {
  title: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.text.title') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 64,
      message: () => t('forms.rulesFeedback.minMaxChars', { min: 1, max: 64 }),
      trigger: 'blur',
    },
  ],
  subtitle: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.text.subtitle') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        value != null && value.length >= 1 && value.length <= 128,
      message: () => t('forms.rulesFeedback.minMaxChars', { min: 1, max: 128 }),
      trigger: 'blur',
    },
  ],
  subtitleLocale: [
    {
      validator: (rule: FormItemRule, value: string) => !!value,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('general.language') }),
      trigger: 'blur',
    },
  ],
  slug: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.text.slug') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 16,
      message: () => t('forms.rulesFeedback.minMaxChars', { min: 1, max: 16 }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) => !!value && /^[a-z0-9]+$/.test(value),
      message: () => t('models.text.formRulesFeedback.slugChars'),
      trigger: ['input', 'blur'],
    },
  ],
  levels: [
    {
      validator: (rule: FormItemRule, value: any[]) =>
        !!value && value.length >= 1 && value.length <= 32,
      message: () => t('forms.rulesFeedback.minMaxItems', { min: 1, max: 32 }),
      trigger: 'blur',
    },
  ],
  levelTranslationLocale: [
    {
      validator: (rule: FormItemRule, value: string) => !!value,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('general.language') }),
      trigger: 'blur',
    },
  ],
  levelTranslationLabel: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.text.level') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 32,
      message: () => t('forms.rulesFeedback.minMaxChars', { min: 1, max: 32 }),
      trigger: 'blur',
    },
  ],
  defaultLevel: [
    {
      validator: (rule: FormItemRule, value: number) =>
        value !== undefined && value !== null && value >= 0,
      message: () => t('models.text.formRulesFeedback.defaultLevelRange'),
      trigger: 'blur',
    },
  ],
  locDelim: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.text.locDelim') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 3,
      message: () => t('forms.rulesFeedback.minMaxChars', { min: 1, max: 3 }),
      trigger: 'blur',
    },
  ],
};

export function useFormRules() {
  return {
    accountFormRules,
    textFormRules,
  };
}

import type { FormItemRule } from 'naive-ui';
import { i18n } from './i18n';

const t = i18n.global.t;

const formRules: Record<string, FormItemRule[]> = {
  email: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.user.email') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) => /^.+@.+\.\w+$/.test(value),
      message: () => t('register.rulesFeedback.emailInvalid'),
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
      message: () => t('register.rulesFeedback.usernameChars'),
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
      message: () => t('register.rulesFeedback.passwordChars'),
      trigger: ['input', 'blur'],
    },
  ],
  passwordRepeat: [
    {
      required: true,
      message: () => t('register.rulesFeedback.passwordRepReq'),
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

export function useFormRules() {
  return {
    ...formRules,
  };
}

import OskInput from '@/components/OskInput.vue';
import { $t } from '@/i18n';
import { renderIcon } from '@/utils';
import {
  NFlex,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  useDialog,
  type DialogOptions,
  type FormInst,
  type SelectOption,
} from 'naive-ui';
import { h, ref, type Component, type Ref, type VNodeChild } from 'vue';

type FormItemProps = InstanceType<typeof NFormItem>['$props'];

type PromptConfigBase = {
  type: string;
  required?: boolean;
  icon?: Component;
  placeholder?: string;
  title?: DialogOptions['title'];
  label?: FormItemProps['label'];
  positiveText?: DialogOptions['positiveText'];
  negativeText?: DialogOptions['negativeText'];
  rule?: FormItemProps['rule'];
  defaultValue?: unknown;
  msg?: string;
};

interface SingleLineInputPrompt extends PromptConfigBase {
  type: 'singleLineInput';
}

interface MultiLineInputPrompt extends PromptConfigBase {
  type: 'multiLineInput';
  maxLength?: number;
  rows?: number;
}

interface MultiLineInputOSKPrompt extends PromptConfigBase {
  type: 'multiLineInputOSK';
  maxLength?: number;
  rows?: number;
  font?: string;
  oskKey?: string;
}

interface SelectPrompt extends PromptConfigBase {
  type: 'select';
  options: SelectOption[];
}

type PromptConfig =
  | SingleLineInputPrompt
  | MultiLineInputPrompt
  | MultiLineInputOSKPrompt
  | SelectPrompt;

const _getForm = (
  cfg: PromptConfig,
  formRef: Ref<FormInst | undefined>,
  formModel: Record<string, unknown> | undefined,
  defaultContent: VNodeChild
) =>
  h(NFlex, { vertical: true, size: 'large' }, () => [
    ...(cfg.msg ? [h('div', { class: 'text-small' }, cfg.msg)] : []),
    h(
      NForm,
      {
        ref: formRef,
        model: formModel,
      },
      () =>
        h(
          NFormItem,
          {
            label: cfg.label,
            showLabel: !!cfg.label,
            rule: cfg.rule,
            showFeedback: true,
            required: cfg.required,
            path: 'input',
          },
          () => defaultContent
        )
    ),
  ]);
const _getPromptType = (userCfg: PromptConfig) => {
  const promptTypes = {
    singleLineInput: (cfg: SingleLineInputPrompt) => {
      const returnType = undefined as string | undefined;
      const formModel = ref<{ input?: typeof returnType }>({
        input: cfg.defaultValue as typeof returnType,
      });
      const formRef = ref<FormInst>();
      return {
        returnType,
        formRef,
        formModel,
        content: () =>
          _getForm(
            cfg,
            formRef,
            formModel.value,
            h(NInput, {
              value: formModel.value.input,
              placeholder: cfg.placeholder,
              onUpdateValue: (val) => {
                formModel.value = { input: val };
              },
            })
          ),
      };
    },
    multiLineInput: (cfg: MultiLineInputPrompt) => {
      const returnType = undefined as string | undefined;
      const formModel = ref<{ input?: typeof returnType }>({
        input: cfg.defaultValue as typeof returnType,
      });
      const formRef = ref<FormInst>();
      return {
        returnType,
        formRef,
        formModel,
        content: () =>
          _getForm(
            cfg,
            formRef,
            formModel.value,
            h(NInput, {
              value: formModel.value.input,
              placeholder: cfg.placeholder,
              type: 'textarea',
              maxlength: cfg.maxLength,
              showCount: cfg.maxLength != null,
              rows: cfg.rows,
              onUpdateValue: (val) => {
                formModel.value = { input: val };
              },
            })
          ),
      };
    },
    multiLineInputOSK: (cfg: MultiLineInputOSKPrompt) => {
      const returnType = undefined as string | undefined;
      const formModel = ref<{ input?: typeof returnType }>({
        input: cfg.defaultValue as typeof returnType,
      });
      const formRef = ref<FormInst>();
      return {
        returnType,
        formRef,
        formModel,
        content: () =>
          _getForm(
            cfg,
            formRef,
            formModel.value,
            h(OskInput, {
              modelValue: formModel.value.input,
              placeholder: cfg.placeholder,
              type: 'textarea',
              maxlength: cfg.maxLength,
              showCount: cfg.maxLength != null,
              rows: cfg.rows,
              font: cfg.font,
              oskMode: cfg.oskKey,
              'onUpdate:modelValue': (v: string | null | undefined) => {
                formModel.value = { input: v ?? undefined };
              },
            })
          ),
      };
    },
    select: (cfg: SelectPrompt) => {
      const returnType = undefined as string | undefined;
      const formModel = ref<{ input?: typeof returnType }>({
        input: cfg.defaultValue as typeof returnType,
      });
      const formRef = ref<FormInst>();
      return {
        returnType,
        formRef,
        formModel,
        content: () =>
          _getForm(
            cfg,
            formRef,
            formModel.value,
            h(NSelect, {
              value: formModel.value.input,
              options: cfg.options,
              placeholder: cfg.placeholder,
              onUpdateValue: (v) => {
                formModel.value = { input: v ?? undefined };
              },
            })
          ),
      };
    },
  };
  // we need to resolve the discriminated type union here – what a drag
  switch (userCfg.type) {
    case 'singleLineInput':
      return promptTypes['singleLineInput'](userCfg);
    case 'multiLineInput':
      return promptTypes['multiLineInput'](userCfg);
    case 'multiLineInputOSK':
      return promptTypes['multiLineInputOSK'](userCfg);
    case 'select':
      return promptTypes['select'](userCfg);
    default:
      throw new Error('Invalid prompt type.');
  }
};

export function usePrompt() {
  const dialog = useDialog();

  /**
   * Returns a value or `undefined` (empty value) if the user submits the prompt.
   * Returns `null` if the user cancels the prompt and doesn't submit a value.
   * @param cfg
   * @returns Promise<string | null | undefined>
   */
  const prompt = (cfg: PromptConfig) => {
    const typeDef = _getPromptType(cfg);
    return new Promise<typeof typeDef.returnType | null>((promptResolve) => {
      dialog.create({
        ...cfg,
        type: 'default',
        icon: renderIcon(cfg.icon, undefined, 'large'),
        showIcon: !!cfg.icon,
        content: typeDef.content,
        positiveText: cfg.positiveText ?? $t('common.ok'),
        negativeText: cfg.negativeText ?? $t('common.cancel'),
        contentClass: 'my-lg',
        onNegativeClick: () => promptResolve(null),
        onMaskClick: () => promptResolve(null),
        onClose: () => promptResolve(null),
        onEsc: () => promptResolve(null),
        onPositiveClick: () => {
          return new Promise((dialogResolve) => {
            typeDef.formRef.value
              ?.validate()
              .then(() => {
                promptResolve(typeDef.formModel.value.input);
                dialogResolve(true);
              })
              .catch(() => {
                dialogResolve(false);
              });
          });
        },
      });
    });
  };
  return prompt;
}

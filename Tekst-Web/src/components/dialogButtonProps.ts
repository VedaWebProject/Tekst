import type { ButtonProps } from 'naive-ui';

const commonButtonProps: ButtonProps = {
  size: 'medium',
};

export const positiveButtonProps: ButtonProps = {
  ...commonButtonProps,
  type: 'primary',
};

export const negativeButtonProps: ButtonProps = {
  ...commonButtonProps,
  type: 'default',
  secondary: true,
  ghost: false,
};

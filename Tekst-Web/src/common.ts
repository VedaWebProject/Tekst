import type { ButtonProps } from 'naive-ui';

const dialogButtonPropsCommon: ButtonProps = {
  size: 'medium',
};

const dialogButtonPropsPositive: ButtonProps = {
  ...dialogButtonPropsCommon,
  type: 'primary',
};

const dialogButtonPropsNegative: ButtonProps = {
  ...dialogButtonPropsCommon,
  type: 'default',
  secondary: true,
  ghost: false,
};

export const dialogProps = {
  positiveButtonProps: dialogButtonPropsPositive,
  negativeButtonProps: dialogButtonPropsNegative,
};

export const dynInputCreateBtnProps: ButtonProps = { dashed: false, ghost: false, secondary: true };

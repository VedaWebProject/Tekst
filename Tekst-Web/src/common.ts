import type { ButtonProps, DialogProps } from 'naive-ui';

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

export const commonDialogOptions: DialogProps = {
  positiveButtonProps: dialogButtonPropsPositive,
  negativeButtonProps: dialogButtonPropsNegative,
  titleStyle: 'font-weight: bold',
};

export const dynInputCreateBtnProps: ButtonProps = { dashed: false, ghost: false, secondary: true };

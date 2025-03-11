import type { ButtonProps } from 'naive-ui';

export const WEB_PATH = import.meta.env.BASE_URL;
export const STATIC_PATH = WEB_PATH.replace(/\/$/, '') + '/static';

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

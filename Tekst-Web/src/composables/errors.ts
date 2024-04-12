import type { ErrorDetail, ErrorModel, HTTPValidationError, TekstErrorModel } from '@/api';
import { useMessages } from './messages';
import { $t, $te } from '@/i18n';

type FapiUsersInvalidPasswordModel = {
  detail: {
    code: string;
    reason?: string;
  };
};

const fapiUsersErrorCodesMap: Record<string, string> = {
  LOGIN_BAD_CREDENTIALS: 'loginBadCredentials',
  LOGIN_USER_NOT_VERIFIED: 'loginUserNotVerified',
  REGISTER_USER_ALREADY_EXISTS: 'registerEmailAlreadyExists',
  REGISTER_USERNAME_ALREADY_EXISTS: 'registerUsernameAlreadyExists',
  VERIFY_USER_BAD_TOKEN: 'verifyUserBadToken',
  VERIFY_USER_ALREADY_VERIFIED: 'verifyUserAlreadyVerified',
  RESET_PASSWORD_BAD_TOKEN: 'resetPasswordBadToken',
};

function isObject(o: any) {
  return o && typeof o === 'object' && o.constructor === Object;
}

export function useErrors() {
  const { message } = useMessages();

  function msg(
    error: TekstErrorModel | ErrorModel | HTTPValidationError | FapiUsersInvalidPasswordModel,
    displayMessage: boolean = true
  ): string {
    // Here we have to unify the error model because the Tekst API always returns errors
    // of type ErrorDetail or HTTPValidationError, but the auth-related endpoints
    // (coming from fastapi-users) their own ErrorModel.
    let detail: ErrorDetail;
    if (isObject(error.detail) && 'key' in (error.detail as object)) {
      // the received error is an instance of TekstErrorModel
      detail = error.detail as ErrorDetail;
    } else if (error.detail?.constructor.name === 'String') {
      // the received error is an instance of ErrorModel (from FastAPI-Users)
      detail = { key: fapiUsersErrorCodesMap[error.detail as string] };
    } else if (
      error.detail &&
      isObject(error.detail) &&
      'code' in (error.detail as object) &&
      (error as FapiUsersInvalidPasswordModel).detail.code === 'REGISTER_INVALID_PASSWORD'
    ) {
      detail = { key: 'registerInvalidPassword' };
    } else if (error.detail && Array.isArray(error.detail) && error.detail?.[0]?.loc) {
      // the received error is an instance of HTTPValidationError
      detail = {
        key: 'validationError',
        msg: 'There was an error validating the data sent to the server.',
      };
    } else {
      detail = { key: 'unexpected' };
    }
    // show error message
    if ($te(`errors.${detail.key}`)) {
      const m = $t(`errors.${detail.key}`, (detail.values as Record<string, unknown>) || undefined);
      displayMessage && message.error(m, detail.values || undefined, 10);
      return m;
    } else {
      const m = $t('errors.unexpected');
      displayMessage && message.error(m, error, 10);
      return m;
    }
  }

  return { msg };
}

import createClient from 'openapi-fetch';
import type { paths, components } from '@/api/schema';
import { useAuthStore } from '@/stores';
import Cookies from 'js-cookie';
import { useMessages } from '@/messages';
import { $t } from '@/i18n';

const serverUrl: string | undefined = import.meta.env.TEKST_SERVER_URL;
const apiPath: string | undefined = import.meta.env.TEKST_API_PATH;
const apiUrl = (serverUrl && apiPath && serverUrl + apiPath) || '/';

// custom, modified "fetch" for implementing request/response interceptors
const customFetch = async (input: RequestInfo | URL, init?: RequestInit | undefined) => {
  // --- request interceptors go here... ---
  // add XSRF header to request headers
  const xsrfToken = Cookies.get('XSRF-TOKEN');
  if (xsrfToken) {
    init = init || {};
    init.headers = new Headers(init.headers);
    init.headers.set('X-XSRF-TOKEN', xsrfToken);
  }

  // --- perform request ---
  const response = await globalThis.fetch(input, init);

  // --- response interceptors go here... ---
  if (response.ok) return response; // allow 200-299 response to pass through early
  const bodyText = await response.clone().text(); // extract response body text

  if (response.status === 401) {
    // automatically log out on a 401 response
    if (!response.url.endsWith('/logout')) {
      const { message } = useMessages();
      message.error($t('errors.logInToAccess'));
      console.log("Oh no! You don't seem to have access to this resource!");
      const auth = useAuthStore();
      if (auth.loggedIn) {
        console.log('Running logout sequence in reaction to 401/403 response...');
        await auth.logout();
      }
    }
  } else if (response.status === 403 && bodyText.includes('CSRF')) {
    // show CSRF/XSRF error on 403 response mentioning CSRF
    const { message } = useMessages();
    message.error($t('errors.csrf'));
  } else if (response.status === 403) {
    const { message } = useMessages();
    message.error($t('errors.forbidden'));
  }
  return response;
};

export const { GET, POST, PUT, PATCH, DELETE } = createClient<paths>({
  baseUrl: apiUrl,
  fetch: customFetch,
});

export const optionsPresets = {
  formUrlEncoded: {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    bodySerializer: (body: Record<string, string | number | boolean | undefined | null>) => {
      return new URLSearchParams(
        Object.entries(body).map(([key, value]) => [String(key), String(value)])
      ).toString();
    },
  },
};

export function getFullUrl(path: string, query?: Record<string, any>): URL {
  const searchParams = new URLSearchParams(
    Object.fromEntries(Object.entries(query || {}).map(([key, value]) => [key, String(value)]))
  );
  const queryString = searchParams.toString() ? '?' + searchParams.toString() : '';
  const relPath = path.replace(/^\/+/, '');
  return new URL(relPath + queryString, apiUrl.replace(/\/*$/, '/'));
}

// export some common platform properties for use throughout codebase

export const resourceTypes = ['plaintext', 'debug'];
export const prioritizedMetadataKeys = ['author', 'year', 'language'];

// export components types for use throughout codebase

// general

export type ErrorModel = components['schemas']['ErrorModel'];
export type Metadate = components['schemas']['Metadate'];
export type Metadata = Metadate[];
export type LocaleKey = components['schemas']['LocaleKey'];
export type TranslationLocaleKey = components['schemas']['TranslationLocaleKey'];
export type Translation = {
  locale: TranslationLocaleKey;
  translation: string;
};
export type LocationData = components['schemas']['LocationData'];

// user

export type UserCreate = components['schemas']['UserCreate'];
export type UserRead = components['schemas']['UserRead'];
export type UserUpdate = components['schemas']['UserUpdate'];
export type UserReadPublic = components['schemas']['UserReadPublic'];
export type UserUpdatePublicFields = components['schemas']['UserUpdate']['publicFields'];

// text and text structure

export type TextCreate = components['schemas']['TextCreate'];
export type TextRead = components['schemas']['TextRead'];
export type TextUpdate = components['schemas']['TextUpdate'];
export type LocationRead = components['schemas']['LocationRead'];

// platform

export type PlatformStats = components['schemas']['PlatformStats'];
export type PlatformData = components['schemas']['PlatformData'];
export type PlatformSettingsRead = components['schemas']['PlatformSettingsRead'];
export type PlatformSettingsUpdate = components['schemas']['PlatformSettingsUpdate'];
export type ResourceCoverage = components['schemas']['ResourceCoverage'];
export type ResourceCoverageDetails = components['schemas']['ResourceCoverageDetails'];

// client segments

export type ClientSegmentRead = components['schemas']['ClientSegmentRead'];
export type ClientSegmentCreate = components['schemas']['ClientSegmentCreate'];
export type ClientSegmentUpdate = components['schemas']['ClientSegmentUpdate'];
export type ClientSegmentHead = components['schemas']['ClientSegmentHead'];

// resources

export type PlaintextResourceCreate = components['schemas']['PlaintextResourceCreate'];
export type PlaintextResourceRead = components['schemas']['PlaintextResourceRead'];
export type PlaintextResourceUpdate = components['schemas']['PlaintextResourceUpdate'];
export type PlaintextResourceConfig = components['schemas']['PlaintextResourceConfig'];
export type PlaintextContentCreate = components['schemas']['PlaintextContentCreate'];
export type PlaintextContentRead = components['schemas']['PlaintextContentRead'];
export type PlaintextContentUpdate = components['schemas']['PlaintextContentUpdate'];

export type DebugResourceCreate = components['schemas']['DebugResourceCreate'];
export type DebugResourceRead = components['schemas']['DebugResourceRead'];
export type DebugResourceUpdate = components['schemas']['DebugResourceUpdate'];
export type DebugResourceConfig = components['schemas']['DebugResourceConfig'];
export type DebugContentCreate = components['schemas']['DebugContentCreate'];
export type DebugContentRead = components['schemas']['DebugContentRead'];
export type DebugContentUpdate = components['schemas']['DebugContentUpdate'];

export type AnyContentCreate = PlaintextContentCreate | DebugContentCreate;
export type AnyContentRead = PlaintextContentRead | DebugContentRead;
export type AnyContentUpdate = PlaintextContentUpdate | DebugContentUpdate;
export type AnyResourceCreate = PlaintextResourceCreate | DebugResourceCreate;
export type AnyResourceRead = (PlaintextResourceRead | DebugResourceRead) & {
  active?: boolean;
  contents?: AnyContentRead[];
  coverage?: ResourceCoverage;
};
export type AnyResourceUpdate = PlaintextResourceUpdate | DebugResourceUpdate;

// common resource config types

export type AnyResourceConfig = PlaintextResourceConfig | DebugResourceConfig;
export type DeepLLinksConfig = components['schemas']['DeepLLinksConfig'];

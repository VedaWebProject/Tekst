import createClient from 'openapi-fetch';
import type { paths, components } from '@/api/schema';
import { useAuthStore } from '@/stores';
import Cookies from 'js-cookie';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { useErrors } from '@/composables/errors';

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
  } else if (response.status >= 400) {
    // it's some kind of error, so pass the response body to the error message util
    try {
      useErrors().msg(await response.clone().json());
    } catch (e) {
      console.error(e);
    }
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

export async function withSelectedFile(
  cb: (file: File | null) => void | Promise<void>,
  contentType: string = 'application/json,.json',
  multiple?: boolean
) {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = contentType;
  input.multiple = !!multiple;
  input.onchange = () => cb(input.files ? input.files[0] : null);
  input.onclose = input.remove;
  input.click();
}

export function saveDownload(blob: Blob, filename: string) {
  const a = document.createElement('a');
  a.href = window.URL.createObjectURL(blob);
  if (filename) {
    a.download = filename;
  }
  a.click();
  a.remove();
}

// export some common platform properties for use throughout codebase

export const resourceTypes = ['plainText', 'richText'];
export const prioritizedMetadataKeys = ['author', 'year', 'language'];

// export components types for use throughout codebase

// general

export type TekstErrorModel = components['schemas']['TekstErrorModel'];
export type ErrorDetail = components['schemas']['ErrorDetail'];
export type ErrorModel = components['schemas']['ErrorModel'];
export type HTTPValidationError = components['schemas']['HTTPValidationError'];

export type Metadate = components['schemas']['Metadate'];
export type Metadata = Metadate[];
export type LocaleKey = components['schemas']['LocaleKey'];
export type TranslationLocaleKey = components['schemas']['TranslationLocaleKey'];
export type Translation = {
  locale: TranslationLocaleKey;
  translation: string;
};

// bookmark

export type BookmarkRead = components['schemas']['BookmarkRead'];
export type BookmarkCreate = components['schemas']['BookmarkCreate'];

// user

export type UserCreate = components['schemas']['UserCreate'];
export type UserRead = components['schemas']['UserRead'];
export type UserUpdate = components['schemas']['UserUpdate'];
export type UserReadPublic = components['schemas']['UserReadPublic'];
export type UserUpdateAdminNotificationTriggers =
  components['schemas']['UserUpdate']['adminNotificationTriggers'];
export type UserUpdatePublicFields = components['schemas']['UserUpdate']['publicFields'];

// text and text structure

export type TextCreate = components['schemas']['TextCreate'];
export type TextRead = components['schemas']['TextRead'];
export type TextUpdate = components['schemas']['TextUpdate'];
export type LocationRead = components['schemas']['LocationRead'];
export type LocationData = components['schemas']['LocationData'];

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

type ResourceReadExtras = {
  active?: boolean;
  coverage?: ResourceCoverage;
};

export type PlainTextContentRead = components['schemas']['PlainTextContentRead'];
export type PlainTextContentCreate = components['schemas']['PlainTextContentCreate'];
export type PlainTextResourceCreate = components['schemas']['PlainTextResourceCreate'];
export type PlainTextResourceRead = components['schemas']['PlainTextResourceRead'] &
  ResourceReadExtras & {
    contents?: PlainTextContentRead[];
  };

export type RichTextContentRead = components['schemas']['RichTextContentRead'];
export type RichTextContentCreate = components['schemas']['RichTextContentCreate'];
export type RichTextResourceCreate = components['schemas']['RichTextResourceCreate'];
export type RichTextResourceRead = components['schemas']['RichTextResourceRead'] &
  ResourceReadExtras & {
    contents?: RichTextContentRead[];
  };

export type AnyContentCreate =
  paths['/contents']['post']['requestBody']['content']['application/json'];
export type AnyContentRead =
  paths['/contents/{id}']['get']['responses']['200']['content']['application/json'];
export type AnyContentUpdate =
  paths['/contents/{id}']['patch']['requestBody']['content']['application/json'];

export type AnyResourceCreate =
  paths['/resources']['post']['requestBody']['content']['application/json'];
export type AnyResourceRead =
  paths['/resources/{id}']['get']['responses']['200']['content']['application/json'] &
    ResourceReadExtras & {
      contents?: AnyContentRead[];
    };
export type AnyResourceUpdate =
  paths['/resources/{id}']['patch']['requestBody']['content']['application/json'];

// resource config types

export type PlainTextResourceConfig = components['schemas']['PlainTextResourceConfig'];
export type RichTextResourceConfig = components['schemas']['RichTextResourceConfig'];

export type CommonResourceConfig = components['schemas']['CommonResourceConfig'];
export type AnyResourceConfig = AnyResourceRead['config'];
export type DeepLLinksConfig = components['schemas']['DeepLLinksConfig'];

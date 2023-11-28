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
  if (response.status === 401) {
    // automatically log out on a 401 response
    if (!response.url.endsWith('/logout')) {
      const { message } = useMessages();
      message.error($t('errors.logInToAccess'));
      console.log('Oh no! The server responded with 401!');
      const auth = useAuthStore();
      if (auth.loggedIn) {
        console.log('Running logout sequence in reaction to 401 response...');
        await auth.logout();
      }
    }
  } else if (response.status === 403) {
    // show CSRF/XSRF error on 403 response
    const { message } = useMessages();
    message.error($t('errors.csrf'));
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

// export components types for use throughout codebase

// general

export type ErrorModel = components['schemas']['ErrorModel'];
export type Metadate = components['schemas']['Metadate'];
export type Metadata = Metadate[];

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
export type SubtitleTranslation = components['schemas']['SubtitleTranslation'];
export type StructureLevelTranslation = components['schemas']['StructureLevelTranslation'];
export type NodeRead = components['schemas']['NodeRead'];

// platform

export type PlatformStats = components['schemas']['PlatformStats'];
export type PlatformData = components['schemas']['PlatformData'];
export type PlatformSettingsRead = components['schemas']['PlatformSettingsRead'];
export type PlatformSettingsUpdate = components['schemas']['PlatformSettingsUpdate'];
export type LayerNodeCoverage = components['schemas']['LayerNodeCoverage'];

// client segments

export type ClientSegmentRead = components['schemas']['ClientSegmentRead'];
export type ClientSegmentCreate = components['schemas']['ClientSegmentCreate'];
export type ClientSegmentUpdate = components['schemas']['ClientSegmentUpdate'];
export type ClientSegmentHead = components['schemas']['ClientSegmentHead'];

// data layers

export type PlaintextLayerCreate = components['schemas']['PlaintextLayerCreate'];
export type PlaintextLayerRead = components['schemas']['PlaintextLayerRead'];
export type PlaintextLayerUpdate = components['schemas']['PlaintextLayerUpdate'];
export type PlaintextLayerConfig = components['schemas']['PlaintextLayerConfig'];

export type DebugLayerCreate = components['schemas']['DebugLayerCreate'];
export type DebugLayerRead = components['schemas']['DebugLayerRead'];
export type DebugLayerUpdate = components['schemas']['DebugLayerUpdate'];
export type DebugLayerConfig = components['schemas']['DebugLayerConfig'];

export type AnyLayerRead = PlaintextLayerRead | DebugLayerRead;
export type AnyLayerUpdate = PlaintextLayerUpdate | DebugLayerUpdate;

// common data layer config types

export type DeepLLinksConfig = components['schemas']['DeepLLinksConfig'];

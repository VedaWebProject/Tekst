import createClient from 'openapi-fetch';
import type { paths, components } from '@/api/schema';
import queryString from 'query-string';
import { useAuthStore } from '@/stores';
import Cookies from 'js-cookie';

const serverUrl: string | undefined = import.meta.env.TEKST_SERVER_URL;
const apiPath: string | undefined = import.meta.env.TEKST_API_PATH;
const apiUrl = (serverUrl && apiPath && serverUrl + apiPath) || '/';

// custom, monkeypatched "fetch" for implementing request/response interceptors
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
  // automatically log out on a 401 response
  if (response.status === 401) {
    if (!response.url.endsWith('/logout')) {
      console.log('401 DETECTED! OH NO!');
      const auth = useAuthStore();
      if (auth.loggedIn) {
        console.log('Running logout sequence in reaction to 401 response');
        auth.logout();
      }
    }
  }
  return response;
};

export const { GET, POST, PUT, PATCH, DELETE } = createClient<paths>({
  baseUrl: apiUrl,
  fetch: customFetch,
  querySerializer: (q) => queryString.stringify(q, { arrayFormat: 'none' }),
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

// export components types for use throughout codebase
export type UserCreate = components['schemas']['UserCreate'];
export type UserRead = components['schemas']['UserRead'];
export type UserUpdate = components['schemas']['UserUpdate'];
export type UserReadPublic = components['schemas']['UserReadPublic'];
export type UserUpdatePublicFields = components['schemas']['UserUpdate']['publicFields'];
export type TextCreate = components['schemas']['TextCreate'];
export type TextRead = components['schemas']['TextRead'];
export type SubtitleTranslation = components['schemas']['SubtitleTranslation'];
export type StructureLevelTranslation = components['schemas']['StructureLevelTranslation'];
export type NodeRead = components['schemas']['NodeRead'];
export type PlainTextLayerConfig = components['schemas']['PlainTextLayerConfig-Output'];
export type DeepLLinksConfigOutput = components['schemas']['DeepLLinksConfig-Output'];
export type LayerNodeCoverage = components['schemas']['LayerNodeCoverage'];
export type PlatformStats = components['schemas']['PlatformStats'];
export type PlatformData = components['schemas']['PlatformData'];
export type ErrorModel = components['schemas']['ErrorModel'];

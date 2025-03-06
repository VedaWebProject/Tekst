import type { components, paths } from '@/api/schema';
import { useErrors } from '@/composables/errors';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { useAuthStore } from '@/stores';
import Cookies from 'js-cookie';
import createClient, { type Middleware } from 'openapi-fetch';

const serverUrl: string | undefined = import.meta.env.TEKST_SERVER_URL;
const apiPath: string | undefined = import.meta.env.TEKST_API_PATH;
const apiUrl = (serverUrl && apiPath && serverUrl + apiPath) || '/';

// HTTP client middleware for intercepting requests and responses
const interceptors: Middleware = {
  // intercept requests
  async onRequest({ request }) {
    // set XSRF header
    const xsrfToken = Cookies.get('XSRF-TOKEN');
    if (xsrfToken) {
      request.headers.set('X-XSRF-TOKEN', xsrfToken);
    }
    return request;
  },
  // intercept responses
  async onResponse({ response }) {
    if (response.ok) return;
    const { message } = useMessages();
    const responseBodyText = await response.clone().text();

    if (response.status === 401) {
      // automatically log out on a 401 response
      if (!response.url.endsWith('/logout')) {
        const auth = useAuthStore();
        if (auth.loggedIn) {
          message.warning($t('account.sessionExpired'));
          console.log('Running logout sequence in reaction to 401 response...');
          await auth.logout(true);
        } else {
          message.error($t('errors.noAccess', { resource: response.url || '/' }));
          console.log("Oh no! You don't seem to have access to this resource!");
        }
      }
    } else if (response.status === 403 && responseBodyText.includes('CSRF')) {
      // show CSRF/XSRF error on 403 response mentioning CSRF
      message.error($t('errors.csrf'));
    } else if (response.status === 500) {
      message.error($t('errors.unexpected'));
    } else if (response.status >= 400 && response.status !== 404) {
      // it's some other kind of error,
      // so pass the response body to the error message util...
      try {
        useErrors().msg(await response.clone().json());
      } catch (e) {
        console.error(e);
      }
    }
  },
};

const client = createClient<paths>({ baseUrl: apiUrl });
client.use(interceptors);

export const { GET, POST, PUT, PATCH, DELETE } = client;

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

export function getFullUrl(path: string, query?: Record<string, unknown>): URL {
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

export function downloadData(blob: Blob, filename: string) {
  const a = document.createElement('a');
  a.href = window.URL.createObjectURL(blob);
  if (filename) {
    a.download = filename;
  }
  a.click();
  a.remove();
}

// export some common platform properties for use throughout codebase

export const accentColorPresets = [
  '#384a71', // indigo
  '#386C71', // teal
  '#38714b', // green
  '#716938', // olive
  '#715938', // coffee
  '#713839', // dark red
  '#71384e', // aubergine
  '#6c3871', // violet
];

export const resourceTypes = [
  {
    name: 'plainText',
    searchableQuick: true,
    searchableAdv: true,
    contentContext: true,
  },
  {
    name: 'richText',
    searchableQuick: true,
    searchableAdv: true,
    contentContext: false,
  },
  {
    name: 'textAnnotation',
    searchableQuick: true,
    searchableAdv: true,
    contentContext: true,
  },
  {
    name: 'audio',
    searchableQuick: true,
    searchableAdv: true,
    contentContext: true,
  },
  {
    name: 'images',
    searchableQuick: true,
    searchableAdv: true,
    contentContext: true,
  },
  {
    name: 'externalReferences',
    searchableQuick: true,
    searchableAdv: true,
    contentContext: true,
  },
  {
    name: 'apiCall',
    searchableQuick: false,
    searchableAdv: false,
    contentContext: false,
  },
];

export const prioritizedMetadataKeys = ['author', 'year', 'language'];

export const deeplSourceLanguages = [
  'ar',
  'bg',
  'cs',
  'da',
  'de',
  'el',
  'en',
  'es',
  'et',
  'fi',
  'fr',
  'hu',
  'id',
  'it',
  'ja',
  'ko',
  'lt',
  'lv',
  'nb',
  'nl',
  'pl',
  'pt',
  'ro',
  'ru',
  'sk',
  'sl',
  'sv',
  'tr',
  'uk',
  'zh',
];

export const deeplTargetLanguages = [
  'ar',
  'bg',
  'cs',
  'da',
  'de',
  'el',
  'en-gb',
  'en-us',
  'es',
  'et',
  'fi',
  'fr',
  'hu',
  'id',
  'it',
  'ja',
  'ko',
  'lt',
  'lv',
  'nb',
  'nl',
  'pl',
  'pt-br',
  'pt-pt',
  'ro',
  'ru',
  'sk',
  'sl',
  'sv',
  'tr',
  'uk',
  'zh-hans',
  'zh-hant',
];

// export components types for use throughout codebase

// general

export type TekstErrorModel = components['schemas']['TekstErrorModel'];
export type ErrorDetail = components['schemas']['ErrorDetail'];
export type ErrorModel = components['schemas']['ErrorModel'];
export type HTTPValidationError = components['schemas']['HTTPValidationError'];
export type IndexInfoResponse = components['schemas']['IndexInfo'][];
export type TaskRead = components['schemas']['TaskRead'];

export type MetadataEntry = components['schemas']['MetadataEntry'];
export type Metadata = MetadataEntry[];
export type LocaleKey = components['schemas']['LocaleKey'];
export type TranslationLocaleKey = components['schemas']['TranslationLocaleKey'];
export type Translation = components['schemas']['TextLevelTranslation'];
export type ResourceExportFormat = NonNullable<
  NonNullable<paths['/resources/{id}/export']['get']['parameters']['query']>['format']
>;

// browse

export type LocationDataQuery = paths['/browse']['get']['parameters']['query'];

// bookmark

export type BookmarkRead = components['schemas']['BookmarkRead'];
export type BookmarkCreate = components['schemas']['BookmarkCreate'];

// correction

export type CorrectionRead = components['schemas']['CorrectionRead'];
export type CorrectionCreate = components['schemas']['CorrectionCreate'];

// user

export type UserCreate = components['schemas']['UserCreate'];
export type UserRead = components['schemas']['UserRead'];
export type UserUpdate = components['schemas']['UserUpdate'];
export type UserReadPublic = components['schemas']['UserReadPublic'];
export type UserUpdateUserNotificationTriggers =
  components['schemas']['UserUpdate']['userNotificationTriggers'];
export type UserUpdateAdminNotificationTriggers =
  components['schemas']['UserUpdate']['adminNotificationTriggers'];
export type UserUpdatePublicFields = components['schemas']['UserUpdate']['publicFields'];

// user messages

export type UserMessageCreate = components['schemas']['UserMessageCreate'];
export type UserMessageRead = components['schemas']['UserMessageRead'];
export type UserMessageThread = components['schemas']['UserMessageThread'];

// text and text structure

export type TextCreate = components['schemas']['TextCreate'];
export type TextRead = components['schemas']['TextRead'];
export type TextUpdate = components['schemas']['TextUpdate'];
export type LocationRead = components['schemas']['LocationRead'];
export type LocationData = components['schemas']['LocationData'];

// platform

export type PlatformData = components['schemas']['PlatformData'];
export type PlatformStateUpdate = components['schemas']['PlatformStateUpdate'];
export type ResourceCoverage = components['schemas']['ResourceCoverage'];

// client segments

export type ClientSegmentRead = components['schemas']['ClientSegmentRead'];
export type ClientSegmentCreate = components['schemas']['ClientSegmentCreate'];
export type ClientSegmentUpdate = components['schemas']['ClientSegmentUpdate'];
export type ClientSegmentHead = components['schemas']['ClientSegmentHead'];

// resources

export type ResourceType = AnyResourceRead['resourceType'];
export type SearchableResourceType = Exclude<ResourceType, 'apiCall'>;
type ResourceReadExtras = {
  active?: boolean;
  corrections?: number;
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

export type TextAnnotationContentRead = components['schemas']['TextAnnotationContentRead'];
export type TextAnnotationContentCreate = components['schemas']['TextAnnotationContentCreate'];
export type TextAnnotationResourceCreate = components['schemas']['TextAnnotationResourceCreate'];
export type TextAnnotationResourceRead = components['schemas']['TextAnnotationResourceRead'] &
  ResourceReadExtras & {
    contents?: TextAnnotationContentRead[];
  };
export type AnnotationAggregation = components['schemas']['AnnotationAggregation'];

export type AudioContentRead = components['schemas']['AudioContentRead'];
export type AudioContentCreate = components['schemas']['AudioContentCreate'];
export type AudioResourceCreate = components['schemas']['AudioResourceCreate'];
export type AudioResourceRead = components['schemas']['AudioResourceRead'] &
  ResourceReadExtras & {
    contents?: AudioContentRead[];
  };

export type ImagesContentRead = components['schemas']['ImagesContentRead'];
export type ImagesContentCreate = components['schemas']['ImagesContentCreate'];
export type ImagesResourceCreate = components['schemas']['ImagesResourceCreate'];
export type ImagesResourceRead = components['schemas']['ImagesResourceRead'] &
  ResourceReadExtras & {
    contents?: ImagesContentRead[];
  };

export type ExternalReferencesContentRead = components['schemas']['ExternalReferencesContentRead'];
export type ExternalReferencesContentCreate =
  components['schemas']['ExternalReferencesContentCreate'];
export type ExternalReferencesResourceCreate =
  components['schemas']['ExternalReferencesResourceCreate'];
export type ExternalReferencesResourceRead =
  components['schemas']['ExternalReferencesResourceRead'] &
    ResourceReadExtras & {
      contents?: ExternalReferencesContentRead[];
    };

export type ApiCallContentRead = components['schemas']['ApiCallContentRead'];
export type ApiCallContentCreate = components['schemas']['ApiCallContentCreate'];
export type ApiCallResourceCreate = components['schemas']['ApiCallResourceCreate'];
export type ApiCallResourceRead = components['schemas']['ApiCallResourceRead'] &
  ResourceReadExtras & {
    contents?: ApiCallContentRead[];
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
export type TextAnnotationResourceConfig = components['schemas']['TextAnnotationResourceConfig'];

export type CommonResourceConfig = components['schemas']['CommonResourceConfig'];
export type AnyResourceConfig = AnyResourceRead['config'];
export type LineLabellingConfig = components['schemas']['LineLabellingConfig'];
export type DeepLLinksConfig = components['schemas']['DeepLLinksConfig'];

// search

export type SearchResults = components['schemas']['SearchResults'];
export type SearchHit = components['schemas']['SearchHit'];
export type QuickSearchRequestBody = components['schemas']['QuickSearchRequestBody'];
export type AdvancedSearchRequestBody = components['schemas']['AdvancedSearchRequestBody'];
export type SortingPreset = components['schemas']['SortingPreset'];
export type SearchPagination = { pg: number; pgs: number };
export type ResourceSearchQuery = components['schemas']['ResourceSearchQuery'];

export type PlainTextSearchQuery = components['schemas']['PlainTextSearchQuery'];
export type RichTextSearchQuery = components['schemas']['RichTextSearchQuery'];
export type TextAnnotationSearchQuery = components['schemas']['TextAnnotationSearchQuery'];
export type AudioSearchQuery = components['schemas']['AudioSearchQuery'];
export type ImagesSearchQuery = components['schemas']['ImagesSearchQuery'];
export type ExternalReferencesSearchQuery = components['schemas']['ExternalReferencesSearchQuery'];

export type PublicUserSearchFilters = NonNullable<
  paths['/users/public']['get']['parameters']['query']
>;
export type UserSearchFilters = NonNullable<paths['/users']['get']['parameters']['query']>;
export type UsersSearchResult = components['schemas']['UsersSearchResult'];

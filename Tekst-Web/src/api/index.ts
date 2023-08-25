import createClient from 'openapi-fetch';
import type { paths, components } from '@/api/schema';
import queryString from 'query-string';

const serverUrl: string | undefined = import.meta.env.TEKST_SERVER_URL;
const apiPath: string | undefined = import.meta.env.TEKST_API_PATH;
const apiUrl = (serverUrl && apiPath && serverUrl + apiPath) || '/';

// custom, monkeypatched "fetch" for implementing interceptors
const customFetch = async (input: RequestInfo | URL, init?: RequestInit | undefined) => {
  // (see: https://blog.logrocket.com/intercepting-javascript-fetch-api-requests-responses/)
  // --- request interceptors go here... ---
  // TODO: intercept requests and add XSRF-token to header
  const response = await globalThis.fetch(input, init);
  // --- response interceptors go here... ---
  if (response.status === 401) {
    // TODO: logout and cleanup
    // if (error.response.status === 401 && !error.response.config.url.endsWith('/logout')) {
    //   console.log('401 response');
    //   const auth = useAuthStore();
    //   if (auth.loggedIn) {
    //     console.log('Running logout sequence in reaction to 401 response');
    //     auth.logout();
    //   }
    // }
    console.log('401 DETECTED! OH NO!');
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

// // USE LIKE THIS:

// <script setup lang="ts">
// import { ref } from 'vue';
// import { POST, GET, optionsPresets } from './api';
// import type {components} from '@/api/types.d.ts'

// type TextRead = components['schemas']['TextRead'];

// const texts = ref<TextRead[]>([]);

// async function handleClickLogin(){
//   const { error } = await POST(
//     '/auth/cookie/login',
//     {
//       body: {
//         username: 'superuser@test.com',
//         password: 'poiPOI098'
//       },
//       ...optionsPresets.formUrlEncoded
//     });
//   if (error) {
//     console.error(`NOGOOD: ${error}`);
//   } else {
//     console.log("LOGGED IN!")
//   }
// }

// async function handleClickTexts(){
//   const { data, error } = await GET(
//     '/texts',
//     { params: {} });
//   if (error) {
//     console.error(error);
//   } else {
//     texts.value = data;
//   }
// }

// async function handleClick401(){
//   const { data, error } = await POST('/nodes', {body: {
//     textId: '5eb7cf5a86d9755df3a6c593',
//     level: 0,
//     position: 0,
//     label: 'Hello',
//   }});
//   if (error) {
//     console.error(error);
//   } else {
//     console.log(`Created ${data}`)
//   }
// }
// </script>

// <template>
//   <button type="button" @click="handleClickLogin">Login</button>
//   <button type="button" @click="handleClickTexts">Texts</button>
//   <button type="button" @click="handleClick401">401</button>
//   <div v-for="text in texts" :key="text.id">
//     {{ text.title }}
//   </div>
// </template>

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

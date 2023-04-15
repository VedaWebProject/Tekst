import type { BaseAPI } from '@/openapi/base';
import { Configuration } from '@/openapi';

const SERVER_URL: string | undefined = import.meta.env.TEKST_SERVER_URL;
const API_PATH: string | undefined = import.meta.env.TEKST_API_PATH;
const API_URL = SERVER_URL && API_PATH && SERVER_URL + API_PATH;

const apiConfig = new Configuration({ basePath: API_URL || '/' });

export function configureApi<ApiType extends BaseAPI>(
  ApiClass: new (...args: any[]) => ApiType
): ApiType {
  return new ApiClass(apiConfig);
}

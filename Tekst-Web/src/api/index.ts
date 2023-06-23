import type { BaseAPI } from '@/openapi/base';
import {
  AdminApi,
  AuthApi,
  Configuration,
  LayersApi,
  NodesApi,
  PlatformApi,
  TextsApi,
  UnitsApi,
  UsersApi,
  BrowseApi,
} from '@/openapi';

const serverUrl: string | undefined = import.meta.env.TEKST_SERVER_URL;
const apiPath: string | undefined = import.meta.env.TEKST_API_PATH;
const apiUrl = (serverUrl && apiPath && serverUrl + apiPath) || '/';
const apiConfig = new Configuration({ basePath: apiUrl });

function configureApi<ApiType extends BaseAPI>(ApiClass: new (...args: any[]) => ApiType): ApiType {
  return new ApiClass(apiConfig);
}

const api = {
  platformApi: configureApi(PlatformApi),
  adminApi: configureApi(AdminApi),
  authApi: configureApi(AuthApi),
  usersApi: configureApi(UsersApi),
  textsApi: configureApi(TextsApi),
  nodesApi: configureApi(NodesApi),
  layersApi: configureApi(LayersApi),
  unitsApi: configureApi(UnitsApi),
  browseApi: configureApi(BrowseApi),
};

export function useApi() {
  return { ...api };
}

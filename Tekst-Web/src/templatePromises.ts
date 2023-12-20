import { createTemplatePromise } from '@vueuse/core';
import type { RouteLocationRaw } from 'vue-router';
import type { UserReadPublic } from './api';

export const LoginTemplatePromise = createTemplatePromise<
  // promise resolve type
  boolean,
  // extra args
  [
    // login modal message
    string | undefined,
    // route to change to after login
    RouteLocationRaw | undefined,
    // display register button
    boolean,
  ]
>();

export const PromptTemplatePromise = createTemplatePromise<
  // promise resolve type
  string,
  // extra args
  [
    // title
    string | undefined,
    // message
    string | undefined,
    // preset value
    string | undefined,
  ]
>();

export const TransferResourceTemplatePromise = createTemplatePromise<UserReadPublic>();

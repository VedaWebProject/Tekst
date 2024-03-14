import { type Component } from 'vue';
import PlainTextSearchFormItems from './PlainTextSearchFormItems.vue';

export const resourceTypeSearchForms: Record<string, Component> = {
  plainText: PlainTextSearchFormItems,
};

import { type Component } from 'vue';
import PlainTextSearchFormItems from './PlainTextSearchFormItems.vue';
import RichTextSearchFormItems from './RichTextSearchFormItems.vue';

export const resourceTypeSearchForms: Record<string, Component> = {
  plainText: PlainTextSearchFormItems,
  richText: RichTextSearchFormItems,
};

import { type Component } from 'vue';
import AudioSearchFormItems from './AudioSearchFormItems.vue';
import ExternalReferencesSearchFormItems from './ExternalReferencesSearchFormItems.vue';
import ImagesSearchFormItems from './ImagesSearchFormItems.vue';
import PlainTextSearchFormItems from './PlainTextSearchFormItems.vue';
import RichTextSearchFormItems from './RichTextSearchFormItems.vue';
import TextAnnotationSearchFormItems from './TextAnnotationSearchFormItems.vue';

export const resourceTypeSearchForms: Record<string, Component> = {
  plainText: PlainTextSearchFormItems,
  richText: RichTextSearchFormItems,
  textAnnotation: TextAnnotationSearchFormItems,
  audio: AudioSearchFormItems,
  images: ImagesSearchFormItems,
  externalReferences: ExternalReferencesSearchFormItems,
};

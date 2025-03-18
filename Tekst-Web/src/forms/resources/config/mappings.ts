import { type Component } from 'vue';
import ApiCallSpecialConfigFormItems from './ApiCallSpecialConfigFormItems.vue';
import ContentCssFormItems from './ContentCssFormItems.vue';
import DefaultCollapsedFormItems from './DefaultCollapsedFormItems.vue';
import FocusViewConfigFormItems from './FocusViewConfigFormItems.vue';
import LocationMetadataSpecialConfigFormItems from './LocationMetadataSpecialConfigFormItems.vue';
import PlainTextSpecialConfigFormItems from './PlainTextSpecialConfigFormItems.vue';
import ResourceFontFormItems from './ResourceFontFormItems.vue';
import SearchReplacementsConfigFormItems from './SearchReplacementsConfigFormItems.vue';
import TextAnnotationSpecialConfigFormItems from './TextAnnotationSpecialConfigFormItems.vue';

export const generalConfigFormItems: Record<string, Component> = {
  defaultCollapsed: DefaultCollapsedFormItems,
  focusView: FocusViewConfigFormItems,
  font: ResourceFontFormItems,
  searchReplacements: SearchReplacementsConfigFormItems,
  contentCss: ContentCssFormItems,
};

export const specialConfigFormItems: Record<string, Component> = {
  plainText: PlainTextSpecialConfigFormItems,
  textAnnotation: TextAnnotationSpecialConfigFormItems,
  locationMetadata: LocationMetadataSpecialConfigFormItems,
  apiCall: ApiCallSpecialConfigFormItems,
};

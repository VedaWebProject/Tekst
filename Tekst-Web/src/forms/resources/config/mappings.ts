import ApiCallSpecialConfigFormItems from '@/forms/resources/config/ApiCallSpecialConfigFormItems.vue';
import ContentCssFormItems from '@/forms/resources/config/ContentCssFormItems.vue';
import DefaultCollapsedFormItems from '@/forms/resources/config/DefaultCollapsedFormItems.vue';
import FocusViewConfigFormItems from '@/forms/resources/config/FocusViewConfigFormItems.vue';
import PlainTextSpecialConfigFormItems from '@/forms/resources/config/PlainTextSpecialConfigFormItems.vue';
import ResourceFontFormItems from '@/forms/resources/config/ResourceFontFormItems.vue';
import SearchReplacementsConfigFormItems from '@/forms/resources/config/SearchReplacementsConfigFormItems.vue';
import TextAnnotationSpecialConfigFormItems from '@/forms/resources/config/TextAnnotationSpecialConfigFormItems.vue';
import { type Component } from 'vue';

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
  apiCall: ApiCallSpecialConfigFormItems,
};

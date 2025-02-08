import ApiCallSpecialConfigFormItems from '@/forms/resources/config/ApiCallSpecialConfigFormItems.vue';
import DefaultCollapsedFormItems from '@/forms/resources/config/DefaultCollapsedFormItems.vue';
import PlainTextSpecialConfigFormItems from '@/forms/resources/config/PlainTextSpecialConfigFormItems.vue';
import ReducedViewConfigFormItems from '@/forms/resources/config/ReducedViewConfigFormItems.vue';
import ResourceFontFormItems from '@/forms/resources/config/ResourceFontFormItems.vue';
import SearchReplacementsConfigFormItems from '@/forms/resources/config/SearchReplacementsConfigFormItems.vue';
import TextAnnotationSpecialConfigFormItems from '@/forms/resources/config/TextAnnotationSpecialConfigFormItems.vue';
import { type Component } from 'vue';

export const generalConfigFormItems: Record<string, Component> = {
  defaultCollapsed: DefaultCollapsedFormItems,
  reducedView: ReducedViewConfigFormItems,
  font: ResourceFontFormItems,
  searchReplacements: SearchReplacementsConfigFormItems,
};

export const specialConfigFormItems: Record<string, Component> = {
  plainText: PlainTextSpecialConfigFormItems,
  textAnnotation: TextAnnotationSpecialConfigFormItems,
  apiCall: ApiCallSpecialConfigFormItems,
};

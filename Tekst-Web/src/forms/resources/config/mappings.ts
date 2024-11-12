import { type Component } from 'vue';
import LineLabellingConfigFormItems from '@/forms/resources/config/LineLabellingConfigFormItems.vue';
import DeepLLinksConfigFormItems from '@/forms/resources/config/DeepLLinksConfigFormItems.vue';
import ReducedViewConfigFormItems from '@/forms/resources/config/ReducedViewConfigFormItems.vue';
import DefaultCollapsedFormItems from '@/forms/resources/config/DefaultCollapsedFormItems.vue';
import ResourceFontFormItems from '@/forms/resources/config/ResourceFontFormItems.vue';
import DisplayTemplateConfigFormItems from '@/forms/resources/config/DisplayTemplateConfigFormItems.vue';
import AnnotationGroupsFormItems from '@/forms/resources/config/AnnotationGroupsFormItems.vue';
import MultiValueDelimiterConfigFormItems from '@/forms/resources/config/MultiValueDelimiterConfigFormItems.vue';

export const generalConfigFormItems: Record<string, Component> = {
  defaultCollapsed: DefaultCollapsedFormItems,
  reducedView: ReducedViewConfigFormItems,
  font: ResourceFontFormItems,
};

export const specialConfigFormItems: Record<string, Component> = {
  lineLabelling: LineLabellingConfigFormItems,
  deeplLinks: DeepLLinksConfigFormItems,
  displayTemplate: DisplayTemplateConfigFormItems,
  annotationGroups: AnnotationGroupsFormItems,
  multiValueDelimiter: MultiValueDelimiterConfigFormItems,
};

import { type Component } from 'vue';
import LineLabellingConfigFormItems from '@/forms/resources/config/LineLabellingConfigFormItems.vue';
import DeepLLinksConfigFormItems from '@/forms/resources/config/DeepLLinksConfigFormItems.vue';
import ReducedViewOnelineFormItems from '@/forms/resources/config/ReducedViewOnelineFormItems.vue';
import DefaultCollapsedFormItems from '@/forms/resources/config/DefaultCollapsedFormItems.vue';
import ResourceFontFormItems from '@/forms/resources/config/ResourceFontFormItems.vue';
import DisplayTemplateConfigFormItems from '@/forms/resources/config/DisplayTemplateConfigFormItems.vue';
import MultiValueDelimiterConfigFormItems from './MultiValueDelimiterConfigFormItems.vue';

export const generalConfigFormItems: Record<string, Component> = {
  defaultCollapsed: DefaultCollapsedFormItems,
  reducedViewOneline: ReducedViewOnelineFormItems,
  font: ResourceFontFormItems,
};

export const specialConfigFormItems: Record<string, Component> = {
  lineLabelling: LineLabellingConfigFormItems,
  deeplLinks: DeepLLinksConfigFormItems,
  displayTemplate: DisplayTemplateConfigFormItems,
  multiValueDelimiter: MultiValueDelimiterConfigFormItems,
};

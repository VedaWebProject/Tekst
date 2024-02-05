import { type Component } from 'vue';
import DeepLLinksConfigFormItems from '@/forms/resources/DeepLLinksConfigFormItems.vue';
import ReducedViewOnelineFormItems from '@/forms/resources/ReducedViewOnelineFormItems.vue';
import DefaultCollapsedFormItems from '@/forms/resources/DefaultCollapsedFormItems.vue';
import ResourceFontFormItems from '@/forms/resources/ResourceFontFormItems.vue';

export const generalConfigFormItems: Record<string, Component> = {
  defaultCollapsed: DefaultCollapsedFormItems,
  reducedViewOneline: ReducedViewOnelineFormItems,
  font: ResourceFontFormItems,
};

export const specialConfigFormItems: Record<string, Component> = {
  deeplLinks: DeepLLinksConfigFormItems,
};

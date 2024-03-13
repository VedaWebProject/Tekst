import { type Component } from 'vue';
import DeepLLinksConfigFormItems from '@/forms/resources/config/DeepLLinksConfigFormItems.vue';
import ReducedViewOnelineFormItems from '@/forms/resources/config/ReducedViewOnelineFormItems.vue';
import DefaultCollapsedFormItems from '@/forms/resources/config/DefaultCollapsedFormItems.vue';
import ResourceFontFormItems from '@/forms/resources/config/ResourceFontFormItems.vue';

export const generalConfigFormItems: Record<string, Component> = {
  defaultCollapsed: DefaultCollapsedFormItems,
  reducedViewOneline: ReducedViewOnelineFormItems,
  font: ResourceFontFormItems,
};

export const specialConfigFormItems: Record<string, Component> = {
  deeplLinks: DeepLLinksConfigFormItems,
};

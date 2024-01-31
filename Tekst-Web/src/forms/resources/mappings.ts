import { type Component } from 'vue';
import DeepLLinksConfigFormItems from '@/forms/resources/DeepLLinksConfigFormItems.vue';
import ReducedViewOnelineFormItems from '@/forms/resources/ReducedViewOnelineFormItems.vue';
import DefaultCollapsedFormItems from '@/forms/resources/DefaultCollapsedFormItems.vue';

export const generalConfigFormItems: Record<string, Component> = {
  defaultCollapsed: DefaultCollapsedFormItems,
  reducedViewOneline: ReducedViewOnelineFormItems,
};

export const specialConfigFormItems: Record<string, Component> = {
  reducedViewOneline: ReducedViewOnelineFormItems,
  defaultCollapsed: DefaultCollapsedFormItems,
  deeplLinks: DeepLLinksConfigFormItems,
};

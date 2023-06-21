import { defineAsyncComponent, type Component } from 'vue';

const unitWidgets: Record<string, Component> = {
  deeplLinks: defineAsyncComponent(
    () => import('@/components/browse/widgets/DeepLLinksWidget.vue')
  ),
};

export default unitWidgets;

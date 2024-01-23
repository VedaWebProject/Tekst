import { defineAsyncComponent, type Component } from 'vue';

const contentWidgets: Record<string, Component> = {
  deeplLinks: defineAsyncComponent(
    () => import('@/components/browse/widgets/DeepLLinksWidget.vue')
  ),
};

export default contentWidgets;

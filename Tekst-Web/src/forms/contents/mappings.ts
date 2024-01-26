import { type Component } from 'vue';
import PlainTextFormItems from '@/forms/contents/PlainTextFormItems.vue';
import RichTextFormItems from '@/forms/contents/RichTextFormItems.vue';

const resourceContentFormItems: Record<string, Component> = {
  plainText: PlainTextFormItems,
  richText: RichTextFormItems,
};

export default resourceContentFormItems;

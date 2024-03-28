import { type Component } from 'vue';
import PlainTextFormItems from '@/forms/contents/PlainTextFormItems.vue';
import RichTextFormItems from '@/forms/contents/RichTextFormItems.vue';
import TextAnnotationFormItems from '@/forms/contents/TextAnnotationFormItems.vue';

const resourceContentFormItems: Record<string, Component> = {
  plainText: PlainTextFormItems,
  richText: RichTextFormItems,
  textAnnotation: TextAnnotationFormItems,
};

export default resourceContentFormItems;

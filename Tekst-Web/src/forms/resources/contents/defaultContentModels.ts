const common = {
  comment: undefined,
  notes: undefined,
};

export const defaultContentModels = {
  plainText: {
    ...common,
    text: '',
  },
  richText: {
    ...common,
    html: '',
  },
  textAnnotation: {
    ...common,
    tokens: [
      {
        token: undefined,
        annotations: [],
      },
    ],
  },
  audio: {
    ...common,
    files: [
      {
        url: undefined,
        caption: undefined,
      },
    ],
  },
};

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
};

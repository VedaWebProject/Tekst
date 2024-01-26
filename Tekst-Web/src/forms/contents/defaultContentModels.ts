const common = {
  comment: undefined,
  notes: undefined,
};

export const defaultContentModels = {
  plainText: {
    ...common,
    text: '',
  },
  debug: {
    ...common,
    text: '',
  },
};

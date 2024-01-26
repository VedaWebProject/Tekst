export type PromptModalProps = {
  show?: boolean;
  actionKey?: string;
  initialValue?: string;
  inputLabel?: string;
  title?: string;
  multiline?: boolean;
  rows?: number;
  disableOkWhenNoValue?: boolean;
};

export interface HelpText {
  title: string | null;
  content: string;
}

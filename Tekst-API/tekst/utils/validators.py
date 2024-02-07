from pydantic.functional_validators import AfterValidator

from tekst.utils.strings import cleanup_spaces_multiline, cleanup_spaces_oneline


EmptyStringToNone = AfterValidator(lambda s: s or None)
CleanupOneline = AfterValidator(cleanup_spaces_oneline)
CleanupMultiline = AfterValidator(cleanup_spaces_multiline)

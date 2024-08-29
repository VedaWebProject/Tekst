# Quick Search

## Operators

- `+` signifies AND operation
- `|` signifies OR operation
- `-` negates a single token
- `"` wraps a sequence of tokens to signify a phrase for searching
- `*` at the end of a term signifies a prefix query
- `(` and `)` signify search operator precedence
- `~N` after a word signifies edit distance (fuzziness), where `N` is a digit
- `~N` after a phrase signifies slop amount, where `N` is a digit

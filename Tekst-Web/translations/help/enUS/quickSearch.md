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


## Settings

### Texts
Decides which texts are searched.

### All terms must occur
With “_All terms must occur_” you can decide how individual search terms should be logically linked to each other. If the function is activated, only locations with contents that contain hits for all the search terms entered will be found. Otherwise, the locations with the most hits will be given a higher rank in the search results than those with fewer hits.

### Interpret Regular Expressions
The Quick Search is capable of running search queries based on a Regular Expression. Switching this setting _on_ will **disable the standard search operators listed above**!

The expression _must_ match a whole term in any case, so don't use anchors (`^` at the beginning and `$` at the end of the expression). For an overview of the available RegExp syntax, please see [the Elasticsearch documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/regexp-syntax.html).

### Respect diacritics
If this function is activated, entered or missing (!) diacritics are taken into account in the search and only content with the same use of diacritics is found.

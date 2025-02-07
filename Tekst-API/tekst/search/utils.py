from typing import Any

from tekst.models.resource import ResourceBaseDocument
from tekst.resources import resource_types_mgr


def add_analysis_settings(
    *,
    for_resource: ResourceBaseDocument,
    to_analysis: dict[str, Any],
) -> None:
    res_id_str = str(for_resource.id)

    # SEARCH REPLACEMENTS
    # (This is currently only implemented for plain text resources – which use a
    # "text" type field for their content. If the search replacements feature is to be
    # implemented for resource types that use keyword fields, this section should be
    # extended/modified to create a normalizer instead of an analyzer!)
    if (
        for_resource.resource_type == "plainText"
        and hasattr(for_resource.config, "general")
        and hasattr(for_resource.config.general, "search_replacements")
    ):
        if "char_filter" not in to_analysis:
            to_analysis["char_filter"] = {}
        if "analyzer" not in to_analysis:
            to_analysis["analyzer"] = {}
        for index, search_replacement in enumerate(
            for_resource.config.general.search_replacements
        ):
            filter_name = f"{res_id_str}_search_replacements_{index}"
            to_analysis["char_filter"][filter_name] = {
                "type": "pattern_replace",
                "pattern": search_replacement["pattern"],
                "replacement": search_replacement["replacement"],
            }
            # add char filter to custom standard (strict) analyzer
            if not to_analysis["analyzer"].get(res_id_str):
                to_analysis["analyzer"][res_id_str] = {
                    "filter": ["lowercase"],
                    "char_filter": [],
                    "tokenizer": "standard",
                }
            to_analysis["analyzer"][res_id_str]["char_filter"].append(filter_name)
            # add char filter to custom no_diacritics analyzer
            no_diac_analyzer = f"{res_id_str}_no_diacritics"
            if not to_analysis["analyzer"].get(no_diac_analyzer):
                to_analysis["analyzer"][no_diac_analyzer] = {
                    "filter": ["no_diacritics", "lowercase"],
                    "char_filter": [],
                    "tokenizer": "standard",
                }
            to_analysis["analyzer"][no_diac_analyzer]["char_filter"].append(filter_name)


def add_mappings(
    *,
    for_resource: ResourceBaseDocument,
    to_mappings: dict[str, Any],
) -> None:
    to_mappings[str(for_resource.id)] = {
        "properties": resource_types_mgr.get(
            for_resource.resource_type
        ).index_doc_props(for_resource),
    }

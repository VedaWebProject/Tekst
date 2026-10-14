import os
import re
import shutil
import zipfile

from datetime import datetime
from pathlib import Path
from typing import cast
from urllib.parse import quote

import click
import humanize

from beanie import PydanticObjectId
from beanie.operators import Eq, In

from tekst import db, resources
from tekst.config import get_config
from tekst.errors import TekstHTTPException
from tekst.i18n import pick_translation
from tekst.models.resource import (
    ResourceBaseDocument,
    ResourceExportFormat,
    res_exp_fmt_info,
)
from tekst.models.text import TextDocument
from tekst.routers.resources import export_resource_contents_task
from tekst.state import get_state
from tekst.utils import ensure


def _make_dir_browsable(
    path: Path,
    *,
    output_file: Path,
    filename_glob: str = "*",
    title: str = "Index",
    is_root_dir: bool = True,
):
    """
    This is a heavily modified version of https://github.com/joshbrunty/Indexer
    """

    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    * { padding: 0; margin: 0; }
    body {
        font-family: sans-serif;
        text-rendering: optimizespeed;
        background-color: #ffffff;
    }
    a {
        color: #006ed3;
        text-decoration: none;
    }
    a:hover,
    h1 a:hover {
        color: #319cff;
    }
    header,
    #summary {
        padding-left: 5%;
        padding-right: 5%;
    }
    th:first-child,
    td:first-child {
        width: 5%;
    }
    th:last-child,
    td:last-child {
        width: 5%;
    }
    header {
        padding-top: 25px;
        padding-bottom: 15px;
        background-color: #f2f2f2;
    }
    h1 {
        font-size: 20px;
        font-weight: normal;
        white-space: nowrap;
        overflow-x: hidden;
        text-overflow: ellipsis;
        color: #999;
    }
    h1 a {
        color: #000;
        margin: 0 4px;
    }
    h1 a:hover {
        text-decoration: underline;
    }
    h1 a:first-child {
        margin: 0;
    }
    main {
        display: block;
    }
    .meta {
        font-size: 12px;
        font-family: Verdana, sans-serif;
        border-bottom: 1px solid #9C9C9C;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .meta-item {
        margin-right: 1em;
    }
    #filter {
        padding: 4px;
        border: 1px solid #CCC;
    }
    table {
        width: 100%;
        border-collapse: collapse;
    }
    tr {
        border-bottom: 1px dashed #dadada;
    }
    tbody tr:hover {
        background-color: #ffffec;
    }
    th,
    td {
        text-align: left;
        padding: 10px 0;
    }
    th {
        padding-top: 15px;
        padding-bottom: 15px;
        font-size: 16px;
        white-space: nowrap;
    }
    th a {
        color: black;
    }
    th svg {
        vertical-align: middle;
    }
    td {
        white-space: nowrap;
        font-size: 14px;
    }
    td:nth-child(2) {
        width: 80%;
    }
    td:nth-child(3) {
        padding: 0 20px 0 20px;
    }
    th:nth-child(4),
    td:nth-child(4) {
        text-align: right;
    }
    td:nth-child(2) svg {
        position: absolute;
    }
    td .name {
        margin-left: 1.75em;
        word-break: break-all;
        overflow-wrap: break-word;
        white-space: pre-wrap;
    }
    td .goup {
        margin-left: 1.75em;
        padding: 0;
        word-break: break-all;
        overflow-wrap: break-word;
        white-space: pre-wrap;
    }
    .icon {
        margin-right: 5px;
    }
    tr.clickable {
        cursor: pointer;
    }
    tr.clickable a {
        display: block;
    }
    @media (max-width: 600px) {
        * {
            font-size: 1.06rem;
        }
        .hideable {
            display: none;
        }
        td:nth-child(2) {
            width: auto;
        }
        th:nth-child(3),
        td:nth-child(3) {
            padding-right: 5%;
            text-align: right;
        }
        h1 {
            color: #000;
        }
        h1 a {
            margin: 0;
        }
        #filter {
            max-width: 100px;
        }
    }
    </style>
</head>
<body>
    <svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" height="0" width="0" style="position: absolute;">
    <defs>
        <!-- Go-up -->
        <g id="go-up">
            <path d="M10,9V5L3,12L10,19V14.9C15,14.9 18.5,16.5 21,20C20,15 17,10 10,9Z" fill="#696969"/>
        </g>
        <!-- Folder -->
        <g id="folder" fill-rule="nonzero" fill="none">
            <path d="M285.22 37.55h-142.6L110.9 0H31.7C14.25 0 0 16.9 0 37.55v75.1h316.92V75.1c0-20.65-14.26-37.55-31.7-37.55z" fill="#FFA000"/>
            <path d="M285.22 36H31.7C14.25 36 0 50.28 0 67.74v158.7c0 17.47 14.26 31.75 31.7 31.75H285.2c17.44 0 31.7-14.3 31.7-31.75V67.75c0-17.47-14.26-31.75-31.7-31.75z" fill="#FFCA28"/>
        </g>
        <g id="folder-shortcut" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
            <g id="folder-shortcut-group" fill-rule="nonzero">
                <g id="folder-shortcut-shape">
                    <path d="M285.224876,37.5486902 L142.612438,37.5486902 L110.920785,0 L31.6916529,0 C14.2612438,0 0,16.8969106 0,37.5486902 L0,112.646071 L316.916529,112.646071 L316.916529,75.0973805 C316.916529,54.4456008 302.655285,37.5486902 285.224876,37.5486902 Z" id="Shape" fill="#FFA000"></path>
                    <path d="M285.224876,36 L31.6916529,36 C14.2612438,36 0,50.2838568 0,67.7419039 L0,226.451424 C0,243.909471 14.2612438,258.193328 31.6916529,258.193328 L285.224876,258.193328 C302.655285,258.193328 316.916529,243.909471 316.916529,226.451424 L316.916529,67.7419039 C316.916529,50.2838568 302.655285,36 285.224876,36 Z" id="Shape" fill="#FFCA28"></path>
                </g>
                <path d="M126.154134,250.559184 C126.850974,251.883673 127.300549,253.006122 127.772602,254.106122 C128.469442,255.206122 128.919016,256.104082 129.638335,257.002041 C130.559962,258.326531 131.728855,259 133.100057,259 C134.493737,259 135.415364,258.55102 136.112204,257.67551 C136.809044,257.002041 137.258619,255.902041 137.258619,254.577551 C137.258619,253.904082 137.258619,252.804082 137.033832,251.457143 C136.786566,249.908163 136.561779,249.032653 136.561779,248.583673 C136.089726,242.814286 135.864939,237.920408 135.864939,233.273469 C135.864939,225.057143 136.786566,217.514286 138.180246,210.846939 C139.798713,204.202041 141.889234,198.634694 144.429328,193.763265 C147.216689,188.869388 150.678411,184.873469 154.836973,181.326531 C158.995535,177.779592 163.626149,174.883673 168.481552,172.661224 C173.336954,170.438776 179.113983,168.665306 185.587852,167.340816 C192.061722,166.218367 198.760378,165.342857 205.481514,164.669388 C212.18017,164.220408 219.598146,163.995918 228.162535,163.995918 L246.055591,163.995918 L246.055591,195.514286 C246.055591,197.736735 246.752431,199.510204 248.370899,201.059184 C250.214153,202.608163 252.079886,203.506122 254.372715,203.506122 C256.463236,203.506122 258.531277,202.608163 260.172223,201.059184 L326.102289,137.797959 C327.720757,136.24898 328.642384,134.47551 328.642384,132.253061 C328.642384,130.030612 327.720757,128.257143 326.102289,126.708163 L260.172223,63.4469388 C258.553756,61.8979592 256.463236,61 254.395194,61 C252.079886,61 250.236632,61.8979592 248.393377,63.4469388 C246.77491,64.9959184 246.07807,66.7693878 246.07807,68.9918367 L246.07807,100.510204 L228.162535,100.510204 C166.863084,100.510204 129.166282,117.167347 115.274437,150.459184 C110.666301,161.54898 108.350993,175.310204 108.350993,191.742857 C108.350993,205.279592 113.903236,223.912245 124.760454,247.438776 C125.00772,248.112245 125.457294,249.010204 126.154134,250.559184 Z" id="Shape" fill="#FFFFFF" transform="translate(218.496689, 160.000000) scale(-1, 1) translate(-218.496689, -160.000000) "></path>
            </g>
        </g>
        <!-- File -->
        <g id="file" stroke="#000" stroke-width="25" fill="#FFF" fill-rule="evenodd" stroke-linecap="round" stroke-linejoin="round">
            <path d="M13 24.12v274.76c0 6.16 5.87 11.12 13.17 11.12H239c7.3 0 13.17-4.96 13.17-11.12V136.15S132.6 13 128.37 13H26.17C18.87 13 13 17.96 13 24.12z"/>
            <path d="M129.37 13L129 113.9c0 10.58 7.26 19.1 16.27 19.1H249L129.37 13z"/>
        </g>
        <g id="file-shortcut" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
            <g id="file-shortcut-group" transform="translate(13.000000, 13.000000)">
                <g id="file-shortcut-shape" stroke="#000000" stroke-width="25" fill="#FFFFFF" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M0,11.1214886 L0,285.878477 C0,292.039924 5.87498876,296.999983 13.1728373,296.999983 L225.997983,296.999983 C233.295974,296.999983 239.17082,292.039942 239.17082,285.878477 L239.17082,123.145388 C239.17082,123.145388 119.58541,2.84217094e-14 115.369423,2.84217094e-14 L13.1728576,2.84217094e-14 C5.87500907,-1.71479982e-05 0,4.96022995 0,11.1214886 Z" id="rect1171"></path>
                    <path d="M116.37005,0 L116,100.904964 C116,111.483663 123.258008,120 132.273377,120 L236,120 L116.37005,0 L116.37005,0 Z" id="rect1794"></path>
                </g>
                <path d="M47.803141,294.093878 C48.4999811,295.177551 48.9495553,296.095918 49.4216083,296.995918 C50.1184484,297.895918 50.5680227,298.630612 51.2873415,299.365306 C52.2089688,300.44898 53.3778619,301 54.7490634,301 C56.1427436,301 57.0643709,300.632653 57.761211,299.916327 C58.4580511,299.365306 58.9076254,298.465306 58.9076254,297.381633 C58.9076254,296.830612 58.9076254,295.930612 58.6828382,294.828571 C58.4355724,293.561224 58.2107852,292.844898 58.2107852,292.477551 C57.7387323,287.757143 57.5139451,283.753061 57.5139451,279.95102 C57.5139451,273.228571 58.4355724,267.057143 59.8292526,261.602041 C61.44772,256.165306 63.5382403,251.610204 66.0783349,247.62449 C68.8656954,243.620408 72.3274172,240.35102 76.4859792,237.44898 C80.6445412,234.546939 85.2751561,232.177551 90.1305582,230.359184 C94.9859603,228.540816 100.76299,227.089796 107.236859,226.006122 C113.710728,225.087755 120.409385,224.371429 127.13052,223.820408 C133.829177,223.453061 141.247152,223.269388 149.811542,223.269388 L167.704598,223.269388 L167.704598,249.057143 C167.704598,250.87551 168.401438,252.326531 170.019905,253.593878 C171.86316,254.861224 173.728893,255.595918 176.021722,255.595918 C178.112242,255.595918 180.180284,254.861224 181.82123,253.593878 L247.751296,201.834694 C249.369763,200.567347 250.291391,199.116327 250.291391,197.297959 C250.291391,195.479592 249.369763,194.028571 247.751296,192.761224 L181.82123,141.002041 C180.202763,139.734694 178.112242,139 176.044201,139 C173.728893,139 171.885639,139.734694 170.042384,141.002041 C168.423917,142.269388 167.727077,143.720408 167.727077,145.538776 L167.727077,171.326531 L149.811542,171.326531 C88.5120908,171.326531 50.8152886,184.955102 36.9234437,212.193878 C32.3153075,221.267347 30,232.526531 30,245.971429 C30,257.046939 35.5522422,272.291837 46.4094607,291.540816 C46.6567266,292.091837 47.1063009,292.826531 47.803141,294.093878 Z" id="Shape-Copy" fill="#000000" fill-rule="nonzero" transform="translate(140.145695, 220.000000) scale(-1, 1) translate(-140.145695, -220.000000) "></path>
            </g>
        </g>
    </defs>
    </svg>
<header>
    <h1>"""  # noqa: E501
    html += title if is_root_dir else f"{title} / {path.name}"
    html += """</h1>
                 </header>
                 <main>
                 <div class="listing">
                     <table aria-describedby="summary">
                         <thead>
                         <tr>
                             <th></th>
                             <th>Name</th>
                             <th>Size</th>
                             <th class="hideable">
                                 Modified
                             </th>
                             <th class="hideable"></th>
                         </tr>
                         </thead>
                         <tbody>
                 """  # noqa: E501

    if not is_root_dir:
        html += f"""
        <tr class="clickable">
            <td></td>
            <td><a href="../{output_file.name}"><svg width="1.5em" height="1em" version="1.1" viewBox="0 0 24 24"><use xlink:href="#go-up"></use></svg>
            <span class="goup">..</span></a></td>
            <td>&mdash;</td>
            <td class="hideable">&mdash;</td>
            <td class="hideable"></td>
        </tr>
        """  # noqa: E501

    # sort dirs first
    sorted_entries = sorted(
        path.glob(filename_glob or "*"), key=lambda p: (p.is_file(), p.name)
    )

    for entry in sorted_entries:
        # don't include index.html in the file listing
        if entry.name.lower() == output_file.name.lower():
            continue

        if entry.is_dir():
            _make_dir_browsable(
                entry,
                output_file=entry / output_file.name,
                filename_glob=filename_glob,
                is_root_dir=False,
                title=title,
            )

        # From Python 3.6, os.access() accepts path-like objects
        if (not entry.is_symlink()) and not os.access(str(entry), os.W_OK):
            print(
                f"*** WARNING *** entry {entry.absolute()} is not writable! SKIPPING!"
            )
            continue

        size_bytes = -1  ## is a folder
        size_pretty = "&mdash;"
        last_modified = "-"
        last_modified_human_readable = "-"
        last_modified_iso = ""
        try:
            if entry.is_file():
                size_bytes = entry.stat().st_size
                size_pretty = humanize.naturalsize(size_bytes, binary=True)

            if entry.is_dir() or entry.is_file():
                last_modified = datetime.fromtimestamp(entry.stat().st_mtime).replace(
                    microsecond=0
                )
                last_modified_iso = last_modified.isoformat()
                last_modified_human_readable = last_modified.strftime("%c")

        except Exception as e:
            print("ERROR accessing file name:", e, entry)
            continue

        entry_path = str(entry.name)

        if entry.is_dir() and not entry.is_symlink():
            entry_type = "folder"
            if os.name not in ("nt",):
                # append explicit index page name to dirs
                entry_path = str(Path(entry.name) / output_file.name)

        elif entry.is_dir() and entry.is_symlink():
            entry_type = "folder-shortcut"

        elif entry.is_file() and entry.is_symlink():
            entry_type = "file-shortcut"

        else:
            entry_type = "file"

        html += f"""
        <tr class="file">
            <td></td>
            <td>
                <a href="{quote(entry_path)}">
                    <svg width="1.5em" height="1em" version="1.1" viewBox="0 0 265 323">
                        <use xlink:href="#{entry_type}"></use>
                    </svg>
                    <span class="name">{entry.name}</span>
                </a>
            </td>
            <td data-order="{size_bytes}">{size_pretty}</td>
            <td class="hideable">
                <time datetime="{last_modified_iso}">
                    {last_modified_human_readable}
                </time>
            </td>
            <td class="hideable"></td>
        </tr>
"""

    html += """
            </tbody>
        </table>
    </div>
</main>
</body>
</html>"""

    output_file.write_text(html, encoding="utf-8")


def _safe_name(
    name: str,
    *,
    replacement: str = "-",
    lower: bool = True,
    web_safe: bool = True,
    max_len: int = 255,
) -> str:
    if web_safe:
        safe = re.sub(r"[^a-zA-Z0-9\-_.]+", replacement, name)
    else:
        safe = "".join(char if char.isalpha() else " " for char in name)
        safe = re.sub(r" +", replacement, safe)
    safe = safe.strip(replacement)
    safe = safe[:max_len]
    return safe.lower() if lower else safe


async def _get_target_path(
    res: ResourceBaseDocument,
    *,
    base_path: Path,
    fmt: ResourceExportFormat,
    ext: str,
    structured: bool,
    web_safe: bool,
) -> Path:
    res_id_str = str(res.id)
    res_safe_name = _safe_name(
        pick_translation(res.title),
        web_safe=web_safe,
        max_len=200,
    )
    export_fname = f"{res_safe_name}_{res_id_str}_{fmt}.{ext}"
    if not structured:
        return base_path / export_fname
    else:
        text = ensure(await TextDocument.get(res.text_id))
        res_cat = next(
            (
                cat
                for cat in text.resource_categories
                if cat["key"] == res.config.general.category
            ),
            None,
        )
        if res_cat:
            res_cat = _safe_name(
                pick_translation(res_cat["translations"]), web_safe=web_safe
            )
        else:
            res_cat = "other"
        text_safe_name = _safe_name(text.title, web_safe=web_safe)
        return base_path / text_safe_name / res_cat / export_fname


async def run(
    resource_ids: list[PydanticObjectId] | None,
    *,
    formats: list[ResourceExportFormat],
    out_dir: Path,
    delete: bool = False,
    archive: int | None = None,
    structured: bool = True,
    web_safe: bool = False,
    browsable: bool = False,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    if not out_dir.is_dir():
        click.echo(f"Output directory {out_dir} is not a directory.", err=True)
        exit(1)
    await db.init_odm()

    # handle archiving
    if archive is not None:
        archive_ts_fmt = "%Y-%m-%d_%H-%M-%S"
        archive_dir = out_dir / "_archive"
        old_export_files = [
            f
            for f in out_dir.iterdir()
            if not (f.is_dir() and f.name == archive_dir.name)
        ]

        ts_str = datetime.now().strftime(archive_ts_fmt)
        pf = await get_state()
        pf_name = _safe_name(pf.platform_name, web_safe=True)
        zip_prefix = f"{pf_name}_exports_"
        zip_ext = ".zip"
        zip_path = archive_dir / f"{zip_prefix}{ts_str}{zip_ext}"

        # archive existing files
        if old_export_files:
            click.echo(f"Archiving existing files in {out_dir} ...")
            archive_dir.mkdir(parents=True, exist_ok=True)
            # create zip archive of everything in "existing" list
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for f in old_export_files:
                    if f.is_file() and f.name != "index.html":
                        zipf.write(f, arcname=f.name)
                        f.unlink()
                    elif f.is_dir():
                        for root, _dirs, files in os.walk(f):
                            for file in files:
                                if file == "index.html":
                                    continue
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, out_dir)
                                zipf.write(file_path, arcname=arcname)
                        shutil.rmtree(f)
        else:
            click.echo("No existing files to archive.")

        # delete old archives
        if archive > 0 and archive_dir.exists():
            for f in archive_dir.iterdir():
                if f.is_file() and f.suffix == zip_ext:
                    ts_str = f.name[len(zip_prefix) : -len(zip_ext)]
                    ts = datetime.strptime(ts_str, archive_ts_fmt)
                    if (datetime.now() - ts).days > archive:
                        f.unlink()

    if delete and archive is None:
        click.echo(f"Deleting old export data in {out_dir} ...")
        for child in out_dir.iterdir():
            if child.is_file():
                child.unlink()
            elif child.is_dir():
                shutil.rmtree(child)

    await resources.call_resource_precompute_hooks()

    # determine target resource IDs
    target_resources: list[ResourceBaseDocument] = await ResourceBaseDocument.find(
        Eq(ResourceBaseDocument.public, True),
        In(ResourceBaseDocument.id, resource_ids) if resource_ids else {},
        with_children=True,
    ).to_list()

    # give feedback on resources that could not be found
    for res in resource_ids or []:
        if res not in [res.id for res in target_resources]:
            click.echo(f"Resource ID {res} not found or not public", err=True)

    # run exports
    if not target_resources:
        click.echo("No resources to export", err=True)
        exit(1)
    cfg = get_config()
    for res in target_resources:
        res_id_str = str(res.id)
        for fmt in formats:
            click.echo(f"Exporting resource {res_id_str} as {fmt} ...")
            try:
                export_props = await export_resource_contents_task(
                    user=None,
                    cfg=cfg,
                    resource_id=cast(PydanticObjectId, res.id),
                    export_format=fmt,
                )
            except TekstHTTPException as e:
                if "unsupportedExportFormat" in str(e.detail):
                    click.echo(
                        f"Resource {res_id_str} does not support export format {fmt}",
                        err=True,
                    )
                    continue
                else:
                    raise

            # move exported file to output directory
            source_path = cfg.temp_files_dir / export_props["artifact"]
            ext = res_exp_fmt_info[fmt]["extension"]
            target_path = await _get_target_path(
                res,
                base_path=out_dir,
                fmt=fmt,
                ext=ext,
                structured=structured,
                web_safe=web_safe or browsable,
            )
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(source_path, target_path)
            os.remove(source_path)
            click.echo(f"Exported resource {res_id_str} as {str(target_path)}.")

    if browsable:
        pf = await get_state()
        _make_dir_browsable(
            out_dir,
            output_file=out_dir / "index.html",
            title=f"{pf.platform_name} Exports",
            filename_glob="*",
        )

    await db.close()

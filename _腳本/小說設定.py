"""Novel configuration — single source of truth for novel_id ↔ folder mapping.
All scripts should import from here instead of hardcoding folder names."""

NOVELS = {
    "infinite_livestream": {
        "folder": "無限直播間",
        "title_cn": "无限直播间",
        "title_tw": "無限直播間",
    },
}

# Build lookup: any known name → actual folder name
_ALIASES = {}
for _id, info in NOVELS.items():
    _ALIASES[_id] = info["folder"]
    _ALIASES[info["title_cn"]] = info["folder"]
    _ALIASES[info["title_tw"]] = info["folder"]
    _ALIASES[info["folder"]] = info["folder"]

def resolve_novel_folder(novel_key: str) -> str:
    """Return actual folder name for any key (ID, CN title, TW title, or folder)."""
    return _ALIASES.get(novel_key, novel_key)

def add_novel_arg(parser):
    """Add --novel argument with hint about available IDs."""
    ids = ", ".join(NOVELS.keys())
    parser.add_argument("--novel", required=True,
                       help=f"小说 ID 或名称（可用 ID: {ids}）")

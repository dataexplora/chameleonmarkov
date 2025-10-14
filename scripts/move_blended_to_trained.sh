#!/usr/bin/env bash
set -euo pipefail

# move_blended_to_trained.sh
# Safe utility to move all files from blended_idioms/ to trained_idioms/
# Usage:
#   ./move_blended_to_trained.sh --dry-run      # show what would change
#   ./move_blended_to_trained.sh                # perform the move
#   ./move_blended_to_trained.sh --help         # show help

SRC_DIR="/root/docker-apps/chameleonmarkov/blended_idioms"
DST_DIR="/root/docker-apps/chameleonmarkov/trained_idioms"
RSYNC_OPTS=("-a" "--info=progress2")
DRY_RUN=true

print_help() {
  cat <<EOF
move_blended_to_trained.sh

Moves files from:
  $SRC_DIR
into:
  $DST_DIR

By default the script runs in --dry-run mode. Use no flags to actually move files.
Options:
  --dry-run     show actions (default)
  --run         perform the move
  --force       perform the move and overwrite existing files if any
  --help        show this help

Examples:
  ${0} --dry-run
  ${0} --run
EOF
}

if [ "$#" -gt 0 ]; then
  case "$1" in
    --help|-h)
      print_help
      exit 0
      ;;
    --dry-run)
      DRY_RUN=true
      ;;
    --run)
      DRY_RUN=false
      ;;
    --force)
      DRY_RUN=false
      RSYNC_OPTS+=("--inplace")
      ;;
    *)
      echo "Unknown option: $1"
      print_help
      exit 2
      ;;
  esac
fi

# sanity checks
if [ ! -d "$SRC_DIR" ]; then
  echo "Source directory does not exist: $SRC_DIR"
  exit 1
fi

if [ ! -d "$DST_DIR" ]; then
  echo "Destination directory does not exist. Creating: $DST_DIR"
  if [ "$DRY_RUN" = false ]; then
    mkdir -p "$DST_DIR"
  fi
fi

count_files() {
  local dir="$1"
  find "$dir" -maxdepth 1 -type f | wc -l
}

size_human() {
  du -sh "$1" 2>/dev/null || true
}

echo "Source: $SRC_DIR"
echo "Destination: $DST_DIR"
echo "Source files before: $(count_files "$SRC_DIR")"
echo "Destination files before: $(count_files "$DST_DIR")"
echo "Source size: $(size_human "$SRC_DIR")"
echo "Destination size: $(size_human "$DST_DIR")"

echo
if [ "$DRY_RUN" = true ]; then
  echo "DRY RUN: showing rsync command that WOULD run"
  printf 'rsync %s "%s/" "%s/" --remove-source-files\n' "${RSYNC_OPTS[*]}" "$SRC_DIR" "$DST_DIR"
  echo
  echo "To perform the move, re-run with --run"
  exit 0
fi

# perform move with rsync (preserve attributes), then clean empty files/dirs
echo "Running rsync to move files..."
rsync "${RSYNC_OPTS[@]}" --remove-source-files "$SRC_DIR/" "$DST_DIR/"

# remove any zero-length leftover files
find "$SRC_DIR" -type f -empty -delete || true
# remove empty directories in source
find "$SRC_DIR" -type d -empty -not -path "$SRC_DIR" -delete || true

echo "Move complete. Post-move counts:"
echo "Source files after: $(count_files "$SRC_DIR")"
echo "Destination files after: $(count_files "$DST_DIR")"
echo "Destination size: $(size_human "$DST_DIR")"

echo "Done."

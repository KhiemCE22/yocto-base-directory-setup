#!/usr/bin/env bash
set -euo pipefail

SEED=/opt/seed/yocto-ppe-workspace
DEST=/home/yocto/ws/yocto-ppe-workspace   # điểm mount volume

# Nếu DEST chưa có gì (trống), mới seed
if [ ! -d "$DEST" ] || [ -z "$(find "$DEST" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]; then
  echo "[seed] Copy seed -> $DEST"
  mkdir -p "$DEST"
  rsync -a --delete "$SEED"/ "$DEST"/
  echo "[seed] Done."
else
  echo "[seed] $DEST already has content; skipping."
fi
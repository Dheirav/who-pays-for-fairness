#!/bin/bash
# Progress for an operating-point sweep: arms done of total, elapsed, and an ETA derived
# from the measured completion rate -- never guessed up front.
#
#   scripts/sweep_progress.sh <results-stem> <point> [<point> ...]
#   scripts/sweep_progress.sh --watch <results-stem> <point> [<point> ...]
#
# e.g. scripts/sweep_progress.sh hmda_tx_2021_race_manufactured 045 055 065 075 085 092
#
# Exists because the 2026-09-08 TX sweep crashed the WSL VM and its scratchpad progress
# reader died with it; a reader for a job that gets relaunched belongs in the repo.
R="$(dirname "$0")/../research/results"
WATCH=0; [ "$1" = "--watch" ] && { WATCH=1; shift; }
STEM="$1"; shift
POINTS=("$@")
STATE="/tmp/sweep_progress_${STEM}.start"
[ -f "$STATE" ] || date +%s > "$STATE"

show() {
  local done_n=0
  for p in "${POINTS[@]}"; do
    [ -f "$R/${STEM}_levelling_up_op${p}/levelling_up_runs.csv" ] && done_n=$((done_n+1))
  done
  local start now el
  start=$(cat "$STATE"); now=$(date +%s); el=$((now-start))
  if [ "$done_n" -gt 0 ] && [ "$done_n" -lt "${#POINTS[@]}" ]; then
    local eta=$(( el * (${#POINTS[@]} - done_n) / done_n ))
    printf "%s: %d/%d arms  elapsed %dm%02ds  ETA ~%dm%02ds (from measured rate)\n" \
      "$STEM" "$done_n" "${#POINTS[@]}" $((el/60)) $((el%60)) $((eta/60)) $((eta%60))
  elif [ "$done_n" -eq "${#POINTS[@]}" ]; then
    printf "%s: %d/%d arms  DONE in %dm%02ds\n" "$STEM" "$done_n" "${#POINTS[@]}" $((el/60)) $((el%60))
  else
    printf "%s: 0/%d arms  elapsed %dm%02ds  (no completions yet -- no ETA)\n" \
      "$STEM" "${#POINTS[@]}" $((el/60)) $((el%60))
  fi
}
if [ "$WATCH" = 1 ]; then
  while true; do show; sleep 20; done
else
  show
fi

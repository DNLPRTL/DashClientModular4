#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pprint import pprint

from core.parser.dash import DashParser


def main() -> int:
    arg_parser = argparse.ArgumentParser(description="Manual MPD parser inspection helper.")
    arg_parser.add_argument("mpd_url", help="MPD URL or local MPD path to inspect.")
    args = arg_parser.parse_args()

    parser = DashParser()
    parser.load(args.mpd_url)

    info = parser.get_mpd_info()
    periods = parser.get_periods()
    if not periods:
        print("No Period elements found in the MPD.")
        return 1

    print("=== MPD INFO ===")
    pprint(info)
    print()

    for p_idx, period in enumerate(periods):
        print(f"=== Period #{p_idx} id={period.get('id', '')} dur={period.get('duration', '')} ===")
        adap_sets = period.get("adaptationSets", [])
        if not adap_sets:
            print("  (No AdaptationSet elements)")
            continue

        for a_idx, adap in enumerate(adap_sets):
            print(
                f"  -- AdaptationSet #{a_idx} type={adap.get('type', '')} "
                f"mime={adap.get('mimeType', '')} lang={adap.get('lang', '')}"
            )
            reps = adap.get("representations", [])
            if not reps:
                print("     (No Representation elements)")
                continue

            for r_idx, rep in enumerate(reps):
                segs = rep.get("segments", []) or []
                frag = rep.get("fragment_duration") or 0.0
                init_url = rep.get("init_url") or ""
                has_init = bool(init_url)
                total_items = len(segs) + (1 if has_init else 0)

                last_name = segs[-1].split("/")[-1] if segs else "N/A"
                first_name = segs[0].split("/")[-1] if segs else "N/A"

                print(
                    f"    [Rep #{r_idx}] id={rep.get('id', '')} bw={rep.get('bandwidth', 0)} "
                    f"{rep.get('width', '')}x{rep.get('height', '')}"
                )
                print(f"       init={'YES' if has_init else 'no'} | frag_dur={frag:.6f}s")
                print(f"       media_segments={len(segs)} | total_items_with_init={total_items}")
                print(f"       first={first_name} | last={last_name}")

    print("\nOK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from pprint import pprint
from dash import DashParser

# 🔹 PON AQUÍ TU URL O RUTA LOCAL DEL MPD
MPD_URL = "http://172.16.0.251/dash/2/6sec/walk_simple_6s.mpd"


def main():
    parser = DashParser()
    parser.load(MPD_URL)

    info = parser.get_mpd_info()
    periods = parser.get_periods()
    if not periods:
        print("⚠️ No se encontraron Periods en el MPD.")
        return

    print("=== MPD INFO ===")
    pprint(info)
    print()

    for p_idx, period in enumerate(periods):
        print(f"=== Period #{p_idx} id={period.get('id','')} dur={period.get('duration','')} ===")
        adap_sets = period.get("adaptationSets", [])
        if not adap_sets:
            print("  (Sin AdaptationSets)")
            continue

        for a_idx, adap in enumerate(adap_sets):
            print(f"  -- AdaptationSet #{a_idx} type={adap.get('type','')} mime={adap.get('mimeType','')} lang={adap.get('lang','')}")
            reps = adap.get("representations", [])
            if not reps:
                print("     (Sin Representations)")
                continue

            for r_idx, rep in enumerate(reps):
                segs = rep.get("segments", []) or []
                frag = rep.get("fragment_duration") or 0.0
                init_url = rep.get("init_url") or ""
                has_init = bool(init_url)
                total_items = len(segs) + (1 if has_init else 0)

                last_name = segs[-1].split("/")[-1] if segs else "N/A"
                first_name = segs[0].split("/")[-1] if segs else "N/A"

                print(f"    [Rep #{r_idx}] id={rep.get('id','')} bw={rep.get('bandwidth',0)} "
                      f"{rep.get('width','')}x{rep.get('height','')}")
                print(f"       init={'YES' if has_init else 'no'} | frag_dur={frag:.6f}s")
                print(f"       medias reales={len(segs)} | items totales(incl INIT)={total_items}")
                print(f"       first={first_name} | last={last_name}")

    print("\nOK.")


if __name__ == "__main__":
    main()

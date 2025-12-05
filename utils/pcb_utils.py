import re
import numpy as np

def get_lines(filename):
    # === Datei einlesen ===
    with open(filename, "r", encoding="utf-8") as f:
        data = f.read()

    # === Alle Leitersegmente finden ===
    # Beispiel: (segment (start 10.16 20.32) (end 30.48 20.32) (width 0.25) (layer "F.Cu") ...)
    pattern = r"\(segment\s+\(start ([\d\.\-]+) ([\d\.\-]+)\)\s+\(end ([\d\.\-]+) ([\d\.\-]+)\)\s+\(width ([\d\.]+)\)\s+\(layer \"([^\"]+)\"\)"
    segments = re.findall(pattern, data)

    print(f"{len(segments)} Leiterzüge gefunden.")

    return segments

def get_fiducials(filename):
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()

    # --- Alle Footprints finden ---
    # Ein footprint-Block beginnt mit "(footprint" und endet mit ")"
    footprint_pattern = r"\(footprint\s+\"([^\"]+)\"(.*?)\)\s*\)"
    footprints = re.findall(footprint_pattern, text, flags=re.DOTALL)

    fiducials = []

    for fp_name, fp_body in footprints:
        # Prüfen, ob es ein Fiducial ist
        if "fiducial" in fp_name.lower():
            # Position extrahieren: (at x y [angle])
            at_match = re.search(r"\(at\s+([\d\.\-]+)\s+([\d\.\-]+)", fp_body)
            layer_match = re.search(r'\(layer\s+"([^"]+)"\)', fp_body)

            if at_match:
                x = float(at_match.group(1))
                y = float(at_match.group(2))
                layer = layer_match.group(1) if layer_match else "unknown"

                fiducials.append(np.array([x,y]))

    return fiducials


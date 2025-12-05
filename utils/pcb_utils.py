import re
import matplotlib.pyplot as plt

# === Pfad zur KiCad-PCB-Datei anpassen ===
filename = "board.kicad_pcb"

# === Datei einlesen ===
with open(filename, "r", encoding="utf-8") as f:
    data = f.read()

# === Alle Leitersegmente finden ===
# Beispiel: (segment (start 10.16 20.32) (end 30.48 20.32) (width 0.25) (layer "F.Cu") ...)
pattern = r"\(segment\s+\(start ([\d\.\-]+) ([\d\.\-]+)\)\s+\(end ([\d\.\-]+) ([\d\.\-]+)\)\s+\(width ([\d\.]+)\)\s+\(layer \"([^\"]+)\"\)"
segments = re.findall(pattern, data)

print(f"{len(segments)} Leiterzüge gefunden.")

# === Plot vorbereiten ===
fig, ax = plt.subplots()
ax.set_aspect("equal", adjustable="box")
ax.set_title("Leiterzüge aus KiCad-Datei")
ax.set_xlabel("x [mm]")
ax.set_ylabel("y [mm]")

# === Farben pro Layer definieren ===
layer_colors = {
    "F.Cu": "red",
    "B.Cu": "blue",
    "In1.Cu": "green",
    "In2.Cu": "orange"
}

# === Alle Segmente plotten ===
for seg in segments:
    x1, y1, x2, y2, width, layer = seg
    x1, y1, x2, y2, width = map(float, [x1, y1, x2, y2, width])
    color = layer_colors.get(layer, "gray")
    ax.plot([x1, x2], [y1, y2], color=color, linewidth=width*5, alpha=0.8)  # width*5 für bessere Sichtbarkeit

# === Plot anpassen ===
ax.invert_yaxis()  # KiCad hat invertierte Y-Achse
plt.tight_layout()
plt.show()

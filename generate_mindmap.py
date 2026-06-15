"""
Carte mentale du projet Mobile Money CI
Genere un PNG avec matplotlib
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'data', 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

fig, ax = plt.subplots(figsize=(20, 14))
ax.set_xlim(0, 20)
ax.set_ylim(0, 14)
ax.axis('off')

# Couleurs
C_BG = '#F8F9FA'
C_CENTRE = '#1A237E'
C_CM = '#1565C0'
C_TD = '#2E7D32'
C_DATA = '#E65100'
C_OUTILS = '#6A1B9A'
C_LIVRABLES = '#C62828'
C_BLANC = '#FFFFFF'
C_BLEU_CLAIR = '#E3F2FD'
C_VERT_CLAIR = '#E8F5E9'
C_ORANGE_CLAIR = '#FFF3E0'

fig.patch.set_facecolor(C_BG)

def draw_box(ax, x, y, w, h, color, text, text_color='white', fontsize=10, alpha=0.9):
    rect = mpatches.FancyBboxPatch(
        (x-w/2, y-h/2), w, h,
        boxstyle="round,pad=0.15",
        facecolor=color, edgecolor='none', alpha=alpha, zorder=3
    )
    ax.add_patch(rect)
    ax.text(x, y, text, ha='center', va='center', fontsize=fontsize,
            fontweight='bold', color=text_color, zorder=4)

def draw_arrow(ax, x1, y1, x2, y2, color='#666666', lw=1.5):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw, alpha=0.6), zorder=2)

def draw_circle(ax, x, y, r, color, text, text_color='white', fontsize=8):
    circle = plt.Circle((x, y), r, color=color, alpha=0.9, zorder=3)
    ax.add_patch(circle)
    ax.text(x, y, text, ha='center', va='center', fontsize=fontsize,
            fontweight='bold', color=text_color, zorder=4)

# ─── NOEUD CENTRAL ────────────────────────────────────────────
draw_box(ax, 10, 12.5, 5, 0.7, C_CENTRE,
         "PROJET MOBILE MONEY CI\nPipeline ETL + Schéma en étoile", fontsize=13)

# ─── BRANCHE 1 : CM (cours) ───────────────────────────────────
draw_box(ax, 2, 10, 3.2, 0.5, C_CM, "CM — Cours Magistraux", fontsize=10)
draw_arrow(ax, 10, 12.15, 2, 10.25, C_CM)

cms = [
    (2, 8.8, "CM1\nÉcosystème\nAfrique/CI"),
    (2, 7.3, "CM2\nCollecte\nIngestion"),
    (2, 5.8, "CM3\nTransformation\nQualité"),
    (2, 4.3, "CM4\nOrchestration\nCarrière"),
]
for x, y, txt in cms:
    draw_circle(ax, x, y, 0.65, C_CM, txt, fontsize=7)
    draw_arrow(ax, 2, 9.75, x, y+0.7, C_CM)

# ─── BRANCHE 2 : TD (pratique) ────────────────────────────────
draw_box(ax, 10, 10, 3.5, 0.5, C_TD, "TD — Travaux Dirigés", fontsize=10)
draw_arrow(ax, 10, 12.15, 10, 10.25, C_TD)

tds = [
    (10, 8.8, "TD1\nExploration\nPandas"),
    (10, 7.3, "TD2\nPipeline\nETL"),
    (10, 5.8, "TD3\nModélisation\nSchéma étoile"),
    (10, 4.3, "TD4\nOrchestration\nAirflow/Docker"),
]
for x, y, txt in tds:
    draw_circle(ax, x, y, 0.65, C_TD, txt, fontsize=7)
    draw_arrow(ax, 10, 9.75, x, y+0.7, C_TD)

# ─── BRANCHE 3 : Données ──────────────────────────────────────
draw_box(ax, 18, 10, 3, 0.5, C_DATA, "Données", fontsize=10)
draw_arrow(ax, 10, 12.15, 18, 10.25, C_DATA)

datas = [
    (18, 8.3, "Source\nCSV"),
    (18, 6.8, "100 000\nlignes"),
    (18, 5.3, "12\ncolonnes"),
    (18, 3.8, "4\nopérateurs"),
]
for x, y, txt in datas:
    draw_circle(ax, x, y, 0.55, C_DATA, txt, fontsize=7)
    draw_arrow(ax, 18, 9.75, x, y+0.6, C_DATA)

# ─── BRANCHE 4 : Outils ───────────────────────────────────────
draw_box(ax, 18, 12, 3.2, 0.5, C_OUTILS, "Stack Technique", fontsize=10)
draw_arrow(ax, 10, 12.15, 18, 12.25, C_OUTILS)

outils = [
    (16.5, 1.8, "Python\nPandas"),
    (18, 1.8, "Supabase\nPostgreSQL"),
    (19.5, 1.8, "Airflow"),
    (16.5, 0.5, "Docker"),
    (18, 0.5, "dbt"),
    (19.5, 0.5, "GitHub\nActions"),
]
for x, y, txt in outils:
    draw_circle(ax, x, y, 0.5, C_OUTILS, txt, fontsize=6.5)

# ─── BRANCHE 5 : Livrables ────────────────────────────────────
draw_box(ax, 2, 12, 3.2, 0.5, C_LIVRABLES, "Livrables", fontsize=10)
draw_arrow(ax, 10, 12.15, 2, 12.25, C_LIVRABLES)

livrables = [
    (3.5, 1.8, "Notebook\nJupyter"),
    (5, 1.8, "Rapport\nPDF"),
    (6.5, 1.8, "Dashboard\nPNG"),
    (3.5, 0.5, "DAG\nAirflow"),
    (5, 0.5, "Docker\nCompose"),
    (6.5, 0.5, "GitHub\nRepo"),
]
for x, y, txt in livrables:
    draw_circle(ax, x, y, 0.5, C_LIVRABLES, txt, fontsize=6.5)

# ─── ÉTAPES DU PROJET (en bas) ───────────────────────────────
etapes_y = 1.8
etapes_x_start = 9.5
etapes = [
    "1. Prépa", "2. ETL", "3. Supabase", "4. Schéma",
    "5. SQL", "6. Dashboard", "7. Airflow", "8. Docker",
    "9. dbt", "10. Rapport"
]
for i, e in enumerate(etapes):
    draw_circle(ax, etapes_x_start + i*1.05, etapes_y, 0.45,
                C_OUTILS if i < 8 else C_LIVRABLES, e, fontsize=6.5)
    if i < len(etapes)-1:
        draw_arrow(ax, etapes_x_start + i*1.05 + 0.45, etapes_y,
                   etapes_x_start + (i+1)*1.05 - 0.45, etapes_y, '#999999', 1)

# ─── TITRE ─────────────────────────────────────────────────────
ax.text(10, 13.6, "Carte mentale du projet - Mobile Money Côte d'Ivoire",
        ha='center', va='center', fontsize=16, fontweight='bold', color=C_CENTRE)
ax.text(10, 13.1, "Notre trinôme — Data Engineering 2025",
        ha='center', va='center', fontsize=10, color='#666666')

# ─── LÉGENDE ──────────────────────────────────────────────────
legende_y = 0.3
legende_items = [
    (0.5, legende_y, C_CM, "CM"),
    (1.3, legende_y, C_TD, "TD"),
    (2.1, legende_y, C_DATA, "Données"),
    (2.9, legende_y, C_OUTILS, "Outils"),
    (3.7, legende_y, C_LIVRABLES, "Livrables"),
]
for x, y, c, t in legende_items:
    rect = mpatches.FancyBboxPatch((x, y-0.12), 0.5, 0.24, boxstyle="round,pad=0.05",
                                    facecolor=c, edgecolor='none', alpha=0.9, zorder=3)
    ax.add_patch(rect)
    ax.text(x+0.55, y, t, va='center', fontsize=8, color='#333333', zorder=4)

# ─── SAUVEGARDE ───────────────────────────────────────────────
output_path = os.path.join(OUTPUT_DIR, 'carte_mentale_projet.png')
plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor=C_BG)
plt.close()
print(f'Carte mentale créée : {output_path}')

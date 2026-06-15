"""
Tableau de bord Mobile Money CI — 5 graphiques
Genere un PNG professionnel pour le rapport
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import os
import warnings
warnings.filterwarnings('ignore')

CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                        'TD', 'Data2_transactions_mobile_money_100k.csv')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'data', 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams.update({
    'figure.facecolor': '#F8F9FA',
    'axes.facecolor': '#FFFFFF',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'font.family': 'DejaVu Sans',
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.titleweight': 'bold',
})

PALETTE = {
    'MTN CI': '#FFCC00',
    'Orange Money': '#FF6600',
    'Moov Africa': '#009900',
    'Wave': '#1A73E8',
}
BLEUS = ['#1565C0', '#1976D2', '#42A5F5', '#90CAF9', '#BBDEFB', '#E3F2FD']

df = pd.read_csv(CSV_PATH, encoding='utf-8', low_memory=False)
df['date_heure'] = pd.to_datetime(df['date_heure'])
df = df.replace('', np.nan)
df['frais_fcfa'] = df['frais_fcfa'].fillna(0).astype(int)
df['zone_beneficiaire'] = df['zone_beneficiaire'].fillna('Zone inconnue')
df = df[df['montant_fcfa'] > 0].copy()
df['heure'] = df['date_heure'].dt.hour
df['mois'] = df['date_heure'].dt.strftime('%Y-%m')
df_s = df[df['statut'] == 'Succès'].copy()

fig = plt.figure(figsize=(16, 20))
fig.suptitle('Tableau de bord Mobile Money - Cote d Ivoire 2024',
             fontsize=18, fontweight='bold', y=0.98)

# Graphique 1 : Volume mensuel par operateur (barres empilees)
ax1 = fig.add_subplot(3, 2, 1)
pivot = df_s.groupby(['mois', 'operateur'])['montant_fcfa'].sum().unstack(fill_value=0) / 1e9
bottom = np.zeros(len(pivot))
for op, color in PALETTE.items():
    if op in pivot.columns:
        ax1.bar(pivot.index, pivot[op], bottom=bottom, label=op, color=color, alpha=0.85)
        bottom += pivot[op].values
ax1.set_title('Volume mensuel par operateur')
ax1.set_ylabel('Milliards FCFA')
ax1.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{x:.1f}B'))
ax1.legend(fontsize=8, loc='upper right')
ax1.tick_params(axis='x', rotation=30)

# Graphique 2 : Parts de marche
ax2 = fig.add_subplot(3, 2, 2)
parts = df_s.groupby('operateur')['montant_fcfa'].sum()
colors = [PALETTE.get(op, '#999999') for op in parts.index]
wedges, texts, autotexts = ax2.pie(
    parts.values, labels=parts.index, autopct='%1.1f%%',
    colors=colors, explode=[0.04]*len(parts), startangle=90)
for t in autotexts: t.set_fontsize(8)
ax2.set_title('Parts de marche par volume')

# Graphique 3 : Volume horaire
ax3 = fig.add_subplot(3, 2, 3)
vol_heure = df_s.groupby('heure')['montant_fcfa'].sum() / 1e6
ax3.fill_between(vol_heure.index, vol_heure.values, alpha=0.3, color='#1565C0')
ax3.plot(vol_heure.index, vol_heure.values, color='#1565C0', linewidth=2.5, marker='o', markersize=5)
ax3.axvspan(6, 9, alpha=0.1, color='green', label='Matin')
ax3.axvspan(17, 20, alpha=0.1, color='orange', label='Soir')
ax3.set_title('Volume par tranche horaire')
ax3.set_xlabel('Heure'); ax3.set_ylabel('Millions FCFA')
ax3.set_xticks(range(0, 24, 2))
ax3.legend(fontsize=8)

# Graphique 4 : Taux de succes par operateur
ax4 = fig.add_subplot(3, 2, 4)
taux_s = df.groupby('operateur').apply(lambda g: (g['statut'] == 'Succès').mean()*100).sort_values(ascending=True)
colors_s = [PALETTE.get(op, '#999999') for op in taux_s.index]
bars = ax4.barh(taux_s.index, taux_s.values, color=colors_s, alpha=0.85)
for bar, val in zip(bars, taux_s.values):
    ax4.text(val-2, bar.get_y()+bar.get_height()/2, f'{val:.1f}%',
             va='center', ha='right', color='white', fontweight='bold', fontsize=9)
ax4.set_title('Taux de succes par operateur')
ax4.set_xlabel('%'); ax4.set_xlim(0, 100)
ax4.axvline(taux_s.mean(), color='red', linestyle='--', linewidth=1.5, label='Moyenne')
ax4.legend(fontsize=8)

# Graphique 5 : Distribution montants par categorie (violin)
ax5 = fig.add_subplot(3, 2, (5, 6))
def cat(m):
    if m <= 5000: return 'Micro (<=5k)'
    elif m <= 50000: return 'Petit (5k-50k)'
    elif m <= 200000: return 'Moyen (50k-200k)'
    else: return 'Gros (>200k)'
df_s['categorie'] = df_s['montant_fcfa'].apply(cat)
ordre = ['Micro (<=5k)', 'Petit (5k-50k)', 'Moyen (50k-200k)', 'Gros (>200k)']
donnees_cat = [
    df_s[df_s['categorie'] == c]['montant_fcfa'].sample(
        min(1000, len(df_s[df_s['categorie'] == c]))).values
    for c in ordre
]
parts_nb = df_s['categorie'].value_counts().reindex(ordre).fillna(0)
vp = ax5.violinplot(donnees_cat, positions=range(len(ordre)), widths=0.6, showmedians=True)
for i, pc in enumerate(vp['bodies']):
    pc.set_facecolor(BLEUS[i]); pc.set_alpha(0.7)
for i, (c, nb) in enumerate(zip(ordre, parts_nb.values)):
    ax5.text(i, df_s['montant_fcfa'].max()*0.92, f'n={int(nb):,}',
             ha='center', fontsize=8, color=BLEUS[i])
ax5.set_title('Distribution des montants par categorie')
ax5.set_ylabel('Montant FCFA')
ax5.set_xticks(range(len(ordre)))
ax5.set_xticklabels(ordre, fontsize=9)
ax5.set_yscale('log')

plt.tight_layout(rect=[0, 0, 1, 0.96])
output_path = os.path.join(OUTPUT_DIR, 'dashboard_mobile_money.png')
plt.savefig(output_path, dpi=180, bbox_inches='tight', facecolor='#F8F9FA')
plt.close()
print(f'Dashboard sauvegarde : {output_path}')

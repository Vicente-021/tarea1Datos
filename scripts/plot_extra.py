#!/usr/bin/env python3
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 10, 'axes.titlesize': 12, 'legend.fontsize': 8,
                     'lines.linewidth': 1.6, 'grid.alpha': 0.35})

WIDTHS = (256, 1024, 4096)
CMAP_CMS = {256: '#fdd0a2', 1024: '#fd8d3c', 4096: '#a63603'}
CMAP_CS = {256: '#c6dbef', 1024: '#6baed6', 4096: '#08519c'}
TH = 1000


def cargar(key):
    ex = pd.read_csv(f'resultados/exact_many_{key}.csv')
    sk = {w: pd.read_csv(f'resultados/sk_many_{key}_w{w}.csv') for w in WIDTHS}
    for w in WIDTHS:
        sk[w] = sk[w].merge(ex[['win', 'key', 'exact_f']], on=['win', 'key'])
    return ex, sk


def fig_scatter():
    fig, axes = plt.subplots(1, 2, figsize=(11, 5), sharey=True)
    for ax, (name, col) in zip(axes, (('CMS', 'cms_f'), ('CS', 'cs_f'))):
        for w in WIDTHS:
            x = []
            y = []
            for key in ('src', 'dst'):
                _, sk = cargar(key)
                d = sk[w]
                m = d.exact_f > 0
                x.append(d.exact_f[m])
                y.append(d[col][m])
            x = pd.concat(x)
            y = pd.concat(y)
            ax.scatter(x, y, s=6, alpha=0.45, color=CMAP_CMS[w] if name == 'CMS' else CMAP_CS[w],
                       label=f'w={w}', rasterized=True)
        lim = (1e0, 2e7)
        ax.set_xscale('log'); ax.set_yscale('log')
        ax.plot(lim, lim, 'k--', lw=1.2, label='y = x', zorder=0)
        ax.set_xlim(lim); ax.set_ylim(lim)
        ax.set_xlabel('Frecuencia exacta $f_j(x)$')
        ax.set_title(name)
        ax.grid(True, which='both')
        ax.legend(loc='upper left')
    axes[0].set_ylabel('Frecuencia estimada $\\hat{f}_j(x)$')
    fig.suptitle('Estimado vs. exacto (19 claves por tipo, 84 ventanas; log-log)', fontweight='bold')
    fig.tight_layout()
    out = 'resultados/figuras/fig_scatter_est_exact.png'
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print('Generado:', out)


def fig_hist():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
    for ax, (name, col) in zip(axes, (('CMS', 'cms_f'), ('CS', 'cs_f'))):
        for w in WIDTHS:
            re = []
            for key in ('src', 'dst'):
                _, sk = cargar(key)
                d = sk[w]
                m = d.exact_f >= TH
                re.append(((d[col][m] - d.exact_f[m]) / d.exact_f[m]).to_numpy())
            re = np.concatenate(re)
            ax.hist(re, bins=60, range=(-0.5, 1.5), alpha=0.5, color=CMAP_CMS[w] if name == 'CMS' else CMAP_CS[w],
                    label=f'w={w}')
        ax.axvline(0, color='k', lw=1.0)
        ax.set_xlabel(r'Error relativo $(\hat{f}_j(x)-f_j(x))/f_j(x)$')
        ax.set_title(name)
        ax.set_ylim(0, ax.get_ylim()[1])
        ax.grid(True)
        ax.legend(loc='upper right')
    axes[0].set_ylabel('Frecuencia de observaciones')
    fig.suptitle(f'Distribucion del error relativo (ventanas con $f_j(x)\\geq {TH}$)', fontweight='bold')
    fig.tight_layout()
    out = 'resultados/figuras/fig_error_hist.png'
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print('Generado:', out)


def fig_frontera():
    df = pd.read_csv('resultados/resumen_ataques.csv')
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
    for ax, atk in zip(axes, ('ddos', 'scan')):
        d = df[df.ataque == atk]
        for name, color in (('CMS', '#d62728'), ('CS', '#1f77b4')):
            s = d[d.sketch == name]
            ax.plot(s.mem_B / 1024, s.MRE_pct, 'o-', color=color, label=name)
        ax.set_title(atk.upper())
        ax.set_xscale('log'); ax.set_yscale('log')
        ax.set_xlabel('Memoria de contadores (KiB)')
        ax.grid(True, which='both')
        ax.legend(loc='upper right')
    axes[0].set_ylabel('MRE durante el ataque (%)')
    fig.suptitle('Compromiso precision-memoria (d = 5)', fontweight='bold')
    fig.tight_layout()
    out = 'resultados/figuras/fig_frontera_mre_mem.png'
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print('Generado:', out)


if __name__ == '__main__':
    fig_scatter()
    fig_hist()
    fig_frontera()
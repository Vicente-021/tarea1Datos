#!/usr/bin/env python3
# plot_ataques.py -- Figuras de la Actividad 2 y 6.3 (una figura por ataque).
# Uso (desde tarea1Datos):  python3 plot_ataques.py
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 10, 'axes.titlesize': 12, 'legend.fontsize': 8,
                     'lines.linewidth': 1.4, 'grid.alpha': 0.35})

WIDTHS = (256, 1024, 4096)
CMS_COL = {256: '#e41a1c', 1024: '#ff7f00', 4096: '#f0c000'}   # tonos calidos
CS_COL = {256: '#08519c', 1024: '#3182bd', 4096: '#6baed6'}    # tonos frios
ATAQUES = {
    'ddos': dict(gt='resultados/gt_ddos.json', exact='resultados/exact_ddos.csv',
                 sk='resultados/sk_ddos_w{w}.csv',
                 titulo='DDoS (frecuencia por IP de destino)'),
    'scan': dict(gt='resultados/gt_scan.json', exact='resultados/exact_scan.csv',
                 sk='resultados/sk_scan_w{w}.csv',
                 titulo='Scan (frecuencia por IP de origen)'),
}


def cargar(cfg):
    with open(cfg['gt'], encoding='utf-8') as fh:
        a0, a1 = json.load(fh)['ventana_ataque_rel_s']
    lo, hi = a0 - 60, a1 + 60                       # rango pedido por la tarea
    ex = pd.read_csv(cfg['exact'])
    ex = ex[(ex.t_rel_s >= lo) & (ex.t_rel_s <= hi)]
    sk = {}
    for w in WIDTHS:
        d = pd.read_csv(cfg['sk'].format(w=w))
        sk[w] = d[(d.t_rel_s >= lo) & (d.t_rel_s <= hi)]
    return a0, a1, ex, sk


def marcar_ataque(ax, a0, a1):
    ax.axvspan(a0, a1, color='gray', alpha=0.15, label='ataque')
    ax.axvline(a0, color='gray', lw=0.8)
    ax.axvline(a1, color='gray', lw=0.8)


def fig_frecuencia(nombre, cfg):
    a0, a1, ex, sk = cargar(cfg)
    fig, ax = plt.subplots(figsize=(10, 6))
    marcar_ataque(ax, a0, a1)
    ax.plot(ex.t_rel_s, ex.exact_f, color='black', ls='--', lw=2.2,
            marker='o', ms=4, label='Exacto', zorder=10)
    ax.step(ex.t_rel_s, ex.threshold, where='post', color='gray', ls=':',
            lw=1.5, label=r'umbral $T_j=\lceil\phi N_j\rceil$')
    for w in WIDTHS:
        ax.plot(sk[w].t_rel_s, sk[w].cms_f, color=CMS_COL[w], marker='s', ms=3,
                label=f'CMS w={w}')
    for w in WIDTHS:
        ax.plot(sk[w].t_rel_s, sk[w].cs_f, color=CS_COL[w], marker='^', ms=3,
                label=f'CS w={w}')
    ax.set_yscale('symlog', linthresh=100)          # cubre desde ~10 hasta ~3e5
    ax.set_xlabel('Tiempo desde el primer paquete (s)')
    ax.set_ylabel(r'Frecuencia $f_j(x)$ (escala symlog)')
    ax.set_title(f'{nombre.upper()}: frecuencia exacta vs estimada - {cfg["titulo"]}')
    ax.grid(True)
    ax.legend(ncol=2, loc='upper left')
    fig.tight_layout()
    out = f'resultados/figuras/fig_{nombre}_frecuencia.png'
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print('Generado:', out)


def fig_delta(nombre, cfg):
    a0, a1, ex, sk = cargar(cfg)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), sharey=True)
    for ax, w in zip(axes, WIDTHS):
        marcar_ataque(ax, a0, a1)
        ax.plot(ex.t_rel_s, ex.exact_delta, color='black', ls='--', lw=2,
                marker='o', ms=4, label=r'$\Delta f_j(x)$ exacto', zorder=10)
        ax.plot(sk[w].t_rel_s, sk[w].cs_delta, color=CS_COL[1024], marker='^',
                ms=4, label='CountSketch')
        ax.plot(sk[w].t_rel_s, sk[w].cms_med_delta, color=CMS_COL[256], marker='s',
                ms=4, label='CMS-mediana')
        ax.axhline(0, color='k', lw=0.6)
        ax.set_yscale('symlog', linthresh=1000)
        ax.set_title(f'w = {w}')
        ax.set_xlabel('Tiempo desde el primer paquete (s)')
        ax.grid(True)
    axes[0].set_ylabel(r'$\Delta f_j(x)$ (escala symlog)')
    axes[0].legend(loc='upper left')
    fig.suptitle(f'{nombre.upper()}: cambio de frecuencia - {cfg["titulo"]}',
                 fontweight='bold')
    fig.tight_layout()
    out = f'resultados/figuras/fig_{nombre}_delta.png'
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print('Generado:', out)


def main():
    for nombre, cfg in ATAQUES.items():
        fig_frecuencia(nombre, cfg)
        fig_delta(nombre, cfg)


if __name__ == '__main__':
    main()
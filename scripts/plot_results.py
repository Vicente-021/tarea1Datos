import os
import pandas as pd
import matplotlib.pyplot as plt

# Configuración visual para informes académicos
plt.rcParams.update({
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.titlesize': 13,
    'lines.linewidth': 1.5,
    'grid.alpha': 0.4
})

WIDTHS = [256, 1024, 4096]
COLORS_CMS = {256: '#e41a1c', 1024: '#377eb8', 4096: '#4daf4a'}
COLORS_CS  = {256: '#ff7f00', 1024: '#984ea3', 4096: '#a65628'}

def load_data(key_type):
    """Carga los datos exactos y los resultados para cada w."""
    exact_file = f'resultados/exact_{key_type}.csv'
    if not os.path.exists(exact_file):
        raise FileNotFoundError(f"No se encontró el archivo exacto: {exact_file}")
    
    df_exact = pd.read_csv(exact_file)
    # Calcular cambio exacto de frecuencia Δf_j = f_j - f_{j-1}
    df_exact['exact_delta'] = df_exact['exact_f'].diff()

    sk_data = {}
    for w in WIDTHS:
        sk_file = f'resultados/sk_{key_type}_w{w}.csv'
        if os.path.exists(sk_file):
            sk_data[w] = pd.read_csv(sk_file)
        else:
            print(f"Advertencia: {sk_file} no existe. Se omitirá en los gráficos.")
            
    return df_exact, sk_data

def plot_frequency(key_type, title, filename):
    """Genera las Figuras 1 y 2 (Frecuencia en el tiempo)."""
    df_exact, sk_data = load_data(key_type)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    
    # Curva exacta en ambos subplots
    ax1.plot(df_exact['t_rel_s'], df_exact['exact_f'], color='black', linestyle='--', linewidth=2, label='Exacto', zorder=5)
    ax2.plot(df_exact['t_rel_s'], df_exact['exact_f'], color='black', linestyle='--', linewidth=2, label='Exacto', zorder=5)

    for w, df_sk in sk_data.items():
        ax1.plot(df_sk['t_rel_s'], df_sk['cms_f'], color=COLORS_CMS[w], label=f'CMS (w={w})')
        ax2.plot(df_sk['t_rel_s'], df_sk['cs_f'], color=COLORS_CS[w], label=f'CS (w={w})')

    ax1.set_title('Count-Min Sketch (CMS) vs Exacto')
    ax1.set_ylabel('Frecuencia Estimada $f_j(x)$')
    ax1.grid(True)
    ax1.legend(loc='upper left')

    ax2.set_title('CountSketch (CS) vs Exacto')
    ax2.set_xlabel('Tiempo relativo (s)')
    ax2.set_ylabel('Frecuencia Estimada $f_j(x)$')
    ax2.grid(True)
    ax2.legend(loc='upper left')

    fig.suptitle(f'Figura: Estimación de Frecuencia Temporal - {title}', fontweight='bold')
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"Generado: {filename}")

def plot_delta(key_type, title, filename, target_w=1024):
    """Genera las Figuras 3 y 4 (Cambio de frecuencia Δf_j)."""
    df_exact, sk_data = load_data(key_type)
    
    if target_w not in sk_data:
        print(f"No se puede generar {filename}: falta la traza con w={target_w}")
        return

    df_sk = sk_data[target_w]

    fig, ax = plt.subplots(figsize=(10, 5))

    # Curva exacta de diferencia
    ax.plot(df_exact['t_rel_s'], df_exact['exact_delta'], color='black', linestyle='--', linewidth=2, label=r'$\Delta f_j(x)$ Exacto', zorder=5)
    
    # CMS-Mediana vs CS para el ancho objetivo (ej. w=1024)
    if 'cms_med_delta' in df_sk.columns:
        ax.plot(df_sk['t_rel_s'], df_sk['cms_med_delta'], color='#e41a1c', label=f'CMS-mediana ($\Delta f_j$, w={target_w})')
    if 'cs_delta' in df_sk.columns:
        ax.plot(df_sk['t_rel_s'], df_sk['cs_delta'], color='#377eb8', label=f'CountSketch ($\Delta f_j$, w={target_w})')

    ax.set_title(f'Figura: Cambio de Frecuencia $\Delta f_j(x)$ - {title} (w={target_w})', fontweight='bold')
    ax.set_xlabel('Tiempo relativo (s)')
    ax.set_ylabel('Diferencia de Frecuencia $\Delta f_j(x)$')
    ax.grid(True)
    ax.legend(loc='upper left')

    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"Generado: {filename}")

def main():
    # Requisitos previos de instalación: pandas, matplotlib
    print("Generando gráficos para el informe...")
    
    # Figura 1: Frecuencia DDoS (IP víctima)
    plot_frequency('dst', 'Ataque DDoS (IP Víctima)', 'resultados/figuras/fig1_ddos_frecuencia.png')
    
    # Figura 2: Frecuencia Scan (IP atacante)
    plot_frequency('src', 'Ataque Scan (IP Atacante)', 'resultados/figuras/fig2_scan_frecuencia.png')
    
    # Figura 3: Cambio de Frecuencia Δf_j para DDoS
    plot_delta('dst', 'Ataque DDoS (IP Víctima)', 'resultados/figuras/fig3_ddos_delta.png', target_w=1024)
    
    # Figura 4: Cambio de Frecuencia Δf_j para Scan
    plot_delta('src', 'Ataque Scan (IP Atacante)', 'resultados/figuras/fig4_scan_delta.png', target_w=1024)

if __name__ == '__main__':
    main()
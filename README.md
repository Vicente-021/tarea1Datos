# Tarea 1 2026 — Count-Min Sketch y CountSketch en ventanas deslizantes

Tópicos en Grandes Volúmenes de Datos. Implementación de **Count-Min Sketch (CMS)** y
**CountSketch (CS)** sobre una ventana deslizante de `W = 60 s` (paso `p = 10 s`,
`m = W/p = 6` subventanas) usando la **linealidad** de los sketches para mantener la
ventana con costo independiente del número de paquetes que permanecen en ella.

Se usan para detectar dos ataques sintéticos sobre una traza real de backbone
(MAWI, samplepoint-F):

- **DDoS**: frecuencia por IP de **destino** (clave: `ataque.victima`).
- **Scan**: frecuencia por IP de **origen** (clave: `ataque.atacante`).

Una clave es *heavy hitter* en la ventana `j` si `f_j(x) >= ⌈φ·N_j⌉`, con `φ = 0.01`.

---

## Estructura

```
sketch_detect.cpp            Programa principal: CMS y CS con ventana deslizante
main.tex                     Informe (≤ 6 páginas)
codigo_entregado/            Herramientas entregadas (pcap2bin, exact_hh, inject_attack.py)
scripts/
  analisis_validacion.py     Act. 1: errores de estimación (abs/rel) y memoria
  analisis_ataques.py        Act. 2 y 6.3: MRE, latencia, FP/FN, Δf_j
  plot_ataques.py            Figuras overlay (una por ataque) para el informe
  plot_extra.py              Figuras nuevas: scatter, histograma de error, frontera MRE-memoria
  plot_results.py            Variante de figuras (opcional)
datos/                       Trazas locales (NO se suben; ver .gitignore)
resultados/
  gt_ddos.json, gt_scan.json   Ground truth de los ataques inyectados
  exact_*.csv                  Ground truth exacto por ventana (exact_hh)
  sk_*.csv                     Estimaciones de los sketches por ventana
  verify_n_*.csv               Verificación del anillo de contadores (N_j)
  validacion.csv               Tabla de validación de la Act. 1
  resumen_ataques.csv          Tabla resumen: error, memoria y latencia
  error_ventanas_ataques.csv   Error por ventana en las ventanas del ataque
  deltas_ataques.csv           Mayores Δf_j (incrementos/decrementos) y estimaciones
  rank_*.csv, stats_*.txt      Caracterización de la traza
  figuras/                     Figuras del informe (PNG)
```

## Reproducibilidad

- **Traza**: MAWI samplepoint-F, 3 de diciembre de 2018, 14:00 (JST).
  `https://mawi.wide.ad.jp/mawi/samplepoint-F/2018/201812031400.pcap.gz`
- **Ataques**: semilla `42` (por defecto de `inject_attack.py`), intervalo `[300, 330] s`.

### 0. Preparación

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # numpy, pandas, matplotlib

make -C codigo_entregado/codigo_entregado          # pcap2bin, exact_hh
g++ -O2 -march=native -std=c++17 -Wall -Wextra -o sketch_detect sketch_detect.cpp
```

### 1. Datos

```bash
curl -L -C - -O https://mawi.wide.ad.jp/mawi/samplepoint-F/2018/201812031400.pcap.gz
mv 201812031400.pcap.gz datos/
zcat datos/201812031400.pcap.gz | ./codigo_entregado/codigo_entregado/pcap2bin > datos/traza.bin
```

### 2. Caracterización de la traza

```bash
./codigo_entregado/codigo_entregado/exact_hh datos/traza.bin --stats --key src | tee resultados/stats_src.txt
./codigo_entregado/codigo_entregado/exact_hh datos/traza.bin --stats --key dst | tee resultados/stats_dst.txt
```

### 3. Actividad 1 — validación contra el conteo exacto

Verificación obligatoria del anillo (`N_j` debe coincidir exactamente con `exact_hh`):

```bash
./sketch_detect datos/traza.bin --key src -W 60 --delta 10 --phi 0.01 -d 5 -w 1024 \
    --verify-n resultados/verify_n_src.csv
./codigo_entregado/codigo_entregado/exact_hh datos/traza.bin --key src -W 60 --delta 10 --phi 0.01 \
    --out-windows resultados/exact_win_src.csv
# comparar las columnas N de ambos archivos (debe ser idéntica ventana por ventana)
```

Consultas de un conjunto de claves (top src/dst) y estimación con `w ∈ {256, 1024, 4096}`:

```bash
./codigo_entregado/codigo_entregado/exact_hh datos/traza.bin --key src -W 60 --delta 10 --phi 0.01 \
    --query 203.83.117.211 --query 203.83.101.148 --query 31.141.14.54 --query 202.12.82.146 \
    --out-query resultados/exact_src.csv
./sketch_detect datos/traza.bin --key src -W 60 --delta 10 --phi 0.01 -d 5 -w 256 \
    --query 203.83.117.211 --query 203.83.101.148 --query 31.141.14.54 --query 202.12.82.146 \
    --out-query resultados/sk_src_w256.csv
# repetir para w = 1024 y 4096, y para --key dst con sus claves
python3 scripts/analisis_validacion.py > resultados/validacion.csv
```

### 4. Actividad 2 — ataques sintéticos

```bash
python3 codigo_entregado/codigo_entregado/inject_attack.py ddos --base datos/traza.bin \
    --out datos/traza_ddos.bin --gt resultados/gt_ddos.json \
    --start 300 --duration 30 --pps 10000 --sources 4000
python3 codigo_entregado/codigo_entregado/inject_attack.py scan --base datos/traza.bin \
    --out datos/traza_scan.bin --gt resultados/gt_scan.json \
    --start 300 --duration 30 --pps 8000 --dst-count 60000

# ground truth exacto (clave desde el JSON: 163.210.30.13 y 198.18.0.7)
./codigo_entregado/codigo_entregado/exact_hh datos/traza_ddos.bin --key dst -W 60 --delta 10 --phi 0.01 \
    --query 163.210.30.13 --out-query resultados/exact_ddos.csv
./codigo_entregado/codigo_entregado/exact_hh datos/traza_scan.bin --key src -W 60 --delta 10 --phi 0.01 \
    --query 198.18.0.7 --out-query resultados/exact_scan.csv

# sketches sobre las trazas con ataque, para cada w en {256, 1024, 4096}
./sketch_detect datos/traza_ddos.bin --key dst -W 60 --delta 10 --phi 0.01 -d 5 -w 256 \
    --query 163.210.30.13 --out-query resultados/sk_ddos_w256.csv \
    --verify-n resultados/verify_n_ddos_w256.csv
./sketch_detect datos/traza_scan.bin --key src -W 60 --delta 10 --phi 0.01 -d 5 -w 256 \
    --query 198.18.0.7 --out-query resultados/sk_scan_w256.csv \
    --verify-n resultados/verify_n_scan_w256.csv

# análisis (MRE, latencia, FP/FN, Δf) y figuras
python3 scripts/analisis_ataques.py
python3 scripts/plot_ataques.py
python3 scripts/plot_extra.py        # figuras nuevas (scatter, histograma, frontera)
```

### 5. Resultados

Tabla resumen (`resumen_ataques.csv`), d = 5, φ = 0.01:

| ataque | w | sketch | mem | MRE (%) | latencia | vs exacto |
|---|---|---|---|---|---|---|
| ddos | 256 | CMS | 70 KB | 4.11 | 10 s | 0 |
| ddos | 256 | CS | 70 KB | 0.16 | 10 s | 0 |
| ddos | 4096 | CMS | 1.09 MB | 0.18 | 10 s | 0 |
| ddos | 4096 | CS | 1.09 MB | 0.02 | 10 s | 0 |
| scan | 256 | CMS | 70 KB | 3.78 | 10 s | −1 ventana (FP esperado) |
| scan | 256 | CS | 70 KB | 0.68 | 20 s | 0 |
| scan | 4096 | CMS | 1.09 MB | 0.09 | 20 s | 0 |
| scan | 4096 | CS | 1.09 MB | 0.02 | 20 s | 0 |

La memoria de contadores corresponde a `7 · d · w · 8 B` (6 sub-sketchs del anillo + agregado,
`int64`, por tipo de sketch).

## Notas

- Las trazas (`*.bin`, `*.pcap`, `*.pcap.gz`) **no** se suben al repositorio (ver `.gitignore`).
  Para reproducir, basta descargar la URL indicada y usar la semilla `42`.
- CMS sobreestima (estimador mínimo); CS es insesgado. El MRE de CS puede ser no monótono en `w`
  por ser una variable aleatoria de media cero; ver `error_ventanas_ataques.csv`.
- Para Δf, CS usa su estimador habitual (mediana con signo) sobre `ΔA_j = A_j − A_{j−1}`;
  CMS usa la variante experimental *CMS-mediana* (el mínimo no aplica a vectores firmados).
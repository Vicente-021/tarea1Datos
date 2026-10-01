# analisis_ataques.py -- Actividad 2 y 6.3: MRE, latencia, decisiones HH y delta f.
# Uso (desde tarea1Datos):  python3 analisis_ataques.py [--ventanas]
import csv, json, sys

W, P, D = 60.0, 10.0, 5
WIDTHS = (256, 1024, 4096)
ATAQUES = {
    'ddos': ('resultados/gt_ddos.json', 'resultados/exact_ddos.csv', 'resultados/sk_ddos_w{w}.csv'),
    'scan': ('resultados/gt_scan.json', 'resultados/exact_scan.csv', 'resultados/sk_scan_w{w}.csv'),
}
SKETCHES = (('CMS', 'cms_f', 'cms_hh', 'cms_med_delta'),
            ('CS',  'cs_f',  'cs_hh',  'cs_delta'))


def leer(path):
    with open(path, newline='', encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def ent(x):
    return int(x) if x != '' else None

def escribir(path, cab, filas):
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        wr = csv.writer(fh)
        wr.writerow(cab)
        for r in filas:
            wr.writerow(['' if x is None else (round(x, 2) if isinstance(x, float) else x)
                         for x in r])
    print('Generado:', path)

def primera(wins, cond):
    return next((j for j in wins if cond(j)), None)


def media(v):
    return sum(v) / len(v) if v else None


def linea(*c):
    print(','.join('' if x is None else (f'{x:.2f}' if isinstance(x, float) else str(x))
                   for x in c))


def main():
    detalle = '--ventanas' in sys.argv
    resumen, eventos, filas = [], [], []

    for nombre, (gt_p, ex_p, sk_p) in ATAQUES.items():
        with open(gt_p, encoding='utf-8') as fh:
            a0, a1 = json.load(fh)['ventana_ataque_rel_s']
        ex = {int(r['win']): r for r in leer(ex_p)}
        wins = sorted(ex)
        t = {j: float(ex[j]['t_rel_s']) for j in wins}
        f = {j: int(ex[j]['exact_f']) for j in wins}
        hh = {j: int(ex[j]['exact_hh']) for j in wins}
        dl = {j: ent(ex[j]['exact_delta']) for j in wins}

        # J: evaluaciones posteriores al inicio y anteriores a la salida del ultimo paquete
        J = [j for j in wins if t[j] > a0 and t[j] - W < a1 and f[j] > 0]
        zona = [j for j in wins if dl[j] is not None and a0 < t[j] <= a1 + W]
        con_d = [j for j in wins if dl[j] is not None]
        incr = sorted(con_d, key=lambda j: -dl[j])[:3]
        decr = sorted(con_d, key=lambda j: dl[j])[:3]
        jex = primera(wins, lambda j: hh[j] == 1)
        det_ex = 'sin deteccion' if jex is None else f't={t[jex]:.0f} s (latencia {t[jex]-a0:.0f} s)'
        print(f'# {nombre}: ataque [{a0:.0f}, {a1:.0f}] s | |J|={len(J)} '
              f'(t={t[J[0]]:.0f}..{t[J[-1]]:.0f} s) | exacto detecta en {det_ex}')

        for w in WIDTHS:
            sk = {int(r['win']): r for r in leer(sk_p.format(w=w))}
            faltan = sorted(set(wins) - set(sk))
            if faltan:
                sys.exit(f'{sk_p.format(w=w)}: faltan ventanas {faltan[:5]}')
            mem = 7 * D * w * 8   # 6 sub-sketches + agregado, int64, por tipo de sketch

            for sname, cf, chh, cd in SKETCHES:
                est = {j: int(sk[j][cf]) for j in wins}
                sh = {j: int(sk[j][chh]) for j in wins}
                dv = {j: ent(sk[j][cd]) for j in wins}

                mre = 100 * media([abs(est[j] - f[j]) / f[j] for j in J])
                mae = media([abs(est[j] - f[j]) for j in J])

                jd = primera(wins, lambda j: sh[j] == 1)
                lat = None if jd is None else t[jd] - a0
                dif = None if (jd is None or jex is None) else (t[jd] - t[jex]) / P
                fp = sum(1 for j in wins if sh[j] and not hh[j])
                fpp = sum(1 for j in wins if sh[j] and not hh[j] and t[j] <= a0)
                fn = sum(1 for j in wins if hh[j] and not sh[j])

                d_all = media([abs(dv[j] - dl[j]) for j in con_d])
                d_atk = media([abs(dv[j] - dl[j]) for j in zona])

                resumen.append((nombre, w, sname, mem, mre, mae, lat, dif,
                                fp, fpp, fn, d_all, d_atk))
                for j in J:
                    filas.append((nombre, w, sname, j, t[j], f[j], est[j],
                                  100 * (est[j] - f[j]) / f[j]))

            for tipo, lista in (('incremento', incr), ('decremento', decr)):
                for j in lista:
                    eventos.append((nombre, w, tipo, j, t[j], dl[j],
                                    ent(sk[j]['cs_delta']), ent(sk[j]['cms_med_delta'])))

    escribir('resultados/resumen_ataques.csv',
             ['ataque', 'w', 'sketch', 'mem_B', 'MRE_pct', 'MAE_J', 'latencia_s',
              'dif_vs_exacto_ventanas', 'FP', 'FP_previos', 'FN',
              'MAE_delta_todas', 'MAE_delta_ataque'], resumen)
    escribir('resultados/deltas_ataques.csv',
             ['ataque', 'w', 'tipo', 'win', 't_rel_s', 'exacto', 'CS', 'CMS_mediana',
              'errabs_CS', 'errabs_CMSmed'],
             [(a, w, tp, j, tt, e, cs, cm, abs(cs - e), abs(cm - e))
              for a, w, tp, j, tt, e, cs, cm in eventos])
    escribir('resultados/error_ventanas_ataques.csv',
             ['ataque', 'w', 'sketch', 'win', 't_rel_s', 'exacto', 'estimado',
              'err_rel_pct'], filas)


if __name__ == '__main__':
    main()
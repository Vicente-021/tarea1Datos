import csv, math, sys

def load(p):
    return list(csv.DictReader(open(p)))

def compute(exact_p, sk_p):
    ex = load(exact_p)
    sk = load(sk_p)
    ex_by = {(int(r['win']), r['key']): int(r['exact_f']) for r in ex}
    res = {'CMS': [], 'CS': []}
    for r in sk:
        fe = ex_by.get((int(r['win']), r['key']))
        if fe is None:
            continue
        for name, col in (('CMS', 'cms_f'), ('CS', 'cs_f')):
            fest = int(r[col])
            ae = abs(fest - fe)
            re = ae / fe if fe > 0 else None
            res[name].append((fe, ae, re))
    return res

def agg(res):
    rows = [x for x in res if x[2] is not None]
    mae = sum(x[1] for x in res) / len(res)
    mre = (sum(x[2] for x in rows) / len(rows)) if rows else float('nan')
    maxae = max(x[1] for x in res)
    return mae, mre, maxae

def main():
    keys = ('src', 'dst')
    widths = (256, 1024, 4096)
    out = sys.stdout
    out.write("key,w,sketch,MAE,MRE_pct,maxAE,mem_counters_B\n")
    for k in keys:
        for w in widths:
            res = compute(f'exact_{k}.csv', f'sk_{k}_w{w}.csv')
            mem = 7 * 5 * w * 8
            for name in ('CMS', 'CS'):
                mae, mre, maxae = agg(res[name])
                out.write(f"{k},{w},{name},{mae:.1f},{mre*100:.2f},{maxae:.0f},{mem}\n")

if __name__ == '__main__':
    main()
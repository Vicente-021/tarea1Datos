#include <algorithm>
#include <cmath>
#include <cinttypes>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

#pragma pack(push, 1)
struct Record {
    uint64_t ts_us;
    uint32_t src, dst;
    uint16_t sport, dport, len;
    uint8_t proto, flags;
};
#pragma pack(pop)
static_assert(sizeof(Record) == 24, "record debe ocupar 24 bytes");

enum KeyKind { K_SRC, K_DST };

static inline uint32_t make_key(const Record &r, KeyKind k) {
    return (k == K_SRC) ? r.src : r.dst;
}

static inline uint64_t splitmix64(uint64_t x) {
    x += 0x9E3779B97F4A7C15ull;
    x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ull;
    x = (x ^ (x >> 27)) * 0x94D049BB133111EBull;
    return x ^ (x >> 31);
}

static int h_pos(uint32_t key, int row, int w) {
    uint64_t h = splitmix64((uint64_t)key + 0x9E3779B97F4A7C15ull * (uint64_t)(row + 1));
    return (int)(h % (uint64_t)w);
}

static int s_sign(uint32_t key, int row) {
    uint64_t h = splitmix64((uint64_t)key + 0xBF58476D1CE4E5B9ull * (uint64_t)(row + 1));
    return (h & 1) ? 1 : -1;
}

struct Sketch {
    int d = 0, w = 0;
    std::vector<std::vector<int64_t>> C;

    void init(int d_, int w_) {
        d = d_;
        w = w_;
        C.assign(d, std::vector<int64_t>(w, 0));
    }

    void clear() {
        for (auto &row : C) std::fill(row.begin(), row.end(), 0);
    }

    int64_t *cell(int row, uint32_t key) { return &C[row][h_pos(key, row, w)]; }
    const int64_t *cell(int row, uint32_t key) const { return &C[row][h_pos(key, row, w)]; }

    void update(uint32_t key, bool sign) {
        for (int j = 0; j < d; ++j) {
            int64_t v = 1;
            if (sign) v *= s_sign(key, j);
            *cell(j, key) += v;
        }
    }

    void add(const Sketch &o) {
        for (int j = 0; j < d; ++j)
            for (int c = 0; c < w; ++c) C[j][c] += o.C[j][c];
    }

    void sub(const Sketch &o) {
        for (int j = 0; j < d; ++j)
            for (int c = 0; c < w; ++c) C[j][c] -= o.C[j][c];
    }

    int64_t est_min(uint32_t key) const {
        int64_t m = INT64_MAX;
        for (int j = 0; j < d; ++j) m = std::min(m, *cell(j, key));
        return m < 0 ? 0 : m;
    }

    int64_t est_med(uint32_t key, bool sign, bool clamp) const {
        std::vector<int64_t> v(d);
        for (int j = 0; j < d; ++j) {
            v[j] = *cell(j, key);
            if (sign) v[j] *= s_sign(key, j);
        }
        return median(v, clamp);
    }

    static int64_t median(std::vector<int64_t> &v, bool clamp) {
        std::sort(v.begin(), v.end());
        int64_t m = (v.size() % 2) ? v[v.size() / 2] : (v[v.size() / 2 - 1] + v[v.size() / 2]) / 2;
        if (clamp && m < 0) m = 0;
        return m;
    }
};

static bool parse_ipv4(const char *s, uint32_t *out) {
    unsigned a, b, c, d;
    if (sscanf(s, "%u.%u.%u.%u", &a, &b, &c, &d) != 4) return false;
    if (a > 255 || b > 255 || c > 255 || d > 255) return false;
    *out = (a << 24) | (b << 16) | (c << 8) | d;
    return true;
}

static void ip_to_string(uint32_t v, char *out) {
    sprintf(out, "%u.%u.%u.%u", v >> 24, (v >> 16) & 255, (v >> 8) & 255, v & 255);
}

struct Trace {
    const Record *r = nullptr;
    size_t n = 0;
    void *addr = nullptr;
    size_t bytes = 0;
};

static Trace map_trace(const char *path) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) { perror("open"); exit(1); }
    struct stat st;
    if (fstat(fd, &st) < 0) { perror("fstat"); exit(1); }
    if (st.st_size % (off_t)sizeof(Record)) {
        fprintf(stderr, "error: el tamano no es multiplo de 24 B\n");
        exit(1);
    }
    void *p = mmap(nullptr, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    if (p == MAP_FAILED) { perror("mmap"); exit(1); }
    close(fd);
    madvise(p, st.st_size, MADV_SEQUENTIAL);
    Trace t;
    t.addr = p;
    t.bytes = st.st_size;
    t.r = (const Record *)p;
    t.n = st.st_size / sizeof(Record);
    return t;
}

static void usage(const char *p) {
    fprintf(stderr,
        "uso: %s TRAZA.bin [opciones]\n"
        "  --key K              src (def) | dst\n"
        "  -d N                 filas del sketch (def. 5)\n"
        "  -w N                 ancho del sketch (def. 1024)\n"
        "  --cms | --cs | --both   que sketchs computar (def. --both)\n"
        "  -W SEGUNDOS          ancho de la ventana (def. 60)\n"
        "  --delta SEGUNDOS     paso de la ventana (def. 10)\n"
        "  --phi F              umbral de heavy hitter (def. 0.01)\n"
        "  --query IP           IP a consultar; puede repetirse\n"
        "  --out-query ARCH     CSV por ventana de las estimaciones\n"
        "  --verify-n ARCH      CSV de N_j del anillo (comparar con exact_hh)\n"
        "  --max-windows N      cortar tras N ventanas (def. sin limite)\n", p);
}

int main(int argc, char **argv) {
    if (argc < 2 || argv[1][0] == '-') { usage(argv[0]); return argc < 2 ? 2 : 0; }
    const char *path = argv[1];

    KeyKind kind = K_SRC;
    int d = 5, w = 1024;
    bool use_cms = true, use_cs = true;
    double W_s = 60.0, delta_s = 10.0, phi = 0.01;
    size_t max_windows = (size_t)-1;
    const char *o_query = nullptr, *o_verify = nullptr;
    std::vector<std::string> query_text;

    for (int i = 2; i < argc; ++i) {
        std::string a = argv[i];
        auto next = [&]() -> const char * {
            if (i + 1 >= argc) { fprintf(stderr, "falta valor para %s\n", a.c_str()); exit(2); }
            return argv[++i];
        };
        if (a == "--key") {
            std::string k = next();
            if (k == "src") kind = K_SRC;
            else if (k == "dst") kind = K_DST;
            else { fprintf(stderr, "clave desconocida: %s\n", k.c_str()); return 2; }
        }
        else if (a == "-d") d = atoi(next());
        else if (a == "-w") w = atoi(next());
        else if (a == "--cms") { use_cms = true; use_cs = false; }
        else if (a == "--cs") { use_cms = false; use_cs = true; }
        else if (a == "--both") { use_cms = true; use_cs = true; }
        else if (a == "-W") W_s = atof(next());
        else if (a == "--delta") delta_s = atof(next());
        else if (a == "--phi") phi = atof(next());
        else if (a == "--max-windows") max_windows = (size_t)atol(next());
        else if (a == "--query") query_text.emplace_back(next());
        else if (a == "--out-query") o_query = next();
        else if (a == "--verify-n") o_verify = next();
        else if (a == "-h" || a == "--help") { usage(argv[0]); return 0; }
        else { fprintf(stderr, "opcion no reconocida: %s\n", argv[i]); return 2; }
    }
    if (d < 1 || w < 1) { fprintf(stderr, "-d y -w deben ser >= 1\n"); return 2; }
    if (delta_s <= 0 || W_s <= 0) { fprintf(stderr, "-W y --delta deben ser positivos\n"); return 2; }
    if (phi <= 0.0 || phi > 1.0) { fprintf(stderr, "--phi debe estar en (0,1]\n"); return 2; }
    if (!query_text.empty() && !o_query) {
        fprintf(stderr, "--query requiere --out-query\n");
        return 2;
    }
    if (o_query && query_text.empty()) {
        fprintf(stderr, "--out-query requiere al menos un --query IP\n");
        return 2;
    }

    std::vector<uint32_t> queries;
    for (const std::string &q : query_text) {
        uint32_t ip = 0;
        if (!parse_ipv4(q.c_str(), &ip)) { fprintf(stderr, "IP invalida: %s\n", q.c_str()); return 2; }
        queries.push_back(ip);
    }

    const uint64_t W = (uint64_t)(W_s * 1e6);
    const uint64_t P = (uint64_t)(delta_s * 1e6);
    if (W % P != 0) { fprintf(stderr, "W debe ser multiplo de delta\n"); return 2; }
    const int m = (int)(W / P);
    if (m > 16) { fprintf(stderr, "m = W/delta demasiado grande\n"); return 2; }

    Trace t = map_trace(path);
    if (t.n == 0) return 1;
    const uint64_t t0 = t.r[0].ts_us;
    const uint64_t tend = t.r[t.n - 1].ts_us;

    Sketch ring_cms[16], ring_cs[16];
    Sketch A_cms, A_cs;
    if (use_cms) { for (int q = 0; q < m; ++q) ring_cms[q].init(d, w); A_cms.init(d, w); }
    if (use_cs) { for (int q = 0; q < m; ++q) ring_cs[q].init(d, w); A_cs.init(d, w); }
    uint64_t ncount[16] = {0};
    uint64_t N = 0;

    FILE *fq = o_query ? fopen(o_query, "w") : nullptr;
    FILE *fv = o_verify ? fopen(o_verify, "w") : nullptr;
    if (o_query && !fq) { perror("fopen out-query"); return 1; }
    if (o_verify && !fv) { perror("fopen verify-n"); return 1; }
    if (fq) {
        fprintf(fq, "win,tau_us,t_rel_s,key,N,threshold");
        if (use_cms) fprintf(fq, ",cms_f,cms_hh,cms_med_delta");
        if (use_cs) fprintf(fq, ",cs_f,cs_hh,cs_delta");
        fprintf(fq, "\n");
    }
    if (fv) fprintf(fv, "win,N\n");

    size_t i = 0;
    size_t win = 0;

    auto load_subwindow = [&](uint64_t q) {
        uint32_t slot = (uint32_t)((q - 1) % (uint64_t)m);
        uint64_t ts_lo = t0 + (q - 1) * P;
        uint64_t ts_hi = t0 + q * P;
        while (i < t.n && t.r[i].ts_us <= ts_hi) {
            if (t.r[i].ts_us <= ts_lo) { ++i; continue; }
            uint32_t key = make_key(t.r[i], kind);
            if (use_cms) { ring_cms[slot].update(key, false); A_cms.update(key, false); }
            if (use_cs) { ring_cs[slot].update(key, true); A_cs.update(key, true); }
            ncount[slot]++;
            N++;
            ++i;
        }
    };

    auto expire_subwindow = [&](uint64_t q) {
        uint32_t slot = (uint32_t)((q - 1) % (uint64_t)m);
        if (use_cms) A_cms.sub(ring_cms[slot]);
        if (use_cs) A_cs.sub(ring_cs[slot]);
        N -= ncount[slot];
        if (use_cms) ring_cms[slot].clear();
        if (use_cs) ring_cs[slot].clear();
        ncount[slot] = 0;
    };

    auto delta_cms_med = [&](uint32_t key, const Sketch &sexp_cms) {
        uint32_t slot = (uint32_t)((win - 1) % (uint64_t)m);
        std::vector<int64_t> v(d);
        for (int j = 0; j < d; ++j) v[j] = *ring_cms[slot].cell(j, key) - *sexp_cms.cell(j, key);
        return Sketch::median(v, false);
    };

    auto delta_cs = [&](uint32_t key, const Sketch &sexp_cs) {
        uint32_t slot = (uint32_t)((win - 1) % (uint64_t)m);
        std::vector<int64_t> v(d);
        for (int j = 0; j < d; ++j) {
            v[j] = *ring_cs[slot].cell(j, key) - *sexp_cs.cell(j, key);
            v[j] *= s_sign(key, j);
        }
        return Sketch::median(v, false);
    };

    auto evaluate = [&](uint64_t tau, bool have_delta, const Sketch &sexp_cms,
                        const Sketch &sexp_cs) {
        uint64_t thr = (uint64_t)std::ceil(phi * (double)N);
        if (thr == 0) thr = 1;
        if (fv) fprintf(fv, "%zu,%" PRIu64 "\n", win, N);
        if (fq) {
            for (uint32_t key : queries) {
                char ips[16];
                ip_to_string(key, ips);
                fprintf(fq, "%zu,%" PRIu64 ",%.6f,%s,%" PRIu64 ",%" PRIu64,
                        win, tau, (double)(tau - t0) / 1e6, ips, N, thr);
                if (use_cms) {
                    int64_t f = A_cms.est_min(key);
                    fprintf(fq, ",%" PRId64 ",%d", f, (f >= (int64_t)thr) ? 1 : 0);
                    if (have_delta) fprintf(fq, ",%" PRId64, delta_cms_med(key, sexp_cms));
                    else fprintf(fq, ",");
                }
                if (use_cs) {
                    int64_t f = A_cs.est_med(key, true, true);
                    fprintf(fq, ",%" PRId64 ",%d", f, (f >= (int64_t)thr) ? 1 : 0);
                    if (have_delta) fprintf(fq, ",%" PRId64, delta_cs(key, sexp_cs));
                    else fprintf(fq, ",");
                }
                fprintf(fq, "\n");
            }
        }
    };

    for (int q = 1; q <= m && t0 + (uint64_t)q * P <= tend; ++q) load_subwindow((uint64_t)q);

    uint64_t tau = t0 + W;
    Sketch zero_cms, zero_cs;
    if (use_cms) zero_cms.init(d, w);
    if (use_cs) zero_cs.init(d, w);
    if (tau <= tend) {
        evaluate(tau, false, zero_cms, zero_cs);
        ++win;
    }

    for (uint64_t q = (uint64_t)m + 1; q <= (uint64_t)((tend - t0) / P); ++q) {
        tau = t0 + q * P;
        if (tau > tend) break;
        if (win >= max_windows) break;
        uint32_t slot = (uint32_t)((q - 1) % (uint64_t)m);
        Sketch sexp_cms, sexp_cs;
        if (use_cms) { sexp_cms = ring_cms[slot]; }
        if (use_cs) { sexp_cs = ring_cs[slot]; }
        expire_subwindow(q - (uint64_t)m);
        load_subwindow(q);
        evaluate(tau, true, sexp_cms, sexp_cs);
        ++win;
    }

    if (fq) fclose(fq);
    if (fv) fclose(fv);
    munmap(t.addr, t.bytes);

    fprintf(stderr, "ventanas evaluadas : %zu\n", win);
    return 0;
}
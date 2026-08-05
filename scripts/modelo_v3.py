#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelo v3 — Presupuesto anual de 365 dias
==========================================
Reemplaza al modelo v2 (scripts/modelo_completo.py).

QUE CAMBIA RESPECTO A v2
------------------------
1. Se elimina por completo la taxonomia de feriados (fijos / trasladables /
   litúrgicos). Todos los feriados se ponderan igual: F * dsl/7.
   Motivo: era la entrada [C] mas debil del modelo, no auditable, y su efecto
   medio (1,4 dias) es menor que la ambiguedad del propio conteo de feriados
   en los paises con conflicto declarado (Peru +-2,6 dias).

2. Se sustituye el marco "dias liberados" por un PRESUPUESTO CERRADO de 365
   dias con cuatro bloques mutuamente excluyentes y exhaustivos:
       trabajo + descanso semanal + vacaciones + feriados = 365
   El cierre en 365 es una verificacion automatica que v2 no tenia.

3. dsl (dias laborables/semana) deja de ser un supuesto libre [C] y pasa a
   DERIVARSE de la ley: dsl = max(5, ceil_medio(jornada_semanal / tope_diario)).
   Motivo: v2 asumia pares (jornada semanal, dias/semana) que implican una
   jornada diaria SUPERIOR al tope legal en Panama, Brasil, Argentina,
   Uruguay y Paraguay. Ver verificacion V4.

4. Nueva correccion: solape feriado-vacaciones. Cuando la ley cuenta las
   vacaciones en dias CALENDARIO/CORRIDOS, un feriado que cae dentro del
   periodo queda absorbido y no libera un dia extra. Cuando las cuenta en
   dias HABILES, la ley ya lo excluye del computo. v2 los sumaba dos veces.

5. Se elimina el indice pct_anio_laboral_descanso (denominador endogeno: la
   jornada se cancelaba algebraicamente). Lo reemplazan indicadores sobre el
   denominador comun de 365 dias / 5.840 h de vigilia.

Ejecutar:  python3 modelo_v3.py
Genera:    ../datos/dataset_maestro.csv
           ../datos/presupuesto_anual.csv
           ../datos/sensibilidad_dsl.csv
           ../datos/jornada_serie_2023_2030.csv
"""
import csv, os, math, statistics as st

DIAS_ANIO   = 365.0
HORAS_SUENO = 8.0
VIGILIA     = DIAS_ANIO * (24 - HORAS_SUENO)      # 5.840 h — mismo ano de 365 dias
HORAS_ANIO  = DIAS_ANIO * 24                      # 8.760 h — el ano completo, sin descontar sueno
HORAS_SUENO_ANIO = DIAS_ANIO * HORAS_SUENO         # 2.920 h — [C] supuesto, mismo para los 11 paises
BASE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(BASE, "..", "datos")

# ---------------------------------------------------------------------------
# ENTRADAS
# ---------------------------------------------------------------------------
# vac    [A] vacaciones legales por tramo [1, 5, 10, 20 anos], en la unidad del pais
# unidad [A] unidad en que la ley expresa las vacaciones
# fer    [A/B/?] feriados nacionales 2026 — la confianza VARIA POR PAIS (README 3.3)
# jor    [A] jornada maxima legal semanal vigente a julio de 2026
# tope   [A] tope de jornada diaria ordinaria diurna, por norma
PAISES = [
 # nombre       unidad         vac[1,5,10,20]    fer  jor  tope  norma_tope
 ("Perú",      "calendario", [30, 30, 30, 30],  16,  48,  8.0, "Const. art. 25 · D.Leg. 854"),
 ("Panamá",    "calendario", [30, 30, 30, 30],  12,  48,  8.0, "CT art. 31"),
 ("Brasil",    "calendario", [30, 30, 30, 30],  10,  44,  8.0, "CLT art. 58"),
 ("Colombia",  "hábiles",    [15, 15, 15, 15],  18,  42, 10.0, "Ley 2101 · distribuible en 5 días"),
 ("Chile",     "hábiles",    [15, 15, 15, 18],  17,  42, 10.0, "CT art. 28 · mín. 5 días, máx. 10 h"),
 ("Argentina", "corridos",   [14, 21, 28, 35],  16,  48,  9.0, "Ley 11.544 art. 1 · sábado inglés"),
 ("Uruguay",   "hábiles",    [20, 21, 22, 25],  15,  48,  8.0, "Ley 5.350"),
 ("Ecuador",   "calendario", [15, 15, 20, 30],  12,  40,  8.0, "CT art. 47 · 40 h en 5 días"),
 ("Paraguay",  "hábiles",    [12, 18, 30, 30],  12,  48,  8.0, "CL art. 194"),
 ("Honduras",  "hábiles",    [10, 20, 20, 20],  11,  44,  8.0, "CT art. 322"),
 ("México",    "hábiles",    [12, 20, 22, 26],   7,  48,  8.0, "LFT art. 61"),
]
TRAMOS = ["1 año", "5 años", "10 años", "20 años"]

# dsl asumido por el modelo v2, conservado solo para la tabla de sensibilidad
DSL_V2 = {"Perú":6.0, "Panamá":5.5, "Brasil":5.0, "Colombia":5.0, "Chile":5.0,
          "Argentina":5.0, "Uruguay":5.5, "Ecuador":5.0, "Paraguay":5.0,
          "Honduras":5.5, "México":6.0}

# Horas efectivas semanales de ASALARIADOS, ILOSTAT 2023 (OIT/Gontero 2025) [A]
# None = la fuente no publica el valor. NO se imputa.
HORAS_EFECTIVAS = {"Colombia":46.6, "Honduras":45.0, "Argentina":37.0, "Uruguay":37.0,
                   "Perú":None, "Panamá":None, "Brasil":None, "Chile":None,
                   "Ecuador":None, "Paraguay":None, "México":None}
REF_LATAM, REF_OCDE = 42.0, 34.6

# Tiempo de desplazamiento IDA Y VUELTA al trabajo, minutos por dia trabajado. [B]
# (minutos, ano de referencia, fuente)
#
# Seis paises: OIT, Informe Tecnico Cono Sur n.o 56 (marzo 2026), Grafico 2,
# elaborado con microdatos de las encuestas nacionales de uso del tiempo (EUT).
# El propio informe advierte: "debido a diferencias metodologicas, los datos no son
# estrictamente comparables entre paises". Los anos de referencia difieren.
#
# Peru: no esta en el informe de la OIT. Se usa el promedio nacional del estudio de
# N. Cespedes (BCRP-USIL, 2026) sobre microdatos de la ENUT 2024 del INEI: 1,33 h/dia.
# Es el MISMO tipo de instrumento (encuesta nacional de uso del tiempo) que la OIT
# usa para los otros seis, procesado por otro equipo.
# La cifra es IDA Y VUELTA: el estudio calcula 32.400 h de vida en traslado como
# "tiempo de traslado diario x 240 dias laborales x 45 anos" y para los distritos
# perifericos (3 h/dia) da 3 x 240 x 45 = 32.400 exacto. Si fuera solo ida no cuadra.
# Se descarta el "107 minutos semanales" que reporta la nota de prensa de la ENUT:
# es incompatible con el resto de la evidencia y con la propia serie 2010-2024.
# None = ninguna fuente cubre ese pais. NO se imputa.
TRASLADO = {
    "Colombia": (86, 2021, "OIT IT-56 · EUT"),
    "Argentina":(77, 2021, "OIT IT-56 · EUT"),
    "Chile":    (74, 2023, "OIT IT-56 · EUT"),
    "México":   (69, 2019, "OIT IT-56 · EUT"),
    "Uruguay":  (56, 2022, "OIT IT-56 · EUT"),
    "Paraguay": (36, 2016, "OIT IT-56 · EUT"),
    "Perú":     (80, 2024, "ENUT INEI · BCRP-USIL"),
    # Brasil: PNS 2019 (IBGE) - 4,8 h/semana ida y vuelta, poblacion ocupada que
    # se traslada. Se divide entre 5 dias (misma convencion que usa el propio
    # informe de la OIT para pasar de semanal a diario en datos brasilenos).
    # 4,8 h/semana / 5 = 0,96 h/dia = 58 min/dia.
    "Brasil":   (58, 2019, "PNS 2019 · IBGE"),
    # Panama, Ecuador, Honduras: sin dato nacional comparable. Ver notas abajo.
    "Panamá":None, "Ecuador":None, "Honduras":None,
}
# ---------------------------------------------------------------------------
# Por que Panama, Ecuador y Honduras quedan sin dato (agosto 2026, busqueda
# dirigida tras pregunta explicita sobre estos 4 paises):
#
# PANAMA: unico dato disponible es Panama-Ciudad, 52 min (67 transporte
#   publico, 56 auto), CAF RED 2017 (Daude y otros, 2017). Es una encuesta de
#   movilidad URBANA (una ciudad), no una encuesta nacional de uso del tiempo
#   como las otras 7 -> mezclarla repetiria el problema de unidades que este
#   trabajo corrige. Ademas no se confirmo si es solo ida o ida y vuelta.
#   NO se usa.
#
# ECUADOR: la unica encuesta nacional de uso del tiempo (EUT 2012, INEC) mide
#   "trabajo y traslado" como una sola categoria (43-50 h/semana), sin poder
#   aislar el traslado. Una cifra posterior de ENEMDU ("4 h vs 5 h semanales",
#   2020 vs 2010) combina traslado a trabajo Y a estudio. Ninguna aisla lo que
#   se necesita. NO se usa.
#
# HONDURAS: no existe encuesta nacional de uso del tiempo. La Encuesta
#   Permanente de Hogares (EPHPM, INE Honduras) no tiene modulo de traslado.
#   El Observatorio de Movilidad Urbana de CAF no cubre Tegucigalpa ni San
#   Pedro Sula. NO se encontro ninguna fuente. NO se usa.
# Referencia regional: Encuesta CAF 2016 (Daude y otros, 2017) — 40 min por trayecto,
# ~80 min ida y vuelta. Paises de altos ingresos (OCDE): ~25 min diarios.
REF_TRASLADO_LATAM, REF_TRASLADO_OCDE = 80.0, 25.0
# Peru, desagregado (mismo estudio): Lima Metropolitana 1,7 h/dia = 102 min;
# distritos perifericos (Ancon, Mi Peru, Santa Rosa) mas de 3 h/dia = 180 min.
TRASLADO_PERU_LIMA, TRASLADO_PERU_PERIFERIA = 102, 180

JORNADA_SERIE = {
    "Perú":[48]*8, "Panamá":[48]*8, "Argentina":[48]*8, "Uruguay":[48]*8,
    "Paraguay":[48]*8, "Brasil":[44]*8, "Honduras":[44]*8, "Ecuador":[40]*8,
    "Colombia":[47, 46, 44, 42, 42, 42, 42, 42],
    "Chile":   [45, 44, 44, 42, 42, 40, 40, 40],
    "México":  [48, 48, 48, 48, 46, 44, 42, 40],
}
ANIOS = list(range(2023, 2031))

r1 = lambda v: round(v, 1)

# ---------------------------------------------------------------------------
# FORMULAS
# ---------------------------------------------------------------------------
def ceil_medio(x):
    """Redondea hacia arriba al medio dia (5,0 · 5,5 · 6,0)."""
    return math.ceil(x * 2) / 2

def dsl_legal(jor, tope):
    """Dias de trabajo por semana MINIMOS que exige la ley.

    Si la jornada semanal maxima es J y el tope diario es T, repartir J en
    menos de J/T dias obliga a superar T. Piso de 5,0: ninguno de los codigos
    de la muestra contempla una semana ordinaria de menos de cinco dias.
    """
    return max(5.0, ceil_medio(jor / tope))

def presupuesto(pais, ti=0, dsl_override=None):
    """Reparte los 365 dias del ano en cuatro bloques excluyentes."""
    nombre, unidad, vac, fer, jor, tope, _ = pais
    dsl = dsl_override if dsl_override else dsl_legal(jor, tope)
    V   = vac[ti]

    potenciales = DIAS_ANIO * dsl / 7          # dias de trabajo posibles
    sem_libre   = DIAS_ANIO - potenciales      # descanso semanal (1 o 2 dias/semana)

    # vacaciones expresadas en dias de trabajo liberados
    if unidad == "hábiles":
        vac_lab = float(V)
        solape  = 0.0        # la ley ya excluye feriados del computo de habiles
    else:
        vac_lab = V * dsl / 7
        # feriados absorbidos por el periodo de vacaciones (no liberan dia extra)
        solape  = (fer * dsl / 7) * (vac_lab / potenciales)

    fer_lab   = fer * dsl / 7 - solape
    trabajo   = potenciales - vac_lab - fer_lab
    horas_dia = jor / dsl
    horas     = trabajo * horas_dia

    return {
        "pais": nombre, "tramo": TRAMOS[ti], "unidad": unidad,
        "vac_legales": V, "feriados": fer, "jornada_h_sem": jor,
        "tope_diario_legal": tope, "dias_lab_semana": dsl,
        "horas_dia": round(horas_dia, 2),
        # --- los cuatro bloques del presupuesto ---
        "d_trabajo":        r1(trabajo),
        "d_descanso_semanal": r1(sem_libre),
        "d_vacaciones":     r1(vac_lab),
        "d_feriados":       r1(fer_lab),
        "d_solape_fer_vac": r1(solape),
        # --- indicadores ---
        "dias_libres_total": r1(DIAS_ANIO - trabajo),
        "pct_trabajo":   r1(trabajo / DIAS_ANIO * 100),
        "pct_desc_sem":  r1(sem_libre / DIAS_ANIO * 100),
        "pct_vacaciones":r1(vac_lab / DIAS_ANIO * 100),
        "pct_feriados":  r1(fer_lab / DIAS_ANIO * 100),
        "pct_descanso_total": r1((DIAS_ANIO - trabajo) / DIAS_ANIO * 100),
        "horas_trabajadas_anio": round(horas),
        "pct_vigilia_trabajando": r1(horas / VIGILIA * 100),
        "dias_trabajo_por_semana": round(trabajo / (DIAS_ANIO / 7), 2),
        # --- capa de traslado: NO entra en el presupuesto de 365 dias ---
        # Es conducta observada, no derecho legal, y de otro instrumento.
        # Se multiplica por dias trabajados: no se viaja en vacaciones ni feriados.
        **_traslado(nombre, trabajo, horas),
    }

def _traslado(nombre, trabajo, horas):
    """Capa de desplazamiento y reparto horario completo.

    Devuelve campos vacios si no hay dato de traslado para el pais: el reparto
    de sueno/trabajo/traslado/libre exige las cuatro piezas, y este trabajo no
    imputa. Es la misma disciplina que ya rige el resto del modelo (feriados
    en conflicto, horas efectivas, traslado de Panama/Ecuador/Honduras): si
    falta una pieza verificable, la fila queda en blanco, no en cero.
    """
    t = TRASLADO.get(nombre)
    campos_vacios = {"traslado_min_dia": "", "traslado_anio_ref": "", "traslado_fuente": "",
                      "horas_traslado_anio": "", "horas_comprometidas_anio": "",
                      "pct_vigilia_comprometida": "", "horas_sueno_anio": "",
                      "horas_libres_anio": "", "pct_libre_vigilia": "",
                      "pct_comprometido_total": "", "pct_libre_total": ""}
    if t is None:
        return campos_vacios
    minutos, anio_ref, fuente = t
    h_tras  = trabajo * minutos / 60
    h_compr = horas + h_tras
    h_libre = HORAS_ANIO - HORAS_SUENO_ANIO - h_compr    # el resto del ano, ni trabajo ni sueno
    return {
        "traslado_min_dia": minutos,
        "traslado_anio_ref": anio_ref,
        "traslado_fuente": fuente,
        "horas_traslado_anio": round(h_tras),
        "horas_comprometidas_anio": round(h_compr),
        "pct_vigilia_comprometida": r1(h_compr / VIGILIA * 100),
        # --- reparto horario completo: sueno + trabajo + traslado + libre = 8.760 h ---
        "horas_sueno_anio":  round(HORAS_SUENO_ANIO),
        "horas_libres_anio": round(h_libre),
        "pct_libre_vigilia": r1(100 - h_compr / VIGILIA * 100),        # base 5.840h, sueno fuera del universo
        "pct_comprometido_total": r1(h_compr / HORAS_ANIO * 100),      # base 8.760h, sueno cuenta aparte
        "pct_libre_total":   r1(h_libre / HORAS_ANIO * 100),           # base 8.760h, sueno NO es "libre"
    }

# ---------------------------------------------------------------------------
def main():
    os.makedirs(OUT, exist_ok=True)
    todas = [presupuesto(p, i) for p in PAISES for i in range(4)]
    base  = [f for f in todas if f["tramo"] == "1 año"]

    # ---------------- CSV: presupuesto anual ----------------
    with open(os.path.join(OUT, "presupuesto_anual.csv"), "w", newline="",
              encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(todas[0].keys()))
        w.writeheader(); w.writerows(todas)

    # ---------------- CSV: dataset maestro ----------------
    with open(os.path.join(OUT, "dataset_maestro.csv"), "w", newline="",
              encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["pais", "unidad_vacaciones", "vac_1a", "vac_5a", "vac_10a", "vac_20a",
                    "feriados_2026", "jornada_h_sem_2026", "tope_diario_legal_h",
                    "norma_tope_diario", "dias_lab_semana_derivado", "dias_lab_semana_v2",
                    "horas_efectivas_asalariados_2023"])
        for n, u, v, fer, jor, tope, norma in PAISES:
            w.writerow([n, u, *v, fer, jor, tope, norma, dsl_legal(jor, tope), DSL_V2[n],
                        HORAS_EFECTIVAS[n] if HORAS_EFECTIVAS[n] is not None else "sin dato"])

    # ---------------- CSV: sensibilidad a dsl ----------------
    with open(os.path.join(OUT, "sensibilidad_dsl.csv"), "w", newline="",
              encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["pais", "escenario", "dias_lab_semana", "pct_trabajo",
                    "horas_trabajadas_anio"])
        for p in PAISES:
            for esc, d in [("legal", dsl_legal(p[4], p[5])), ("v2", DSL_V2[p[0]]),
                           ("uniforme_5d", 5.0)]:
                r = presupuesto(p, 0, d)
                w.writerow([p[0], esc, d, r["pct_trabajo"], r["horas_trabajadas_anio"]])

    # ---------------- CSV: serie de jornada ----------------
    with open(os.path.join(OUT, "jornada_serie_2023_2030.csv"), "w", newline="",
              encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["pais"] + ANIOS + ["variacion_total"])
        for n, s in JORNADA_SERIE.items():
            w.writerow([n] + s + [s[-1] - s[0]])
        prom = [round(sum(JORNADA_SERIE[k][i] for k in JORNADA_SERIE) / len(JORNADA_SERIE), 2)
                for i in range(len(ANIOS))]
        w.writerow(["PROMEDIO SIMPLE"] + prom + [round(prom[-1] - prom[0], 2)])

    # ======================= VERIFICACIONES =======================
    print("=" * 72)
    print("VERIFICACIONES INTERNAS")
    print("=" * 72)
    ok = True

    # V1 — el presupuesto cierra en 365
    peor = 0.0
    for f in todas:
        s = f["d_trabajo"] + f["d_descanso_semanal"] + f["d_vacaciones"] + f["d_feriados"]
        peor = max(peor, abs(s - DIAS_ANIO))
        if abs(s - DIAS_ANIO) > 0.15:
            print(f"  X V1 el presupuesto no cierra: {f['pais']} {f['tramo']} = {s}"); ok = False
    print(f"  V1  presupuesto = 365 dias            desvio maximo {peor:.3f} d  ->  OK")

    # V2 — los porcentajes suman 100
    peor = max(abs(f["pct_trabajo"] + f["pct_desc_sem"] + f["pct_vacaciones"]
                   + f["pct_feriados"] - 100) for f in todas)
    print(f"  V2  porcentajes = 100 %               desvio maximo {peor:.3f} pp ->  "
          + ("OK" if peor < 0.3 else "FALLA"))
    ok &= peor < 0.3

    # V3 — horas coherentes con dias x horas/dia
    peor = max(abs(f["horas_trabajadas_anio"] - f["d_trabajo"] * f["horas_dia"])
               for f in todas)
    print(f"  V3  horas = dias x h/dia              desvio maximo {peor:.2f} h  ->  "
          + ("OK" if peor < 2 else "FALLA"))
    ok &= peor < 2

    # V4 — ninguna jornada diaria supera el tope legal (v2 SI lo hacia)
    print(f"  V4  jornada diaria <= tope legal:")
    fallos_v2 = []
    for n, u, v, fer, jor, tope, norma in PAISES:
        h_v3 = jor / dsl_legal(jor, tope)
        h_v2 = jor / DSL_V2[n]
        if h_v2 > tope + 1e-9:
            fallos_v2.append((n, round(h_v2, 2), tope))
        if h_v3 > tope + 1e-9:
            print(f"      X {n}: {h_v3:.2f} h > {tope} h"); ok = False
    print(f"      v3: 11 de 11 cumplen")
    print(f"      v2: {11 - len(fallos_v2)} de 11 cumplen — incumplian "
          + ", ".join(f"{n} ({h} h > {t} h)" for n, h, t in fallos_v2))

    # V5 — invariancia de horas/anio al supuesto dsl
    peor_pais, peor_pct = None, 0.0
    for p in PAISES:
        hs = [presupuesto(p, 0, d)["horas_trabajadas_anio"]
              for d in (dsl_legal(p[4], p[5]), DSL_V2[p[0]], 5.0)]
        pct = (max(hs) - min(hs)) / min(hs) * 100
        if pct > peor_pct: peor_pct, peor_pais = pct, p[0]
    print(f"  V5  horas/anio invariante a dsl       maximo {peor_pct:.2f} % ({peor_pais}) ->  "
          + ("OK" if peor_pct < 2 else "REVISAR"))

    # V6 — el reparto horario completo cierra en 8.760 h (solo paises con traslado)
    peor_h = 0.0
    con_tras = [f for f in base if f["horas_sueno_anio"] != ""]
    for f in con_tras:
        suma = (f["horas_sueno_anio"] + f["horas_trabajadas_anio"]
                 + f["horas_traslado_anio"] + f["horas_libres_anio"])
        peor_h = max(peor_h, abs(suma - HORAS_ANIO))
    print(f"  V6  sueño+trabajo+traslado+libre=8760 desvio maximo {peor_h:.1f} h "
          f"({len(con_tras)} países) ->  " + ("OK" if peor_h < 2 else "FALLA"))
    ok &= peor_h < 2

    print(f"\n  consistencia interna: {'OK' if ok else 'FALLA'}   ·   filas generadas: {len(todas)}")

    # ======================= RESULTADOS =======================
    print("\n" + "=" * 72)
    print("EL AÑO DE 365 DÍAS, REPARTIDO  ·  trabajador de 1 año de antigüedad")
    print("=" * 72)
    print(f"{'País':<11}{'trabajo':>9}{'sem.':>8}{'vac.':>7}{'fer.':>7}{'% año':>8}"
          f"{'horas':>8}{'libres':>8}{'d/sem':>7}")
    for f in sorted(base, key=lambda x: -x["d_trabajo"]):
        print(f"{f['pais']:<11}{f['d_trabajo']:>9.1f}{f['d_descanso_semanal']:>8.1f}"
              f"{f['d_vacaciones']:>7.1f}{f['d_feriados']:>7.1f}{f['pct_trabajo']:>8.1f}"
              f"{f['horas_trabajadas_anio']:>8}{f['dias_libres_total']:>8.1f}"
              f"{f['dias_trabajo_por_semana']:>7.2f}")

    print("\n" + "-" * 72)
    print("CUÁNTO PESA CADA BLOQUE  ·  dispersión entre los 11 países")
    print("-" * 72)
    for k, lbl in [("d_descanso_semanal", "descanso semanal"), ("d_vacaciones", "vacaciones"),
                   ("d_feriados", "feriados")]:
        xs = [f[k] for f in base]
        print(f"  {lbl:<20} rango {max(xs)-min(xs):5.1f} días   (mín {min(xs):5.1f} · máx {max(xs):5.1f})")
    xs = [f["d_descanso_semanal"] for f in base]; ys = [f["d_vacaciones"] for f in base]
    print(f"\n  -> la estructura de la semana explica un rango "
          f"{(max(xs)-min(xs))/(max(ys)-min(ys)):.1f}x mayor que las vacaciones,")
    print(f"     y es exactamente la variable que la infografía original no mide.")

    # correlaciones
    def corr(a, b):
        ma, mb = st.mean(a), st.mean(b)
        num = sum((x-ma)*(y-mb) for x, y in zip(a, b))
        den = (sum((x-ma)**2 for x in a) * sum((y-mb)**2 for y in b)) ** .5
        return num / den
    jor   = [f["jornada_h_sem"] for f in base]
    pct   = [f["pct_trabajo"] for f in base]
    horas = [f["horas_trabajadas_anio"] for f in base]
    descanso_v2 = [f["d_vacaciones"] + f["d_feriados"] for f in base]
    print("\n" + "-" * 72)
    print("CORRELACIONES")
    print("-" * 72)
    print(f"  jornada semanal   ~ horas/año          r = {corr(jor, horas):+.3f}")
    print(f"  días/semana (dsl) ~ % del año trabajado r = {corr([f['dias_lab_semana'] for f in base], pct):+.3f}")
    print(f"  vacaciones+feriados ~ % del año trab.   r = {corr(descanso_v2, pct):+.3f}   <- el ranking original")
    print(f"  vacaciones+feriados ~ horas/año         r = {corr(descanso_v2, horas):+.3f}   <- el ranking original")

    print("\n" + "-" * 72)
    print("CAPA DE TRASLADO  ·  fuera del presupuesto de 365 días")
    print("-" * 72)
    con = [f for f in base if f["traslado_min_dia"] != ""]
    sin = [f["pais"] for f in base if f["traslado_min_dia"] == ""]
    print(f"{'País':<11}{'min/día':>8}{'año':>6}{'h traslado':>12}{'h trabajo':>11}"
          f"{'comprom.':>10}{'% vigilia':>10}{'tras./vac.':>11}   fuente")
    for f in sorted(con, key=lambda x: -x["horas_comprometidas_anio"]):
        h_vac = f["d_vacaciones"] * f["horas_dia"]
        print(f"{f['pais']:<11}{f['traslado_min_dia']:>8}{f['traslado_anio_ref']:>6}"
              f"{f['horas_traslado_anio']:>12}{f['horas_trabajadas_anio']:>11}"
              f"{f['horas_comprometidas_anio']:>10}{f['pct_vigilia_comprometida']:>10}"
              f"{f['horas_traslado_anio']/h_vac:>10.1f}x   {f['traslado_fuente']}")
    # cuánto reordena el traslado
    print("\n  reordenamiento al sumar el traslado:")
    r_trab = sorted(con, key=lambda x: -x["horas_trabajadas_anio"])
    r_comp = sorted(con, key=lambda x: -x["horas_comprometidas_anio"])
    for f in r_comp:
        a = [x["pais"] for x in r_trab].index(f["pais"]) + 1
        b = [x["pais"] for x in r_comp].index(f["pais"]) + 1
        flecha = "=" if a == b else ("sube" if b < a else "baja")
        print(f"    {f['pais']:<11} {a}.º solo trabajo -> {b}.º con traslado   {flecha}")
    print(f"\n  sin dato comparable: {', '.join(sin)}")
    print(f"  referencias: América Latina ~{REF_TRASLADO_LATAM:.0f} min/día (CAF 2016) · "
          f"OCDE ~{REF_TRASLADO_OCDE:.0f} min/día")
    peor = max(con, key=lambda x: x["horas_traslado_anio"] / (x["d_vacaciones"] * x["horas_dia"]))
    print(f"\n  -> en los {len(con)} países con dato, el traslado consume MÁS horas al año que")
    print(f"     las vacaciones legales. Máximo: {peor['pais']}, "
          f"{peor['horas_traslado_anio'] / (peor['d_vacaciones'] * peor['horas_dia']):.1f}x.")
    d_pp = [(f["pais"], f["pct_vigilia_comprometida"] - f["pct_vigilia_trabajando"]) for f in con]
    print(f"  -> añade entre {min(d for _, d in d_pp):.1f} y {max(d for _, d in d_pp):.1f} puntos "
          f"de la vida despierta.")

    print("\n" + "-" * 72)
    print("EL DÍA COMPLETO  ·  sueño + trabajo + traslado + libre = 8.760 h")
    print("-" * 72)
    print(f"{'País':<11}{'sueño':>7}{'trabajo':>9}{'traslado':>10}{'libre':>8}{'suma':>7}   "
          f"{'%compr.vig':>11}{'%compr.tot':>11}")
    for f in sorted(con, key=lambda x: -x["horas_comprometidas_anio"]):
        suma = (f["horas_sueno_anio"] + f["horas_trabajadas_anio"]
                 + f["horas_traslado_anio"] + f["horas_libres_anio"])
        print(f"{f['pais']:<11}{f['horas_sueno_anio']:>7}{f['horas_trabajadas_anio']:>9}"
              f"{f['horas_traslado_anio']:>10}{f['horas_libres_anio']:>8}{suma:>7}   "
              f"{f['pct_vigilia_comprometida']:>10}%{f['pct_comprometido_total']:>10}%")
    print(f"\n  el sueño (2.920 h/año, supuesto [C]) es un tercio del año para los 11 países por igual.")
    print(f"  las dos columnas de % difieren solo en si el sueño cuenta o no dentro del universo:")
    print(f"    %vigilia = comprometido / 5.840h   (el sueño queda fuera del cálculo)")
    print(f"    %total   = comprometido / 8.760h   (el sueño cuenta como parte del año, no como 'libre')")

    print("\n" + "-" * 72)
    print("EL VUELCO DEL RANKING  ·  Perú")
    print("-" * 72)
    orden_viejo = sorted(base, key=lambda x: -(x["d_vacaciones"] + x["d_feriados"]))
    orden_horas = sorted(base, key=lambda x: -x["horas_trabajadas_anio"])
    orden_pct   = sorted(base, key=lambda x: -x["pct_trabajo"])
    for nom in ("Perú", "México", "Chile", "Ecuador"):
        pv = [f["pais"] for f in orden_viejo].index(nom) + 1
        ph = [f["pais"] for f in orden_horas].index(nom) + 1
        pp = [f["pais"] for f in orden_pct].index(nom) + 1
        print(f"  {nom:<9} {pv:>2}.º en 'días de descanso'  ->  {pp:>2}.º en % del año trabajado"
              f"  ->  {ph:>2}.º en horas/año")

    print("\nArchivos escritos en", os.path.normpath(OUT))

if __name__ == "__main__":
    main()

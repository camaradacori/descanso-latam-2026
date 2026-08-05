#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelo completo — Descanso remunerado en Latinoamérica 2026
============================================================
Reproduce TODAS las cifras derivadas de la infografía HTML.

Ejecutar:  python3 modelo_completo.py
Genera:    ../datos/dataset_maestro.csv
           ../datos/resultados_por_antiguedad.csv
           ../datos/jornada_serie_2023_2030.csv

Cada campo de entrada lleva un código de confianza:
  [A] verificado en fuente primaria (texto de ley o publicación oficial/OIT)
  [B] verificado en prensa especializada, con al menos dos coincidencias
  [C] clasificación o supuesto estructural DEL AUTOR DEL MODELO — auditar primero
"""
import csv, os, json

VIGILIA = 5840          # 8760 h del año − 8 h diarias de sueño   [C] supuesto
BASE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(BASE, "..", "datos")

# ---------------------------------------------------------------------------
# DATASET MAESTRO
# ---------------------------------------------------------------------------
# vac      [A] días de vacaciones legales por tramo de antigüedad [1, 5, 10, 20 años]
# unidad   [A] unidad en que la ley expresa las vacaciones
# fer      [A/B/?] número de feriados nacionales oficiales 2026 — ver README §3.3,
#          el nivel de confianza VARÍA POR PAÍS
# tras     [C] de esos feriados, cuántos traslada la ley a lunes/viernes
# lit      [C] cuántos son litúrgicos o de carnaval (siempre caen en día hábil)
# jor      [A] jornada máxima legal semanal vigente a julio de 2026
# dsl      [C] días laborables por semana — promedio estructural del país
PAISES = [
 # nombre       unidad         vac[1,5,10,20]     fer tras lit jor  dsl
 ("Perú",      "calendario", [30, 30, 30, 30],   16,  0,  2, 48, 6.0),
 ("Panamá",    "calendario", [30, 30, 30, 30],   12,  3,  2, 48, 5.5),
 ("Brasil",    "calendario", [30, 30, 30, 30],   10,  0,  2, 44, 5.0),
 ("Colombia",  "hábiles",    [15, 15, 15, 15],   18, 12,  2, 42, 5.0),
 ("Chile",     "hábiles",    [15, 15, 15, 18],   17,  3,  1, 42, 5.0),
 ("Argentina", "corridos",   [14, 21, 28, 35],   16,  4,  2, 48, 5.0),
 ("Uruguay",   "hábiles",    [20, 21, 22, 25],   15,  4,  4, 48, 5.5),
 ("Ecuador",   "calendario", [15, 15, 20, 30],   12,  5,  3, 40, 5.0),
 ("Paraguay",  "hábiles",    [12, 18, 30, 30],   12,  4,  2, 48, 5.0),
 ("Honduras",  "hábiles",    [10, 20, 20, 20],   11,  0,  2, 44, 5.5),
 ("México",    "hábiles",    [12, 20, 22, 26],    7,  3,  0, 48, 6.0),
]
TRAMOS = ["1 año", "5 años", "10 años", "20 años"]

# Horas efectivas semanales de ASALARIADOS, ILOSTAT 2023 (OIT/Gontero 2025) [A]
# None = la fuente no publica el valor para ese país. NO se imputa.
HORAS_EFECTIVAS = {
    "Colombia": 46.6, "Honduras": 45.0, "Argentina": 37.0, "Uruguay": 37.0,
    "Perú": None, "Panamá": None, "Brasil": None, "Chile": None,
    "Ecuador": None, "Paraguay": None, "México": None,
}
REF_LATAM, REF_OCDE = 42.0, 34.6

# Jornada máxima legal por año [A]. Solo 3 países registran cambios.
JORNADA_SERIE = {
    "Perú":      [48]*8, "Panamá":   [48]*8, "Argentina": [48]*8,
    "Uruguay":   [48]*8, "Paraguay": [48]*8, "Brasil":    [44]*8,
    "Honduras":  [44]*8, "Ecuador":  [40]*8,
    "Colombia": [47, 46, 44, 42, 42, 42, 42, 42],
    "Chile":    [45, 44, 44, 42, 42, 40, 40, 40],
    "México":   [48, 48, 48, 48, 46, 44, 42, 40],
}
ANIOS = list(range(2023, 2031))

r1 = lambda v: round(v, 1)

# ---------------------------------------------------------------------------
# FÓRMULAS
# ---------------------------------------------------------------------------
def feriados_efectivos(fer, tras, lit, dsl):
    """Esperanza matemática de feriados que caen en día laborable.

    Trasladables por ley  -> factor 1,0 (la norma garantiza día hábil)
    Litúrgicos / carnaval -> factor 1,0 (por construcción del calendario litúrgico
                             nunca caen en fin de semana: Jueves y Viernes Santo,
                             Corpus Christi, lunes y martes de carnaval)
    Fecha fija            -> factor dsl/7 (probabilidad de no caer en fin de semana)
    """
    fijos = fer - tras - lit
    return r1(tras + lit + fijos * (dsl / 7))

def vac_en_laborables(v, unidad, dsl):
    """Vacaciones expresadas en días de trabajo efectivamente liberados."""
    if unidad == "hábiles":
        return r1(v)                    # ya son días de trabajo
    return r1(v * dsl / 7)              # calendario/corridos consumen fines de semana

def vac_en_calendario(v, unidad):
    """Vacaciones expresadas en días de calendario."""
    if unidad == "hábiles":
        return r1(v * 7 / 5)            # 5 hábiles = 7 calendario
    return r1(v)

def calcular(p):
    nombre, unidad, vac, fer, tras, lit, jor, dsl = p
    ferLab = feriados_efectivos(fer, tras, lit, dsl)
    h_dia  = jor / dsl
    filas  = []
    for i, v in enumerate(vac):
        vLab = vac_en_laborables(v, unidad, dsl)
        tot  = r1(vLab + ferLab)
        hDesc = r1(tot * h_dia)
        hTeo  = r1(jor * 52)
        hTrab = r1(hTeo - hDesc)
        filas.append({
            "pais": nombre, "tramo": TRAMOS[i], "vac_legales": v, "unidad": unidad,
            "vac_calendario": vac_en_calendario(v, unidad), "vac_laborables": vLab,
            "feriados": fer, "trasladables": tras, "liturgicos": lit,
            "fijos": fer - tras - lit, "feriados_efectivos": ferLab,
            "jornada_h_sem": jor, "dias_lab_semana": dsl, "horas_dia": round(h_dia, 2),
            "suma_bruta": v + fer,
            "descanso_dias_laborables": tot,
            "horas_descanso_anio": hDesc,
            "horas_teoricas_anio": hTeo,
            "horas_trabajadas_anio": hTrab,
            # la jornada se CANCELA en este cociente: equivale a tot/(dsl*52)
            "pct_anio_laboral_descanso": r1(tot / (dsl * 52) * 100),
            "pct_vigilia_trabajando":    r1(hTrab / VIGILIA * 100),
        })
    return filas

# ---------------------------------------------------------------------------
def main():
    os.makedirs(OUT, exist_ok=True)
    todas = [f for p in PAISES for f in calcular(p)]

    with open(os.path.join(OUT, "resultados_por_antiguedad.csv"), "w",
              newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(todas[0].keys()))
        w.writeheader(); w.writerows(todas)

    with open(os.path.join(OUT, "dataset_maestro.csv"), "w",
              newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["pais", "unidad_vacaciones", "vac_1a", "vac_5a", "vac_10a", "vac_20a",
                    "feriados_2026", "trasladables", "liturgicos", "fecha_fija",
                    "jornada_h_sem_2026", "dias_lab_semana",
                    "horas_efectivas_asalariados_2023"])
        for n, u, v, fer, tr, li, jo, ds in PAISES:
            w.writerow([n, u, *v, fer, tr, li, fer - tr - li, jo, ds,
                        HORAS_EFECTIVAS[n] if HORAS_EFECTIVAS[n] is not None else "sin dato"])

    with open(os.path.join(OUT, "jornada_serie_2023_2030.csv"), "w",
              newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["pais"] + ANIOS + ["variacion_total"])
        for n, s in JORNADA_SERIE.items():
            w.writerow([n] + s + [s[-1] - s[0]])
        prom = [round(sum(JORNADA_SERIE[k][i] for k in JORNADA_SERIE) / len(JORNADA_SERIE), 2)
                for i in range(len(ANIOS))]
        w.writerow(["PROMEDIO SIMPLE"] + prom + [round(prom[-1] - prom[0], 2)])

    # ---- verificaciones internas ----
    print("VERIFICACIONES")
    ok = True
    for f in todas:
        if f["suma_bruta"] != f["vac_legales"] + f["feriados"]:
            print("  X suma_bruta", f["pais"]); ok = False
        rec = r1(f["vac_laborables"] + f["feriados_efectivos"])
        if abs(rec - f["descanso_dias_laborables"]) > 0.05:
            print("  X descanso", f["pais"]); ok = False
        if abs(f["horas_teoricas_anio"] - f["horas_descanso_anio"]
               - f["horas_trabajadas_anio"]) > 0.2:
            print("  X horas", f["pais"]); ok = False
        # la jornada debe cancelarse en el índice porcentual
        via_horas = f["horas_descanso_anio"] / f["horas_teoricas_anio"] * 100
        if abs(via_horas - f["pct_anio_laboral_descanso"]) > 0.15:
            print("  X el índice NO se cancela en", f["pais"]); ok = False
    print("  consistencia interna:", "OK" if ok else "FALLA")
    print("  filas generadas:", len(todas))

    print("\nRANKING · días laborables de descanso")
    for tr in TRAMOS:
        sub = sorted([f for f in todas if f["tramo"] == tr],
                     key=lambda x: -x["descanso_dias_laborables"])
        print(f"  {tr:<9}", " · ".join(f"{i+1}.{f['pais']}" for i, f in enumerate(sub[:4])))

    print("\nArchivos escritos en", os.path.normpath(OUT))

if __name__ == "__main__":
    main()

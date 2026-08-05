# -*- coding: utf-8 -*-
import json

# unidad: 'calendario' (incluye fines de semana), 'habil' (solo laborables)
# traslado: fraccion de feriados que la ley mueve a lunes/viernes (garantiza dia laborable)
P = [
 # pais, vac, unidad, feriados, jornada_h, feriados_trasladables, dias_semana_laborales
 ("Perú",      30,"calendario",16,48,0,  6),
 ("Panamá",    30,"calendario",12,48,3,  5.5),
 ("Brasil",    30,"calendario",12,44,0,  5),
 ("Colombia",  15,"habil",     18,42,12, 5),
 ("Chile",     15,"habil",     17,42,3,  5),
 ("Argentina", 14,"calendario",16,48,4,  5),
 ("Uruguay",   20,"habil",     15,48,4,  5.5),
 ("Ecuador",   15,"calendario",12,40,5,  5),
 ("Paraguay",  12,"habil",     12,48,4,  5),
 ("Honduras",  10,"habil",     11,44,0,  5.5),
 ("México",    12,"habil",      7,48,3,  6),
]

out=[]
for pais,vac,uni,fer,jor,tras,dsl in P:
    # 1) vacaciones -> dias laborables efectivamente liberados
    if uni=="habil":
        vac_lab = vac                      # ya son laborables
        vac_cal = round(vac*7/5,1)         # equivalente calendario
    else:
        vac_lab = round(vac*dsl/7,1)       # de calendario a laborables segun semana del pais
        vac_cal = vac
    # 2) feriados que caen en dia laborable en 2026
    fijos = fer - tras
    fer_lab = round(tras*1.0 + fijos*(dsl/7),1)
    # 3) totales
    tot_lab = round(vac_lab + fer_lab,1)
    h_dia   = jor/dsl
    h_desc  = round(tot_lab*h_dia,1)
    h_teor  = jor*52
    h_trab  = round(h_teor - h_desc,1)
    out.append(dict(pais=pais, vac=vac, uni=uni, fer=fer, jor=jor, tras=tras, dsl=dsl,
                    vac_cal=vac_cal, vac_lab=vac_lab, fer_lab=fer_lab,
                    bruto=vac+fer, tot_lab=tot_lab, h_dia=round(h_dia,2),
                    h_desc=h_desc, h_trab=h_trab))

for r in sorted(out,key=lambda x:-x["tot_lab"]):
    print(f'{r["pais"]:<10} bruto={r["bruto"]:>3}  vacLab={r["vac_lab"]:>5}  ferLab={r["fer_lab"]:>5}  TOTlab={r["tot_lab"]:>5}  h/dia={r["h_dia"]:>5}  hTrab={r["h_trab"]:>7}')
json.dump(out, open("datos.json","w"), ensure_ascii=False, indent=1)

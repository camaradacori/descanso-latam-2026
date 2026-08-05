# -*- coding: utf-8 -*-
import json
# vac por antiguedad: 1,5,10,20 años | feriados: tras(ley lunes) lit(liturgico/carnaval habil) fijos
P=[
 #pais, uni, [v1,v5,v10,v20], fer, tras, lit, jor, dsl
 ("Perú","calendario",[30,30,30,30],16,0,2,48,6),
 ("Panamá","calendario",[30,30,30,30],12,3,2,48,5.5),
 ("Brasil","calendario",[30,30,30,30],12,0,1,44,5),
 ("Colombia","habil",[15,15,15,15],18,12,2,42,5),
 ("Chile","habil",[15,15,15,18],17,3,1,42,5),
 ("Argentina","calendario",[14,21,28,35],16,4,2,48,5),
 ("Uruguay","habil",[20,21,22,25],15,4,4,48,5.5),
 ("Ecuador","calendario",[15,15,20,30],12,5,3,40,5),
 ("Paraguay","habil",[12,18,30,30],12,4,2,48,5),
 ("Honduras","habil",[10,20,20,20],11,0,2,44,5.5),
 ("México","habil",[12,20,22,26],7,3,0,48,6),
]
out=[]
for pais,uni,vs,fer,tras,lit,jor,dsl in P:
    fijos=fer-tras-lit
    ferLabNew=round(tras*1+lit*1+fijos*(dsl/7),1)
    ferLabOld=round(tras*1+(fer-tras)*(dsl/7),1)
    r={"p":pais,"uni":uni,"fer":fer,"tras":tras,"lit":lit,"fijos":fijos,
       "jor":jor,"dsl":dsl,"ferLab":ferLabNew,"ferLabOld":ferLabOld,
       "dif":round(ferLabNew-ferLabOld,1),"vacs":vs,"vlab":[],"tot":[],"htr":[]}
    for v in vs:
        vlab = v if uni=="habil" else round(v*dsl/7,1)
        tot  = round(vlab+ferLabNew,1)
        htr  = round(jor*52 - tot*(jor/dsl),1)
        r["vlab"].append(vlab); r["tot"].append(tot); r["htr"].append(htr)
    out.append(r)

print("=== EFECTO DE CORREGIR LA ESPERANZA DE FERIADOS ===")
for r in sorted(out,key=lambda x:-x["dif"]):
    print(f'{r["p"]:<10} fer={r["fer"]:>2} (tras{r["tras"]:>3} lit{r["lit"]:>2} fij{r["fijos"]:>3})  antes={r["ferLabOld"]:>5} → ahora={r["ferLab"]:>5}  Δ{r["dif"]:+.1f}')

print("\n=== RANKING SEGUN ANTIGUEDAD (dias laborables de descanso) ===")
et=["1 año","5 años","10 años","20 años"]
for i in range(4):
    o=sorted(out,key=lambda x:-x["tot"][i])
    print(f'\n-- {et[i]} --')
    for j,r in enumerate(o):
        print(f'  {j+1:>2}. {r["p"]:<10} {r["tot"][i]:>5} d   ({r["htr"][i]:>7.1f} h/año)')
json.dump(out,open("datos2.json","w"),ensure_ascii=False)

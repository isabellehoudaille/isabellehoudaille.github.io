#!/usr/bin/env python3
"""Génère le contenu statique de index.html à partir de data.json.

Le site s'affiche en JavaScript (data.json est lu dans le navigateur). Les robots qui
n'exécutent pas le JavaScript (moteurs de recherche, IA) ne verraient donc rien.
Ce script écrit le même contenu en HTML simple entre les repères SSR:START et SSR:END.
À relancer après chaque modification de data.json :  python3 outils/prerender.py
"""
import json, html, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
e = lambda s: html.escape(str(s), quote=True)

def ul(items): return "<ul>" + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>"

def res(r):
    tag = "estimation" if r.get("est") else "constaté"
    return f"<li>{e(r['t'])} ({e(r['l'])}) : avant {e(r['avl'])}, après {e(r['apl'])}, {tag}</li>"

out = []
M = D["meta"]
out.append('<section id="haut-ssr">')
out.append(f"<h1>{e(M['nom'])} · {e(M['titre'])}</h1>")
if M.get("role"): out.append(f"<p>{e(M['role'])}</p>")
for para in D["profil"]["texte"].split("\n"): out.append(f"<p>{e(para)}</p>")
out.append(f"<p>{e(M['lieu'])}</p>")
out.append(f'<p><a href="mailto:{e(M["email"])}">{e(M["email"])}</a> · <a href="/rdv/">{e(D["contact"]["rdv"])}</a> · '
           f'<a href="{e(M["linkedin"])}">Profil LinkedIn</a></p>')
out.append("</section>")

out.append('<section id="expertise-ssr">')
out.append(f"<h2>{e(D['titres']['expertise'])}</h2>")
for f in D["fonctions"]:
    out.append(f"<article><h3>{e(f['t'])}</h3><p>{e(f['acc'])}</p>")
    if f.get("niv"):
        for n in f["niv"]:
            out.append(f"<h4>{e(n['n'])} : {e(n['t'])}</h4>{ul(n['pts'])}<p>{e(D.get('niv_label', 'Ce que vous y gagnez'))} : {e(n['g'])}</p>")
    elif f.get("d"):
        out.append(f"<p>{e(f['d'])}</p>")
    out.append("<h4>Vos cas métiers en action : exemples, non limitatifs</h4>" + ul(f["cas"]))
    if f.get("ba"):
        out.append(f"<h4>{e(f['ba'].get('titre', 'Avant, après'))}</h4><ul>" + "".join(f"<li>{e(x['t'])} : avant, {e(x['avant'])} ; après, {e(x['apres'])}</li>" for x in f["ba"]["items"]) + "</ul></article>")
    else:
        out.append("<h4>Indicateurs de réussite : exemples</h4><ul>" + "".join(res(r) for r in f["res"]) + "</ul></article>")
out.append("</section>")

out.append('<section id="chiffres-ssr">')
out.append(f"<h2>{e(D['titres']['chiffres'])}</h2><ul>")
for c in D["chiffres"]:
    out.append(f"<li>{e(c['n'])}{e(c['s'])} {e(c['l'])} : {e(c['d'])}</li>")
out.append("</ul>")
out.append(f"<p>{e(D['titres']['publics'])} : " + e(", ".join(D["publics"])) + ".</p></section>")

out.append('<section id="terrain-ssr">')
out.append(f"<h2>{e(D['titres']['terrain'])}</h2><p>{e(D['titres'].get('terrainHint', ''))}</p>")
out.append(ul([t["cap"] for t in D["terrain"]]) + "</section>")

P = D["posture"]
out.append('<section id="posture-ssr">')
out.append(f"<h2>Ma posture : le métier, la posture, puis les outils</h2><p>{e(P['intro'])}</p><ol>")
for it in P["items"]:
    out.append(f"<li><h3>{e(it['t'])}</h3><p>{e(it['s'])}</p><p>{e(it['d'])}</p></li>")
out.append(f"</ol><p>{e(P['cloture'])}</p><p>{e(P['pied'])}</p></section>")

out.append('<section id="realisations-ssr">')
out.append("<h2>Références et réalisations</h2>")
out.append("<p>Missions de conseil et de formation menées avec mes clients, du livre de prompts à l'agent métier.</p>")
for r in D["realisations"]:
    out.append(f"<article><h3>{e(r['t'])}</h3><p>{e(r['sous'])} · {e(r.get('type', ''))}</p><p>{e(r['d'])}</p>{ul(r.get('pts', []))}<p>{e(r['gain'])}</p></article>")
out.append("</section>")

O = D["offre"]
out.append('<section id="offre-ssr">')
out.append(f"<h2>{e(O['titre'])}</h2>")
for it in O["items"]:
    out.append(f"<article><h3>{e(it['t'])}</h3><p>{e(it['d'])}</p></article>")
out.append(f"<p>{e(O['pied'])}</p></section>")

out.append(f"<p>{e(D['contact']['titre'])}. {e(D['contact']['texte'])}</p>")
out.append("<p>cadreIActif, SASU au capital de 1 000 € · SIREN 100634658 · NDA 11923048992 · © 2026 Isabelle Houdaille</p>")

block = '<div class="ssr">' + "\n".join(out) + "</div>"
idx = ROOT / "index.html"
src = idx.read_text(encoding="utf-8")
new, n = re.subn(r"<!--SSR:START-->.*?<!--SSR:END-->", lambda m: "<!--SSR:START-->" + block + "<!--SSR:END-->", src, flags=re.S)
assert n == 1, "repères SSR introuvables dans index.html"
idx.write_text(new, encoding="utf-8")
print("contenu statique écrit :", len(block), "caractères")

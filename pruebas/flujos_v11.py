"""Pruebas de punta a punta de Fondacio Agenda 1.1 (45 verificaciones).
Cubren aceptar, preguntar, deshacer, crear actividad con asistentes, colores por eje,
filtro, vista Lista y búsqueda, compartir, imprimir, informe del mes, copia de seguridad,
restaurar, empezar vacía, letra grande, ayuda, recorrido guiado y DEF-01."""
import asyncio, json, re, os, sys, pathlib
# Uso: pip install playwright && playwright install chromium
#      python pruebas/flujos_v11.py   (desde la carpeta del repositorio)
RAIZ=pathlib.Path(__file__).resolve().parent.parent
URL=(RAIZ/'fondacio.html').as_uri()
COPIA=str(RAIZ/'pruebas'/'copia_prueba.json')
from playwright.async_api import async_playwright
OK=[];MAL=[]
def chk(nombre,cond,extra=''):
    (OK if cond else MAL).append(nombre+(' → '+str(extra) if not cond and extra else ''))
INIT="""
window.__wa=[];const _o=window.open;
window.open=function(u,...r){if(String(u).startsWith('https://wa.me')){window.__wa.push(String(u));return null}return _o.call(window,u,...r)};
"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(viewport={'width':1366,'height':768},locale='es-CO',timezone_id='America/Bogota',accept_downloads=True)
        await ctx.add_init_script(INIT)
        pg=await ctx.new_page(); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.on('dialog',lambda d:asyncio.ensure_future(d.accept()))
        await pg.goto(URL+'?sinTour'); await pg.wait_for_timeout(400)
        S=lambda: pg.evaluate('JSON.parse(localStorage.getItem("fondacio_v3")||"null")||S')
        # 1. Aceptar el taller: texto sin doble punto
        await pg.locator('#listaPend .pc', has_text='Taller de habilidades').locator('[data-ac=aceptar]').click()
        t=await pg.locator('#txt').input_value()
        chk('DEF-01 aceptar sin «p. m..»', 'p. m..' not in t and 'p. m. ¡Nos vemos!' in t, t)
        await pg.locator('#fr button[type=submit]').click(); await pg.wait_for_timeout(200)
        wa=await pg.evaluate('window.__wa'); chk('Aceptar abre WhatsApp', len(wa)==1 and 'Confirmo' in wa[0].replace('%20',' ') or 'Confirmo' in __import__('urllib.parse').parse.unquote(wa[0]), wa)
        st=await S(); ev=[e for e in st['eventos'] if e['titulo']=='Taller de habilidades digitales']
        chk('Aceptar crea la actividad', len(ev)==1)
        chk('Aceptar quita la marca de ejemplo? (no debe)', st.get('ejemplo') is True)
        # 2. Deshacer
        await pg.locator('#resp').click()
        await pg.locator('#listaResp [data-ac=deshacer]').first.click(); await pg.wait_for_timeout(200)
        st=await S(); chk('Deshacer quita la actividad', not any(e['titulo']=='Taller de habilidades digitales' for e in st['eventos']))
        # 3. Preguntar en Visita
        await pg.locator('#listaPend .pc', has_text='Visita').locator('[data-ac=preguntar]').click()
        t=await pg.locator('#txt').input_value(); chk('Preguntar pide lo que falta', 'la fecha, la hora y el lugar' in t, t)
        await pg.locator('#x').click()
        # 4. Crear actividad con asistentes e invitación sin doble punto
        await pg.click('#bNew')
        await pg.fill('#fe [name=titulo]','Taller de huerta'); await pg.select_option('#fe [name=eje]','com')
        await pg.fill('#fe [name=fecha]','2026-11-20'); await pg.fill('#fe [name=ini]','15:00'); await pg.fill('#fe [name=fin]','16:00')
        await pg.fill('#fe [name=asis]','25'); await pg.fill('#fe [name=lugar]','Huerta')
        await pg.locator('#fe details.box', has_text='Invitación para el grupo').locator('summary').click()
        inv=await pg.locator('#txt').input_value(); chk('DEF-01 invitación sin «p. m..»','p. m..' not in inv, inv)
        await pg.select_option('#tono','cercano'); inv2=await pg.locator('#txt').input_value(); chk('DEF-01 invitación cercana','p. m..' not in inv2, inv2)
        await pg.locator('#fe button[type=submit]').click(); await pg.wait_for_timeout(200)
        st=await S(); e=[x for x in st['eventos'] if x['titulo']=='Taller de huerta']
        chk('Actividad guardada con asistentes', e and e[0].get('asis')=='25', e)
        chk('Crear actividad no quita los datos de ejemplo', st.get('ejemplo') is True)
        # color por eje en el chip
        chip=pg.locator('.chip', has_text='Taller de huerta'); chk('Chip con color del eje', 'e-com' in (await chip.get_attribute('class') or ''))
        await chip.click(); await pg.wait_for_timeout(150)
        chk('Detalle del día muestra asistentes', await pg.locator('dialog .pill.ok', has_text='Asistieron 25').count()==1)
        await pg.locator('#x').click()
        # 5. Leyenda como filtro
        await pg.click('#ley [data-eje=eco]'); await pg.wait_for_timeout(100)
        n=await pg.locator('#calMes .chip').count(); clases=await pg.locator('#calMes .chip').evaluate_all('a=>a.map(x=>x.className)')
        chk('Filtro por la leyenda', n>0 and all('e-eco' in c for c in clases), clases)
        chk('Leyenda y lista sincronizadas', await pg.locator('#fEje').input_value()=='eco')
        await pg.click('#ley [data-eje=eco]'); chk('Quitar filtro', await pg.locator('#fEje').input_value()=='')
        # 6. Lista y búsqueda
        await pg.click('#vLis'); await pg.fill('#buscar','huerta'); await pg.wait_for_timeout(100)
        chk('Búsqueda en Lista', await pg.locator('#lisBody .lev').count()==1 and 'Taller de huerta' in await pg.locator('#lisBody').inner_text())
        await pg.fill('#buscar','zzz'); chk('Búsqueda sin resultados', 'No encontré' in await pg.locator('#lisBody').inner_text())
        await pg.fill('#buscar',''); await pg.click('#bPasadas'); chk('Ver pasadas incluye la del 20', 'Taller de huerta' in await pg.locator('#lisBody').inner_text())
        chk('Flechas ocultas en Lista', await pg.locator('#prev').is_hidden())
        await pg.click('#vMes'); chk('Flechas visibles en Mes', await pg.locator('#prev').is_visible())
        # 7. Compartir agenda
        await pg.click('#bShare'); await pg.select_option('#cRan','mes'); t=await pg.locator('#cTxt').input_value()
        chk('Compartir este mes incluye actividad', 'Taller de huerta' in t and '*Agenda de Fondacio*' in t, t[:200])
        await pg.click('#cWa'); wa=await pg.evaluate('window.__wa'); chk('Compartir abre WhatsApp', len(wa)>=2)
        async with ctx.expect_page() as pp:
            await pg.click('#cPr')
        imp=await pp.value; await imp.wait_for_load_state(); chk('Imprimir genera tabla', 'Taller de huerta' in await imp.content()); await imp.close()
        # 8. Informe
        await pg.click('#cInf'); await pg.select_option('#cMes','2026-11'); t=await pg.locator('#cTxt').input_value()
        chk('Informe cuenta asistentes', 'Personas que asistieron: 25' in t, t)
        chk('Informe por eje', 'Comunidad: 1' in t, t)
        await pg.locator('#x').click()
        # 9. Copia de seguridad y restaurar
        await pg.click('#bSet')
        async with pg.expect_download() as dl:
            await pg.click('#dExp')
        d=await dl.value; ruta=COPIA; await d.save_as(ruta)
        c=json.load(open(ruta)); chk('Copia sin la clave de IA', 'key' not in c['datos']['cfg'])
        chk('Copia con actividades', any(e['titulo']=='Taller de huerta' for e in c['datos']['eventos']))
        await pg.click('#dVac'); await pg.wait_for_timeout(200)
        st=await S(); chk('Empezar vacía', len(st['eventos'])==0 and len(st['pend'])==0 and st['ejemplo'] is False)
        chk('Aviso de ejemplo oculto', await pg.locator('#avEj').is_hidden())
        await pg.click('#bSet'); await pg.set_input_files('#fRest', ruta); await pg.wait_for_timeout(400)
        st=await S(); chk('Restaurar copia', any(e['titulo']=='Taller de huerta' for e in st['eventos']), len(st['eventos']))
        # 10. Letra grande
        await pg.click('#bSet'); await pg.check('#aGrande'); chk('Letra grande', await pg.evaluate('document.documentElement.classList.contains("grande")'))
        await pg.uncheck('#aGrande'); await pg.locator('#x2').click()
        # 11. Ayuda y recorrido
        await pg.click('#bHelp'); chk('Ayuda abre', await pg.locator('dialog .ayuda').count()==1)
        await pg.click('#hTour'); await pg.wait_for_timeout(300); chk('Recorrido desde Ayuda', await pg.locator('.tour-card').count()==1)
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(100); chk('Esc cierra recorrido', await pg.locator('.tour-card').count()==0)
        # 12. Guardar un mensaje nuevo
        await pg.click('#bPend'); await pg.fill('#fp [name=texto]','Buenas tardes, somos de la Junta de Acción Comunal. Queremos invitarlos a la reunión de líderes el 14 de diciembre de 3 a 5 pm en el salón comunal.')
        await pg.wait_for_timeout(100)
        chk('Extrae fecha y hora', await pg.locator('#fp [name=fecha]').input_value()=='2026-12-14' and await pg.locator('#fp [name=ini]').input_value()=='15:00')
        await pg.locator('#fp button[type=submit]').click(); await pg.wait_for_timeout(100)
        n=await pg.locator('#nPend').inner_text(); chk('Pendiente guardado (3 restaurados + 1 nuevo)', n=='4', n)

        # 13. Casos pendientes del plan que no necesitan Google ni IA
        await pg.reload(); await pg.wait_for_timeout(300)
        st=await S(); chk('CP-008 La actividad persiste al recargar', any(e['titulo']=='Taller de huerta' for e in st['eventos']))
        await pg.click('#bPend'); await pg.fill('#fp [name=lugar]','Casa de Rodolfo')
        await pg.fill('#fp [name=texto]','Los invitamos a la reunión el 3 de diciembre a las 4 pm en el salón comunal.'); await pg.wait_for_timeout(100)
        chk('CP-014 No sobrescribe lo que la persona editó', await pg.locator('#fp [name=lugar]').input_value()=='Casa de Rodolfo')
        chk('CP-014 Sí completa lo que no se editó', await pg.locator('#fp [name=fecha]').input_value()=='2026-12-03')
        await pg.locator('#x').click()
        await pg.click('#bImp'); await pg.click('#ej'); await pg.wait_for_timeout(150)
        n=await pg.locator('#res .imp').count(); txt=await pg.locator('#res').inner_text()
        chk('CP-016 Importar chat lista candidatos y destino', n>=2 and 'Va al calendario' in txt and 'Va a pendientes' in txt, txt[:200])
        await pg.locator('#fim button[type=submit]').click(); await pg.wait_for_timeout(150)
        await pg.click('#bImp'); await pg.click('#ej'); await pg.wait_for_timeout(150)
        txt=await pg.locator('#res').inner_text(); dis=await pg.locator('#res input:disabled').count()
        chk('CP-017 Chat ya importado no se puede marcar', 'Ya importado' in txt and dis>=2, txt[:200])
        await pg.locator('#x').click()
        await pg.evaluate("""()=>{const t=new Date();t.setDate(t.getDate()+5);const f=iso(t);
          S.eventos.push({id:uid(),titulo:'Reunión de equipo semanal',eje:'eq',fecha:f,ini:'18:30',fin:'19:30',lugar:''});
          S.pend.unshift({id:uid(),estado:'pendiente',de:'Prueba',tel:'',texto:'Reunión de prueba',titulo:'Reunión de prueba',tipo:'',org:'',persona:'',plazo:'',resumen:'',fecha:f,ini:'18:45',fin:'',lugar:'',recibido:new Date().toISOString()});save();render()}""")
        txt=await pg.locator('#listaPend').inner_text()
        chk('CP-024 Advierte el cruce de horario', 'Se cruza con «Reunión de equipo semanal» a las 6:30 p. m.' in txt)
        await pg.click('#bNew'); await pg.locator('#mt summary').click(); await pg.fill('#mtNuevo','correo-sin-arroba'); await pg.click('#mtAdd'); await pg.wait_for_timeout(100)
        chk('CP-027 Rechaza un correo inválido', 'no parece válido' in await pg.locator('#toast').inner_text() and await pg.locator('#mtLista input').count()==0)
        await pg.locator('#x').click()
        await pg.click('#tAsis'); await pg.fill('#chatIn','¿Qué hay esta semana?'); await pg.click('#chatForm button[type=submit]'); await pg.wait_for_timeout(300)
        chk('CP-032 Asistente sin clave pide la clave en Ajustes', 'Falta la clave en Ajustes' in await pg.locator('#msgs').inner_text())
        chk('Sin errores de JavaScript', not errs, errs)
        await b.close()
    print('APROBADAS',len(OK)); [print('  ✔',x) for x in OK]
    print('FALLIDAS',len(MAL)); [print('  ✘',x) for x in MAL]
    if os.path.exists(COPIA): os.remove(COPIA)
    sys.exit(1 if MAL else 0)
asyncio.run(main())

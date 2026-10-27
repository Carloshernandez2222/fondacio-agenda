# Fondacio · Agenda

Un calendario sencillo, parecido a Google Calendar, con una bandeja de **pendientes de WhatsApp**. Hecho para la fundación Fondacio (Altos de Cazucá) dentro de un trabajo de formación en habilidades digitales e inteligencia artificial.

## Qué hace

1. Se guarda un mensaje de WhatsApp (o un chat completo exportado) como **pendiente**. La página lee la fecha, la hora, el lugar, quién escribe, de qué grupo y a quién buscan.
2. Se decide: **aceptar**, **preguntar** o **rechazar**, con una respuesta ya escrita para WhatsApp.
3. Solo al aceptar, la actividad entra al **calendario** (vista de mes y de semana).
4. Al crear una actividad o al aceptar un pendiente se puede crear una **reunión en Google Meet**: eliges los correos de una lista, Google les manda la invitación y el link queda pegado en el mensaje de WhatsApp.
5. Una IA ayuda a leer los mensajes, a redactar respuestas e invitaciones y a contestar preguntas sobre la agenda.

## Cómo usarla

Abre `fondacio.html` en el navegador. No necesita instalación ni servidor.

Para activar la IA, entra a **Ajustes IA**, elige un proveedor (Groq, Gemini y OpenRouter tienen capa gratis) y pega tu clave. También puedes copiar `clave.example.js` como `clave.js` con tu clave, y la página la carga sola. `clave.js` está excluido del repositorio.

Las reuniones de Meet son la excepción: Google no permite iniciar sesión desde un archivo abierto con doble clic, así que para esa parte la página tiene que abrirse desde una dirección web (abajo está cómo).

## Reuniones en Google Meet

La página habla directo con Google Calendar desde el navegador, sin servidor propio. Cada persona inicia sesión con su cuenta de Google la primera vez y las reuniones se crean en **su** calendario, así que también le aparecen en Google Calendar como cualquier otro evento.

Lo que hace:

- **Crear reunión en Meet** crea el evento en Google Calendar con videollamada de Meet e invita a los correos marcados. Google les envía el correo de invitación.
- El link se guarda en la actividad. Aparece en la invitación para el grupo de WhatsApp, en la respuesta al aceptar un pendiente y en el detalle del día ("Unirse a Meet", "Copiar link", "Ver en Google Calendar").
- Si después cambias la fecha, la hora, el lugar o los invitados y guardas, el evento se actualiza en Google Calendar y se avisa a los invitados. Si guardas sin cambiar nada, no se les molesta.
- Si borras la actividad, rechazas el pendiente o deshaces la aceptación, la página pregunta si también se cancela la reunión en Google.
- Los correos que escribes quedan guardados para marcarlos la próxima vez. La × los quita de la lista.

El permiso de Google dura más o menos una hora. Cuando vence, al siguiente clic aparece una ventanita de Google que se cierra sola.

### Configuración (una sola vez, la hace quien administra la página)

**1. Proyecto y API**

1. Entra a [console.cloud.google.com](https://console.cloud.google.com) con la cuenta que va a administrar esto y crea un proyecto, por ejemplo "Fondacio Agenda".
2. En **APIs y servicios → Biblioteca** busca **Google Calendar API** y dale **Habilitar**.

**2. Pantalla de consentimiento** (en la consola aparece como **Google Auth Platform** o **Pantalla de consentimiento de OAuth**)

1. Dale **Comenzar**: nombre de la app ("Fondacio Agenda"), correo de soporte, público **Externo** y correo de contacto.
2. En **Público → Usuarios de prueba** agrega los correos de Gmail de todas las personas que van a usar la agenda (máximo 100). Mientras la app esté en modo de prueba solo esas cuentas pueden iniciar sesión.
3. En **Acceso a los datos** agrega el permiso `https://www.googleapis.com/auth/calendar.events`.

**3. ID de cliente**

1. En **Clientes** (o **Credenciales → Crear credenciales → ID de cliente de OAuth**) elige **Aplicación web**.
2. En **Orígenes autorizados de JavaScript** agrega las direcciones desde donde se va a abrir la página, sin ruta y sin `/` al final:
   - `http://localhost:5500` para probar en tu computador. (No uses el 8000: ahí suele correr `adk web` u otro servidor de FastAPI.)
   - `https://TU-USUARIO.github.io` si la publicas en GitHub Pages.
3. No hace falta llenar los URI de redireccionamiento. Crea el cliente y copia el **ID de cliente** (termina en `.apps.googleusercontent.com`). No es secreto.

**4. Ponerlo en la página**

Tienes dos opciones:

- **Para todos (recomendado al publicar):** en `fondacio.html` busca la línea `const GOOGLE_CLIENT_ID=window.GOOGLE_CLIENT_ID||"";`, pega el ID entre las últimas comillas y súbelo al repositorio. Así nadie tiene que configurar nada.
- **Solo en un navegador:** en **Ajustes IA → Google Calendar y Meet** pega el ID y guarda.

**5. Abrirla desde una dirección web**

- **Para probar en tu computador:** abre una terminal en la carpeta del proyecto y ejecuta `python -m http.server 5500`. Luego abre `http://localhost:5500/fondacio.html`. Tiene que ser `localhost`, no `127.0.0.1`, porque Google compara la dirección exacta.
- **Publicada:** en GitHub, **Settings → Pages → Deploy from a branch → main / (root)**. Queda en `https://TU-USUARIO.github.io/fondacio/fondacio.html`.

### Lo que va a ver cada persona la primera vez

Al dar "Crear reunión en Meet" se abre la ventana de Google para elegir la cuenta. Como la app no está verificada por Google, sale el aviso **"Google no ha verificado esta app"**: hay que dar clic en **Continuar** y luego aceptar el permiso del calendario. Esto pasa una sola vez por cuenta. Si el navegador bloquea la ventana, hay que permitir las ventanas emergentes para la página.

### Si algo falla

- **"Google Calendar API has not been used in project…"**: falta habilitar la API (paso 1).
- **"Error 400: redirect_uri_mismatch" u "origin_mismatch"**: la dirección desde donde abriste la página no está en los orígenes autorizados (paso 3).
- **"Acceso bloqueado: la app no completó el proceso de verificación"**: esa cuenta no está en los usuarios de prueba (paso 2).
- **Cuentas de una organización (Google Workspace):** el administrador puede tener bloqueadas las apps de terceros. En ese caso hay que pedirle que la permita.

## Datos

Se guardan en el navegador de cada persona. No se comparten entre dispositivos. Los mensajes y actividades de ejemplo no son reales. Las reuniones de Meet sí quedan en el Google Calendar de quien las crea.

## Estado

Beta. El mensaje o el chat se pega a mano: la lectura automática de WhatsApp es la siguiente fase.

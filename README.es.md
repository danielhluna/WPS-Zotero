# WPS-Zotero

Un complemento para WPS Writer que permite integrar Zotero como gestor de citas bibliográficas. Compatible con **GNU/Linux**, **Windows** y **macOS**.

WPS Office es una suite ofimática con excelente compatibilidad con MS Word. Para investigadores que migran de Windows a GNU/Linux, la falta de un procesador de texto con gestión de citas siempre ha sido un gran obstáculo. Con este complemento puedes insertar y editar citas en documentos creados con MS Word, o enviar documentos creados en WPS Writer a colaboradores que usen MS Word — ofreciendo una experiencia transparente en entornos donde el resto del equipo usa Windows y MS Office.

---

## Novedades en v0.2.0

**Compatibilidad con Zotero 7**

Zotero 9 introdujo nuevas medidas de seguridad que rompían la comunicación con el proxy en Linux:

- Corregido `NetworkError`: el proxy ahora prueba `127.0.0.1` (IPv4) y luego `localhost` (IPv6/`::1`) — en Linux, Zotero 7 puede escuchar únicamente en `::1`.
- Corregido `400 Bad Request`: el header `Host` ahora se reescribe a `localhost:23119`, requerido por la protección DNS rebinding de Zotero 7.
- Corregido `403 Forbidden`: se inyecta el header `zotero-allowed-request: 1` en todas las peticiones, necesario cuando el User-Agent empieza con `Mozilla/` (WPS usa un motor Chromium embebido).
- Corregido proxy que se detenía al reiniciar el sistema: `install.py` ahora registra el proxy como servicio del sistema (systemd en Linux, LaunchAgent en macOS, Programador de tareas en Windows).

**Interfaz multiidioma**

La barra de herramientas ahora soporta tres idiomas con detección automática y un menú desplegable para cambiar en cualquier momento:

- 🇬🇧 English
- 🇪🇸 Español
- 🇨🇳 中文

El idioma se detecta automáticamente desde la configuración de WPS y se guarda en disco para que persista entre sesiones.

---

## Requisitos

- [WPS Office](https://www.wps.com) (se recomienda la versión más reciente)
- [Zotero](https://www.zotero.org) con el plugin **Zotero LibreOffice Integration** instalado
- Python 3 — en Windows, asegúrate de marcar **"Agregar Python al PATH"** durante la instalación

---

## Instalación

Descarga **el repositorio** (los paquetes de release pueden estar desactualizados), descomprímelo, entra a la carpeta y ejecuta:

**Linux / macOS**
```bash
python3 install.py
```

**Windows**
```bash
python install.py
```

Para desinstalar:
```bash
# Linux / macOS
python3 install.py -u

# Windows
python install.py -u
```

En Windows puedes abrir una terminal presionando el botón Inicio y escribiendo `cmd`, luego usa `cd` para ir a la carpeta descomprimida, por ejemplo `cd D:\Descargas\WPS-Zotero`.

---

## ¿Cómo funciona?

El complemento usa la JSAPI de WPS para controlar WPS Writer y se comunica con Zotero a través de su [protocolo de integración HTTP](https://www.zotero.org/support/dev/client_coding/http_integration_protocol).

Debido a las [restricciones CORS de Zotero](https://groups.google.com/g/zotero-dev/c/MjWzJxaVoSs), las peticiones HTTP directas desde el cliente WPS son bloqueadas. Como solución, un proxy ligero escrito en Python (`proxy.py`) se ejecuta en segundo plano y reenvía las peticiones de WPS (puerto `21931`) a Zotero (puerto `23119`), añadiendo los headers CORS necesarios.

```
WPS Writer  ──►  proxy.py (:21931)  ──►  Zotero (:23119)
```

El proxy se registra como servicio del sistema durante la instalación, por lo que arranca automáticamente al iniciar sesión y se reinicia si falla.

---

## Cambiar el idioma

Haz clic en el menú desplegable **Idioma** en la pestaña Zotero de la barra de herramientas y selecciona tu idioma preferido. La selección se guarda automáticamente y se restaura la próxima vez que abras WPS.

---

## Compatibilidad con MS Word

Las citas se almacenan de forma compatible con MS Word. La única diferencia es que `formattedCitation` en los datos del campo usa formato XML en lugar de RTF (que usa MS Word). Zotero actualiza esto automáticamente, por lo que en la práctica no genera ningún problema.

Siempre almacena las citas como **campos** y no como marcadores — los marcadores no son compatibles con este complemento.

---

## Solución de problemas

**"Error de red, ¿está Zotero en ejecución?"**
Asegúrate de que Zotero esté abierto con el plugin **Zotero LibreOffice Integration** instalado. Si el error persiste, reinicia el proxy manualmente:
```bash
python3 proxy.py kill
python3 proxy.py &
```

**Algo salió mal durante una transacción de cita**
El servidor de Zotero puede quedar inactivo tras un error. Reinicia tanto Zotero como WPS Writer. Si el problema persiste, mata el proxy manualmente como se indica arriba y reinicia ambas aplicaciones.

**Registro del proxy**
El proxy escribe un archivo de log que puede ayudar a diagnosticar problemas:
```bash
# Linux / macOS
cat ~/.wps-zotero-proxy.log

# Windows
type %APPDATA%\kingsoft\wps\jsaddons\wps-zotero-proxy.log
```

---

## Problemas conocidos

**Windows — la ventana de Zotero no pasa al frente**
La ventana de citas de Zotero puede aparecer en segundo plano. Haz clic en el ícono de Zotero en la barra de tareas para traerla al frente. Este es [un bug conocido de Zotero](https://github.com/zotero/zotero-libreoffice-integration/issues/41). El instalador aplica una corrección automática en `prefs.js` para mitigar este problema.

**Windows — `wps.OAAssist.ShellExecute` puede no iniciar programas**
En algunas versiones de WPS para Windows, `ShellExecute` ya no puede lanzar programas locales (ver [#16](../../issues/16)). Como solución alternativa, inicia `proxy.py` manualmente haciendo doble clic, o usa la entrada del Programador de tareas creada por el instalador.

**Atajos de teclado**
Los atajos de teclado no están disponibles actualmente. En Windows puedes activar la cinta con `Alt-C` y luego las teclas de acceso (por ejemplo, `Alt-C` seguido de `C` para añadir/editar una cita). Esto no funciona en Linux ya que esa versión de WPS no soporta teclas de acceso en la cinta.

---

## Licencia

GPL-3.0 — ver [LICENSE](LICENSE). Este complemento se distribuye sin ninguna garantía.

**Autor original:** Tang, Kewei — [https://github.com/tankwyn/WPS-Zotero](https://github.com/tankwyn/WPS-Zotero)

**Cambios** por danielhluna - https://github.com/danielhluna/WPS-Zotero

**Colaboradores:** ver [pull requests](../../pulls) e [issues](../../issues).

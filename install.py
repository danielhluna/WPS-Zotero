#!/usr/bin/env python3
"""
install.py — WPS Zotero Addon Installer
Flujo: WPS (21931) ──► proxy.py (21931) ──► Zotero (23119)

Correcciones respecto al original:
  1. Puerto en XML corregido: 3889 → 21931 (donde proxy.py escucha).
  2. Proxy se registra como servicio del sistema para arrancar automáticamente:
       Linux   → systemd user service (~/.config/systemd/user/)
       macOS   → LaunchAgent (~~/Library/LaunchAgents/)
       Windows → Task Scheduler (schtasks)
  3. Bug en loop de perfiles Windows corregido (fn vs tmp).
  4. Soporte macOS en ADDON_PATH.
  5. stop_proxy seguro vía socket (no depende de import).
  6. Desinstalación también elimina el servicio del sistema.
"""

import os
import platform
import shutil
import sys
import re
import stat
import subprocess
import socket

# ──────────────────────────────────────────────────────────────
# Puertos
# ──────────────────────────────────────────────────────────────
PROXY_PORT  = 21931
ZOTERO_PORT = 23119

SYSTEM = platform.system()

# ──────────────────────────────────────────────────────────────
# Bloquear root en Linux
# ──────────────────────────────────────────────────────────────
if SYSTEM == 'Linux' and os.environ.get('USER') == 'root':
    print("Este addon no puede instalarse como root.", file=sys.stderr)
    sys.exit(1)

# ──────────────────────────────────────────────────────────────
# Rutas
# ──────────────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    PKG_PATH = os.path.dirname(sys.executable)
else:
    PKG_PATH = os.path.dirname(os.path.abspath(__file__))

VERSION = '0.1.2'
version_file = os.path.join(PKG_PATH, 'version.js')
if os.path.isfile(version_file):
    with open(version_file) as f:
        line = f.readline()
    m = re.search(r"['\"]([^'\"]+)['\"]", line)
    if m:
        VERSION = m.group(1)

APPNAME = f'wps-zotero_{VERSION}'

if SYSTEM == 'Darwin':
    ADDON_PATH = os.path.expanduser(
        '~/Library/Containers/com.kingsoft.wpsoffice.mac/Data/.kingsoft/wps/jsaddons'
    )
elif SYSTEM == 'Linux':
    ADDON_PATH = os.path.join(os.environ['HOME'], '.local/share/Kingsoft/wps/jsaddons')
else:
    ADDON_PATH = os.path.join(os.environ['APPDATA'], 'kingsoft', 'wps', 'jsaddons')

XML_PATHS = {
    'jsplugins':   os.path.join(ADDON_PATH, 'jsplugins.xml'),
    'publish':     os.path.join(ADDON_PATH, 'publish.xml'),
    'authwebsite': os.path.join(ADDON_PATH, 'authwebsite.xml'),
}

# Ruta final del proxy una vez instalado
PROXY_INSTALLED = os.path.join(ADDON_PATH, APPNAME, 'proxy.py')

# Nombres del servicio por plataforma
SERVICE_NAME_LINUX = 'wps-zotero-proxy'
SERVICE_NAME_MAC   = 'com.wps-zotero.proxy'
SERVICE_NAME_WIN   = 'WPS-Zotero-Proxy'

# ──────────────────────────────────────────────────────────────
# Helpers generales
# ──────────────────────────────────────────────────────────────
def del_rw(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)


def run(cmd, **kwargs):
    """Ejecuta un comando y devuelve (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs
    )
    return (result.returncode,
            result.stdout.decode(errors='replace').strip(),
            result.stderr.decode(errors='replace').strip())


def stop_proxy_safe():
    """Detiene el proxy enviando /stopproxy; ignora errores."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(('127.0.0.1', PROXY_PORT))
        s.send(b'POST /stopproxy HTTP/1.1\r\n\r\n')
        s.close()
        print('   Proxy detenido.')
    except Exception:
        pass


def check_zotero():
    """Avisa si Zotero no está corriendo (no bloqueante)."""
    try:
        with socket.create_connection(('127.0.0.1', ZOTERO_PORT), timeout=2):
            print(f'✅ Zotero detectado en el puerto {ZOTERO_PORT}.')
    except OSError:
        print(
            f'\n⚠️  Zotero no está corriendo en el puerto {ZOTERO_PORT}.\n'
            '   Abre Zotero antes de usar la extensión en WPS.\n'
        )


def register(fp, tagname, record):
    with open(fp) as f:
        content = f.read()
    pos = [m.end() for m in re.finditer(r'<' + tagname + r'>\s*', content)]
    if not pos:
        content += f'\n<{tagname}></{tagname}>'
        pos = [content.index(f'</{tagname}>')]
    i = pos[0]
    with open(fp, 'w') as f:
        f.write(content[:i] + record + os.linesep + content[i:])


# ──────────────────────────────────────────────────────────────
# Gestión del servicio — Linux (systemd user)
# ──────────────────────────────────────────────────────────────
def get_systemd_service_path():
    return os.path.expanduser(
        f'~/.config/systemd/user/{SERVICE_NAME_LINUX}.service'
    )


def install_service_linux():
    python  = sys.executable
    service = f"""[Unit]
Description=WPS Zotero Proxy
After=graphical-session.target

[Service]
ExecStart={python} {PROXY_INSTALLED}
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
"""
    service_path = get_systemd_service_path()
    os.makedirs(os.path.dirname(service_path), exist_ok=True)

    with open(service_path, 'w') as f:
        f.write(service)
    print(f'✅ Servicio systemd escrito en {service_path}')

    # Recargar, habilitar e iniciar
    for cmd in [
        ['systemctl', '--user', 'daemon-reload'],
        ['systemctl', '--user', 'enable', SERVICE_NAME_LINUX],
        ['systemctl', '--user', 'restart', SERVICE_NAME_LINUX],
    ]:
        code, out, err = run(cmd)
        if code != 0:
            print(f'⚠️  {" ".join(cmd)} falló: {err}')
        else:
            print(f'✅ {" ".join(cmd[2:])}')

    # Verificar que arrancó
    code, out, _ = run(['systemctl', '--user', 'is-active', SERVICE_NAME_LINUX])
    if out == 'active':
        print(f'✅ Proxy corriendo como servicio systemd.')
    else:
        print(f'⚠️  El servicio no está activo aún, estado: {out}')


def uninstall_service_linux():
    for cmd in [
        ['systemctl', '--user', 'stop',    SERVICE_NAME_LINUX],
        ['systemctl', '--user', 'disable', SERVICE_NAME_LINUX],
    ]:
        run(cmd)  # Ignorar errores si no existía

    service_path = get_systemd_service_path()
    if os.path.isfile(service_path):
        os.remove(service_path)
        print(f'   Servicio systemd eliminado.')
    run(['systemctl', '--user', 'daemon-reload'])


# ──────────────────────────────────────────────────────────────
# Gestión del servicio — macOS (LaunchAgent)
# ──────────────────────────────────────────────────────────────
def get_launchagent_path():
    return os.path.expanduser(
        f'~/Library/LaunchAgents/{SERVICE_NAME_MAC}.plist'
    )


def install_service_mac():
    python = sys.executable
    plist  = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{SERVICE_NAME_MAC}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python}</string>
        <string>{PROXY_INSTALLED}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{os.path.expanduser('~/.wps-zotero-proxy.log')}</string>
    <key>StandardErrorPath</key>
    <string>{os.path.expanduser('~/.wps-zotero-proxy.log')}</string>
</dict>
</plist>
"""
    plist_path = get_launchagent_path()
    os.makedirs(os.path.dirname(plist_path), exist_ok=True)

    with open(plist_path, 'w') as f:
        f.write(plist)
    print(f'✅ LaunchAgent escrito en {plist_path}')

    run(['launchctl', 'unload', plist_path])  # descargar si ya existía
    code, out, err = run(['launchctl', 'load', plist_path])
    if code != 0:
        print(f'⚠️  launchctl load falló: {err}')
    else:
        print('✅ LaunchAgent cargado — el proxy arrancará al iniciar sesión.')


def uninstall_service_mac():
    plist_path = get_launchagent_path()
    if os.path.isfile(plist_path):
        run(['launchctl', 'unload', plist_path])
        os.remove(plist_path)
        print('   LaunchAgent eliminado.')


# ──────────────────────────────────────────────────────────────
# Gestión del servicio — Windows (Task Scheduler)
# ──────────────────────────────────────────────────────────────
def install_service_windows():
    python = sys.executable.replace('python.exe', 'pythonw.exe')
    if not os.path.isfile(python):
        python = sys.executable

    # Eliminar tarea previa si existe
    run(['schtasks', '/Delete', '/TN', SERVICE_NAME_WIN, '/F'])

    code, out, err = run([
        'schtasks', '/Create',
        '/TN', SERVICE_NAME_WIN,
        '/TR', f'"{python}" "{PROXY_INSTALLED}"',
        '/SC', 'ONLOGON',          # al iniciar sesión
        '/RL', 'HIGHEST',          # privilegios más altos disponibles
        '/F',                      # forzar si ya existe
    ])
    if code != 0:
        print(f'⚠️  No se pudo crear la tarea programada: {err}')
    else:
        print('✅ Tarea programada creada — el proxy arrancará al iniciar sesión.')

    # Iniciar la tarea ahora mismo
    code, _, err = run(['schtasks', '/Run', '/TN', SERVICE_NAME_WIN])
    if code != 0:
        print(f'⚠️  No se pudo iniciar la tarea ahora: {err}')
    else:
        print('✅ Proxy iniciado.')


def uninstall_service_windows():
    run(['schtasks', '/End',    '/TN', SERVICE_NAME_WIN])
    run(['schtasks', '/Delete', '/TN', SERVICE_NAME_WIN, '/F'])
    print('   Tarea programada eliminada.')


# ──────────────────────────────────────────────────────────────
# Dispatchers multiplataforma
# ──────────────────────────────────────────────────────────────
def install_service():
    print('\n⚙️  Registrando proxy como servicio del sistema...')
    if SYSTEM == 'Linux':
        install_service_linux()
    elif SYSTEM == 'Darwin':
        install_service_mac()
    elif SYSTEM == 'Windows':
        install_service_windows()


def uninstall_service():
    print('   Eliminando servicio del sistema...')
    if SYSTEM == 'Linux':
        uninstall_service_linux()
    elif SYSTEM == 'Darwin':
        uninstall_service_mac()
    elif SYSTEM == 'Windows':
        uninstall_service_windows()


# ──────────────────────────────────────────────────────────────
# Desinstalación del addon
# ──────────────────────────────────────────────────────────────
def uninstall():
    print('🗑️  Desinstalando versiones previas...')
    stop_proxy_safe()
    uninstall_service()

    if not os.path.isdir(ADDON_PATH):
        print('   Directorio de addons no encontrado, nada que desinstalar.')
        return

    for x in os.listdir(ADDON_PATH):
        full = os.path.join(ADDON_PATH, x)
        if os.path.isdir(full) and 'wps-zotero' in x:
            print(f'   Eliminando {full}')
            shutil.rmtree(full, onerror=del_rw)

    for fp in XML_PATHS.values():
        if not os.path.isfile(fp):
            continue
        with open(fp) as f:
            xml = f.read()
        records = [(m.start(), m.end())
                   for m in re.finditer(r'[ \t]*<.*wps-zotero.*/>\s*', xml)]
        for r in reversed(records):
            print(f'   Eliminando entrada de {os.path.basename(fp)}')
            xml = xml[:r[0]] + xml[r[1]:]
        if records:
            with open(fp, 'w') as f:
                f.write(xml)


# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────
def main():
    uninstall()

    if len(sys.argv) > 1 and sys.argv[1] == '-u':
        print('✅ Desinstalación completa.')
        sys.exit(0)

    print(f'\n📦 Instalando {APPNAME}  (proxy :{PROXY_PORT} → Zotero :{ZOTERO_PORT})\n')

    check_zotero()

    # Crear directorio y XML base
    os.makedirs(ADDON_PATH, exist_ok=True)
    xml_defaults = {
        'jsplugins':   '<jsplugins>\n</jsplugins>\n',
        'publish':     '<?xml version="1.0" encoding="UTF-8"?>\n<jsplugins>\n</jsplugins>\n',
        'authwebsite': '<?xml version="1.0" encoding="UTF-8"?>\n<websites>\n</websites>\n',
    }
    for key, default in xml_defaults.items():
        fp = XML_PATHS[key]
        if not os.path.exists(fp):
            with open(fp, 'w') as f:
                f.write(default)

    # Copiar plugin
    dest = os.path.join(ADDON_PATH, APPNAME)
    if os.path.exists(dest):
        shutil.rmtree(dest, onerror=del_rw)
    shutil.copytree(PKG_PATH, dest)
    print(f'✅ Plugin copiado a {dest}')

    # Registrar en los tres XML
    proxy_url = f'http://127.0.0.1:{PROXY_PORT}/'
    register(
        XML_PATHS['jsplugins'], 'jsplugins',
        f'<jsplugin name="wps-zotero" type="wps" url="{proxy_url}" version="{VERSION}"/>'
    )
    register(
        XML_PATHS['publish'], 'jsplugins',
        f'<jsplugin url="{proxy_url}" type="wps" enable="enable_dev" install="null" version="{VERSION}" name="wps-zotero"/>'
    )
    register(
        XML_PATHS['authwebsite'], 'websites',
        '<website origin="null" name="wps-zotero" status="enable"/>'
    )
    print('✅ XML registrados correctamente.')

    # Fix ventana Zotero al frente (Windows)
    if SYSTEM == 'Windows':
        profiles_dir = os.path.join(
            os.environ['APPDATA'], 'Zotero', 'Zotero', 'Profiles'
        )
        if os.path.isdir(profiles_dir):
            for fn in os.listdir(profiles_dir):
                profile_path = os.path.join(profiles_dir, fn)
                prefs_file   = os.path.join(profile_path, 'prefs.js')
                if (os.path.isdir(profile_path)
                        and fn.endswith('.default')
                        and os.path.isfile(prefs_file)):
                    with open(prefs_file) as f:
                        content = f.read()
                    KEY = 'extensions.zotero.integration.keepAddCitationDialogRaised'
                    if KEY in content:
                        content = content.replace(
                            f'user_pref("{KEY}", false)',
                            f'user_pref("{KEY}", true);'
                        )
                    else:
                        content += f'\nuser_pref("{KEY}", true);\n'
                    with open(prefs_file, 'w') as f:
                        f.write(content)
                    print('✅ Preferencia de Zotero ajustada (ventana al frente).')

    # Registrar e iniciar el servicio del sistema
    install_service()

    print('\n🎉 ¡Instalación completa! Reinicia WPS para ver la pestaña Zotero.')
    print('   El proxy arrancará automáticamente al iniciar sesión.')
    print('   Para desinstalar: python3 install.py -u\n')


if __name__ == '__main__':
    main()

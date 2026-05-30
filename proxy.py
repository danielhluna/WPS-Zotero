#!/usr/bin/env python3
"""
proxy.py — WPS ↔ Zotero CORS proxy
Puerto escucha : PROXY_PORT  (21931)  ← WPS/zclient.js apunta aquí
Puerto destino : ZOTERO_PORT (23119)  ← Zotero escucha aquí

Cadena de bugs que causaba "Network error occurred, is Zotero running?":

  BUG A — IPv6 en Linux (causa raíz del NetworkError)
    Zotero 7 en Linux puede escuchar solo en ::1 (IPv6).
    El proxy intentaba conectar a 127.0.0.1 (IPv4) → ECONNREFUSED.
    on_accept() cerraba el forward socket pero dejaba el clientsock
    en input_list sin entrada en self.channels.
    Cuando llegaba la petición, on_recv() detectaba
    "s not in self.channels" → on_close(s) sin enviar ninguna
    respuesta HTTP → XHR recibía RST/FIN → lanzaba NetworkError.
    FIX: probar 127.0.0.1 y luego 'localhost' (que resuelve ::1 en Linux).
    FIX: si Zotero no responde, devolver 503 al cliente en lugar de
         cerrar la conexión en silencio.

  BUG B — Host header incorrecto (causaba 400 Bad Request)
    WPS manda Host: 127.0.0.1:21931.
    El proxy reescribía a Host: 127.0.0.1:23119.
    Zotero 7 valida que el Host sea exactamente 'localhost:23119'
    para prevenir ataques DNS rebinding → devolvía 400.
    FIX: reescribir Host a 'localhost:23119' siempre.

  BUG C — User-Agent Mozilla bloqueado (causaba 403 Forbidden)
    WPS es Chromium embebido → UA empieza con "Mozilla/5.0 ...".
    Zotero 7 bloquea cualquier UA que empiece con "Mozilla/" a menos
    que la petición incluya el header 'zotero-allowed-request: 1'.
    FIX: inyectar ese header en todas las peticiones hacia Zotero.

  BUG D — Estado compartido entre instancias (bug de clase vs instancia)
    input_list / channels / clients eran atributos de clase.
    FIX: moverlos a __init__ como atributos de instancia.

  BUG E — parse_head con split sin maxsplit
    Valores de header que contienen ': ' (ej. Authorization: Bearer a:b)
    se partían incorrectamente.
    FIX: split(': ', 1).
"""

import socket
import select
import time
import sys
import logging
import os
import atexit
import traceback
import errno


ZOTERO_PORT = 23119
PROXY_PORT  = 21931
BUFSIZE     = 4096
DELAY       = 0.0001

PREFLIGHT_HEADERS = {
    'Access-Control-Allow-Origin':      '*',
    'Access-Control-Allow-Methods':     'GET,POST,OPTIONS,PUT,PATCH,DELETE',
    'Access-Control-Allow-Headers':     '*',
    'Access-Control-Allow-Credentials': 'true',
}

# ──────────────────────────────────────────────────────────────────────────────
# Helpers HTTP
# ──────────────────────────────────────────────────────────────────────────────

def parse_head(hd_raw):
    """
    Devuelve (request_line, headers_dict).
    Usa split(': ', 1) para no romper valores que contienen ':'.
    Ignora líneas vacías.
    """
    lines   = hd_raw.decode('utf-8', errors='replace').split('\r\n')
    request = lines[0]
    headers = {}
    for line in lines[1:]:
        if ': ' in line:
            k, v = line.split(': ', 1)
            headers[k] = v
    return request, headers


def build_head(request_line, headers):
    """Reensambla request_line + headers en bytes."""
    lines = [request_line] + [f'{k}: {v}' for k, v in headers.items()] + ['', '']
    return '\r\n'.join(lines).encode('utf-8')


def recv_all(sock):
    """Lee una petición/respuesta HTTP completa del socket."""
    data   = b''
    closed = False

    while True:
        part = sock.recv(BUFSIZE)
        if not part:
            closed = True
            break
        data += part
        if b'\r\n\r\n' in data:
            break

    if not data:
        return data

    hd_raw = data.partition(b'\r\n\r\n')[0]
    req, headers = parse_head(hd_raw)

    if 'Content-Length' in headers:
        total = len(hd_raw) + 4 + int(headers['Content-Length'])
        while len(data) < total:
            part = sock.recv(BUFSIZE)
            if not part:
                break
            data += part
    elif not closed:
        if req.startswith('TRACE'):
            pass
        elif (data.startswith(b'OPTIONS')
              and 'Origin' in headers
              and 'Access-Control-Request-Method' in headers):
            pass
        else:
            while True:
                part = sock.recv(BUFSIZE)
                if not part:
                    break
                data += part

    return data


def make_503():
    """Respuesta 503 para devolver al cliente cuando Zotero no responde."""
    headers = {
        'Content-Type':                'text/plain',
        'Content-Length':              '36',
        'Access-Control-Allow-Origin': '*',
    }
    body = b'Zotero is not running or unreachable'
    return build_head('HTTP/1.0 503 Service Unavailable', headers) + body


# ──────────────────────────────────────────────────────────────────────────────
# Control remoto
# ──────────────────────────────────────────────────────────────────────────────

def stop_proxy():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('127.0.0.1', PROXY_PORT))
        s.send(b'POST /stopproxy HTTP/1.1\r\n\r\n')
    except Exception:
        pass
    finally:
        s.close()


# ──────────────────────────────────────────────────────────────────────────────
# Conexión robusta a Zotero (FIX A)
# ──────────────────────────────────────────────────────────────────────────────

def connect_to_zotero():
    """
    Intenta conectar a Zotero probando primero 127.0.0.1 (IPv4) y luego
    'localhost' (que en Linux con Zotero 7 puede resolver a ::1 / IPv6).
    Devuelve el socket conectado o None.
    """
    candidates = [
        ('127.0.0.1', ZOTERO_PORT, socket.AF_INET),
        ('localhost',  ZOTERO_PORT, socket.AF_UNSPEC),
    ]
    for host, port, family in candidates:
        try:
            if family == socket.AF_UNSPEC:
                # getaddrinfo resuelve tanto IPv4 como IPv6
                infos = socket.getaddrinfo(host, port,
                                           type=socket.SOCK_STREAM)
                for af, socktype, proto, _, addr in infos:
                    try:
                        s = socket.socket(af, socktype, proto)
                        s.connect(addr)
                        logging.info(f'Connected to Zotero via {host} ({addr})')
                        return s
                    except socket.error:
                        s.close()
            else:
                s = socket.socket(family, socket.SOCK_STREAM)
                s.connect((host, port))
                logging.info(f'Connected to Zotero via {host}')
                return s
        except socket.error as e:
            logging.debug(f'Cannot connect via {host}:{port} — {e}')

    logging.warning('Cannot connect to Zotero on any address. Is Zotero running?')
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Servidor proxy
# ──────────────────────────────────────────────────────────────────────────────

class ProxyServer:

    def __init__(self, host, port):
        # FIX D: atributos de instancia, no de clase
        self.input_list = []
        self.channels   = {}
        self.clients    = []

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if os.name == 'posix':
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen()
        self.running = False

    def run(self):
        self.input_list.append(self.server)
        self.running = True
        while self.running:
            time.sleep(DELAY)
            rlist, _, _ = select.select(self.input_list, [], [])
            for s in rlist:
                if s == self.server:
                    self.on_accept()
                    break
                data = recv_all(s)
                if not data:
                    self.on_close(s)
                    break
                else:
                    self.on_recv(s, data)

        for s in list(self.input_list):
            try:
                s.close()
            except Exception:
                pass
        self.input_list.clear()
        self.channels.clear()
        self.clients.clear()

    def on_accept(self):
        clientsock, clientaddr = self.server.accept()
        self.clients.append(clientaddr)
        self.input_list.append(clientsock)
        logging.info(f'{clientaddr} connected')

        # FIX A: conexión robusta IPv4/IPv6
        forward = connect_to_zotero()
        if forward is None:
            # FIX A: devolver 503 en lugar de cerrar en silencio
            # (evita que XHR lance NetworkError en zclient.js)
            try:
                clientsock.sendall(make_503())
            except Exception:
                pass
            # No cerramos clientsock aquí para no descartar comandos /stopproxy
            return

        self.input_list.append(forward)
        self.channels[clientsock] = forward
        self.channels[forward]    = clientsock

    def on_close(self, s):
        try:
            pname = s.getpeername()
        except Exception:
            pname = None
        if pname and pname in self.clients:
            self.clients.remove(pname)
        if s in self.channels:
            peer = self.channels[s]
            try:
                peer.close()
            except Exception:
                pass
            if peer in self.input_list:
                self.input_list.remove(peer)
            self.channels.pop(peer, None)
            self.channels.pop(s,    None)
        if s in self.input_list:
            self.input_list.remove(s)
        try:
            s.close()
        except Exception:
            pass
        logging.info(f'{pname} disconnected')

    def on_recv(self, s, data):
        logging.debug(f'data: {data[:200]}')

        # Comando de parada
        if data.startswith(b'POST /stopproxy'):
            logging.info('Stop command received')
            s.close()
            self.running = False
            return

        if s not in self.channels:
            self.on_close(s)
            return

        head_raw, _, body_raw = data.partition(b'\r\n\r\n')
        request, headers = parse_head(head_raw)

        try:
            peer = s.getpeername()
        except Exception:
            self.on_close(s)
            return

        if peer in self.clients:
            # ── Petición WPS → Zotero ─────────────────────────────────────
            logging.info(f'WPS→Zotero: {request}')

            # Preflight CORS: responder directamente
            if (data.startswith(b'OPTIONS')
                    and 'Origin' in headers
                    and 'Access-Control-Request-Method' in headers):
                headers.update(PREFLIGHT_HEADERS)
                s.sendall(build_head('HTTP/1.0 200 OK', headers) + body_raw)
                logging.info('Preflight response sent')
                return

            # FIX B: Zotero 7 exige Host: localhost:23119 (no 127.0.0.1)
            headers['Host'] = f'localhost:{ZOTERO_PORT}'

            # FIX C: Zotero 7 bloquea User-Agent Mozilla/* sin este header
            headers['zotero-allowed-request'] = '1'

            self.channels[s].send(build_head(request, headers) + body_raw)

        else:
            # ── Respuesta Zotero → WPS ────────────────────────────────────
            logging.info(f'Zotero→WPS: {request}')

            # CORS para que WPS pueda leer la respuesta
            headers['Access-Control-Allow-Origin'] = '*'
            # No reenviar el Host interno al cliente
            headers.pop('Host', None)

            self.channels[s].send(build_head(request, headers) + body_raw)

        logging.info(f'Forwarded to {self.channels[s].getpeername()}')


# ──────────────────────────────────────────────────────────────────────────────
# Entrypoint
# ──────────────────────────────────────────────────────────────────────────────

def main(argv):
    if os.name == 'posix':
        logfile = os.path.join(os.environ['HOME'], '.wps-zotero-proxy.log')
    else:
        logfile = os.path.join(
            os.environ['APPDATA'], 'kingsoft', 'wps', 'jsaddons',
            'wps-zotero-proxy.log'
        )

    if os.path.exists(logfile) and os.path.getsize(logfile) > 100 * 1024:
        os.remove(logfile)

    logging.basicConfig(
        filename=logfile,
        filemode='a',
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO,
    )

    if len(argv) < 2:
        try:
            server = ProxyServer('127.0.0.1', PROXY_PORT)
            logging.info('proxy started!')
            atexit.register(lambda: logging.info('proxy stopped!'))
            server.run()
        except Exception as e:
            if isinstance(e, socket.error) and e.errno == errno.EADDRINUSE:
                logging.warning('Port already in use — another instance may be running.')
                sys.exit()
            else:
                logging.error('Unexpected error:')
                logging.error(traceback.format_exc())
    elif argv[1] == 'kill':
        stop_proxy()


if __name__ == '__main__':
    main(sys.argv)

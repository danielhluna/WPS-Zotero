# WPS-Zotero

A WPS Writer add-on for integrating with Zotero. Supports **GNU/Linux**, **Windows** and **macOS**.

WPS is an office suite with excellent compatibility with MS Word. For scientific workers migrating from Windows to GNU/Linux, the lack of a good word processor with citation management has always been a great obstacle. With this add-on you can add and edit citations in documents created with MS Word, or send documents created with WPS Writer to others to edit in MS Word — providing a seamless experience for people who work in an environment where everyone else uses Windows and MS Word.

这个插件可以让你在Linux下写论文，再发给别人在Windows/MS Word下改，两边插入的引用可以共通（需要选择将引用存储为域）。**现在也支持Windows和macOS了**。喜欢的朋友点个星星，帮忙散播一下消息，帮助更多科研狗逃脱Windows/MS Office！

---

## What's new in v0.2.0

**Zotero 7 compatibility fixes**

Zotero 7 introduced several security measures that broke communication with the proxy on Linux:

- Fixed `NetworkError`: the proxy now tries `127.0.0.1` (IPv4) and then `localhost` (IPv6/`::1`) — on Linux, Zotero 7 may listen only on `::1`.
- Fixed `400 Bad Request`: the `Host` header is now rewritten to `localhost:23119` as required by Zotero 7's DNS rebinding protection.
- Fixed `403 Forbidden`: the header `zotero-allowed-request: 1` is now injected for all requests, required when the User-Agent starts with `Mozilla/` (WPS uses an embedded Chromium engine).
- Fixed proxy stopping after reboot: `install.py` now registers the proxy as a persistent system service (systemd on Linux, LaunchAgent on macOS, Task Scheduler on Windows).

**Multilanguage interface**

The ribbon UI now supports three languages with automatic detection and a dropdown menu to switch at any time:

- 🇬🇧 English
- 🇪🇸 Español
- 🇨🇳 中文

The language is detected automatically from WPS settings and saved to disk so it persists across sessions.

---

## Requirements

- [WPS Office](https://www.wps.com) (latest version recommended)
- [Zotero](https://www.zotero.org) with the **Zotero LibreOffice Integration** plugin installed
- Python 3 — on Windows, make sure to check **"Add Python to PATH"** during installation

---

## Installation

Download **the repository** (release packages may be outdated), unzip it, go into the folder and run:

**Linux / macOS**
```bash
python3 install.py
```

**Windows**
```bash
python install.py
```

To uninstall:
```bash
# Linux / macOS
python3 install.py -u

# Windows
python install.py -u
```

On Windows you can open a terminal by pressing the Start button and typing `cmd`, then use `cd` to navigate to the unzipped folder, for example `cd D:\Downloads\WPS-Zotero`.

安装方法：保证Python3安装好（**Windows上安装Python注意勾选添加到环境变量的选项**），下载源码包解压后执行 `install.py`。详细教程见 [这里](https://www.cnblogs.com/tkwblog/articles/17705935.html)。

---

## How does it work

This add-on uses WPS's JSAPI to control WPS Writer and communicates with Zotero through its [HTTP integration protocol](https://www.zotero.org/support/dev/client_coding/http_integration_protocol).

Due to [CORS restrictions in Zotero](https://groups.google.com/g/zotero-dev/c/MjWzJxaVoSs), direct HTTP requests from the WPS client are blocked. As a workaround, a lightweight Python proxy (`proxy.py`) runs in the background and forwards requests from WPS (port `21931`) to Zotero (port `23119`), adding the necessary CORS headers.

```
WPS Writer  ──►  proxy.py (:21931)  ──►  Zotero (:23119)
```

The proxy is registered as a system service during installation so it starts automatically on login and restarts if it crashes.

---

## Changing the language

Click the **Language / Idioma / 语言** dropdown in the Zotero ribbon tab and select your preferred language. The selection is saved automatically and will be restored the next time WPS starts.

---

## MS Word compatibility

Citations are stored in a way compatible with MS Word. The only difference is that `formattedCitation` in the field data uses XML format instead of RTF (which MS Word uses). Zotero updates this automatically, so it should not cause any issues in practice.

Always store citations as **fields** rather than bookmarks — bookmarks are not supported by this add-on.

---

## Troubleshooting

**"Network error occurred, is Zotero running?"**
Make sure Zotero is open with the **Zotero LibreOffice Integration** plugin installed. If the error persists, restart the proxy manually:
```bash
python3 proxy.py kill
python3 proxy.py &
```

**Something went wrong during a citation transaction**
The Zotero server may become unresponsive after an error. Restart both Zotero and WPS Writer. If the problem persists, kill the proxy manually as shown above and restart both applications.

**Proxy log**
The proxy writes a log file that can help diagnose issues:
```bash
# Linux / macOS
cat ~/.wps-zotero-proxy.log

# Windows
type %APPDATA%\kingsoft\wps\jsaddons\wps-zotero-proxy.log
```

---

## Known issues

**Windows — Zotero window not brought to front**
The Zotero citation window may sometimes appear in the background. Click the Zotero icon in the taskbar to bring it to the front. This is [a known Zotero bug](https://github.com/zotero/zotero-libreoffice-integration/issues/41). The installer applies an automatic fix for this in `prefs.js`.

**Windows — `wps.OAAssist.ShellExecute` may not start programs**
On some versions of WPS for Windows, `ShellExecute` can no longer launch local programs (see [#16](../../issues/16)). As a workaround, start `proxy.py` manually by double-clicking it, or use the Task Scheduler entry created by the installer.

**Shortcuts**
Keyboard shortcuts are not currently supported. On Windows you can activate the ribbon with `Alt-C` and then press the keytip letters (e.g. `Alt-C` then `C` to add/edit a citation). This does not work on Linux as that version of WPS does not support ribbon keytips.

---

## License

GPL-3.0 — see [LICENSE](LICENSE). This add-on comes with no warranty.

**Author:** Tang, Kewei — [https://github.com/tankwyn/WPS-Zotero](https://github.com/tankwyn/WPS-Zotero)

**Change** by danielhluna - https://github.com/danielhluna/WPS-Zotero

**Contributors:** see [pull requests](../../pulls) and [issues](../../issues).

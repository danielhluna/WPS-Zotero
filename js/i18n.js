/**
 * i18n.js — Internacionalización para WPS-Zotero
 * Idiomas soportados: en (English), es (Español), zh (中文)
 *
 * Almacenamiento: archivo lang.cfg en el directorio de instalación del addon.
 * (localStorage y prompt() no funcionan en el entorno WPS)
 */

const TRANSLATIONS = {

    en: {
        tab_label:              'Zotero',
        group_label:            'Zotero',
        btn_addEditCitation:    'Add/Edit Citation',
        btn_addEditBib:         'Add/Edit Refs',
        btn_refresh:            'Refresh',
        btn_pref:               'Preferences',
        btn_addNote:            'Add Note',
        btn_unlink:             'Unlink',
        btn_export:             'Export',
        btn_about:              'About',
        btn_lang:               'Language',

        tip_addEditCitation:    'Insert a new citation, or edit the citation at the current cursor position',
        tip_addEditBib:         'Insert a new bibliography, or edit the existing bibliography',
        tip_refresh:            'Update all citations to reflect changes',
        tip_pref:               'Change the citation style or locale',
        tip_addNote:            'Insert a new note at the current cursor position',
        tip_unlink:             'Remove all Zotero field codes and unlink from Zotero library',
        tip_export:             'Export the document to switch to another word processor',
        tip_about:              'About this add-on',
        tip_lang:               'Switch interface language / Cambiar idioma / 切换语言',

        err_network:            'Network error occurred, is Zotero running?',
        err_network_restart:    '\nYou will have to restart Zotero.',
        err_client:             'Client error',
        err_server:             'Server error',
        err_zotero_busy:        'Zotero is serving another program, restart it if this is not the case.',
        err_redirect:           'Received unexpected redirection message',
        err_generic:            'Error occurred {0}, please click dev tool, navigate to console and report the issue.',
        err_old_wps:            'You are using an old version of WPS, this plugin might not work properly!',

        dlg_export_confirm:     'Convert this document to a format for other word processors to import from? You may want to make a backup first.',
        dlg_about:              'WPS-Zotero ({0})\n\nThis add-on is licensed under GPL-3.0: <http://www.gnu.org/licenses/>, it comes with no warranty.\n\nAuthor: Tang, Kewei\nhttps://github.com/tankwyn/WPS-Zotero',
        dlg_lang_pick:          'Select language / Seleccionar idioma / 选择语言:\n\n1 - English\n2 - Español\n3 - 中文\n\nCurrent / Actual / 当前: {0}\n\nOK = English',
        dlg_lang_es:            'Español? (Cancel = no)',
        dlg_lang_zh:            '中文? (Cancel = no)',
        dlg_lang_changed:       'Language changed to English.\nRestart WPS to apply.',
    },

    es: {
        tab_label:              'Zotero',
        group_label:            'Zotero',
        btn_addEditCitation:    'Añadir/Editar Cita',
        btn_addEditBib:         'Añadir/Editar Refs',
        btn_refresh:            'Actualizar',
        btn_pref:               'Preferencias',
        btn_addNote:            'Añadir Nota',
        btn_unlink:             'Desvincular',
        btn_export:             'Exportar',
        btn_about:              'Acerca de',
        btn_lang:               'Idioma',

        tip_addEditCitation:    'Insertar una nueva cita o editar la cita en la posición actual del cursor',
        tip_addEditBib:         'Insertar una nueva bibliografía o editar la bibliografía existente',
        tip_refresh:            'Actualizar todas las citas para reflejar los cambios',
        tip_pref:               'Cambiar el estilo de cita o configuración regional',
        tip_addNote:            'Insertar una nueva nota en la posición actual del cursor',
        tip_unlink:             'Eliminar todos los códigos de campo de Zotero y desvincular de la biblioteca',
        tip_export:             'Exportar el documento para usar con otro procesador de texto',
        tip_about:              'Acerca de este complemento',
        tip_lang:               'Cambiar idioma / Switch language / 切换语言',

        err_network:            'Error de red, ¿está Zotero en ejecución?',
        err_network_restart:    '\nDeberás reiniciar Zotero.',
        err_client:             'Error del cliente',
        err_server:             'Error del servidor',
        err_zotero_busy:        'Zotero está sirviendo a otro programa, reinícialo si no es el caso.',
        err_redirect:           'Se recibió un mensaje de redirección inesperado',
        err_generic:            'Ocurrió un error {0}, abre las herramientas de desarrollo, ve a la consola y reporta el problema.',
        err_old_wps:            'Estás usando una versión antigua de WPS, ¡este complemento puede no funcionar correctamente!',

        dlg_export_confirm:     '¿Convertir este documento a un formato para importar en otro procesador de texto? Considera hacer una copia de seguridad primero.',
        dlg_about:              'WPS-Zotero ({0})\n\nEste complemento está licenciado bajo GPL-3.0: <http://www.gnu.org/licenses/>, sin garantía.\n\nAutor: Tang, Kewei\nhttps://github.com/tankwyn/WPS-Zotero',
        dlg_lang_pick:          'Seleccionar idioma / Select language / 选择语言:\n\n1 - English\n2 - Español\n3 - 中文\n\nActual / Current / 当前: {0}\n\nOK = English',
        dlg_lang_es:            '¿Español? (Cancelar = no)',
        dlg_lang_zh:            '¿中文? (Cancelar = no)',
        dlg_lang_changed:       'Idioma cambiado a {0}.\nReinicia WPS para aplicar.',
    },

    zh: {
        tab_label:              'Zotero',
        group_label:            'Zotero',
        btn_addEditCitation:    '添加/编辑引用',
        btn_addEditBib:         '添加/编辑参考文献',
        btn_refresh:            '刷新',
        btn_pref:               '首选项',
        btn_addNote:            '添加笔记',
        btn_unlink:             '取消链接',
        btn_export:             '导出',
        btn_about:              '关于',
        btn_lang:               '语言',

        tip_addEditCitation:    '在当前光标位置插入新引用或编辑引用',
        tip_addEditBib:         '在当前光标位置插入新参考文献列表或编辑现有列表',
        tip_refresh:            '更新所有引用以反映更改',
        tip_pref:               '更改引用样式或语言设置',
        tip_addNote:            '在当前光标位置插入新笔记',
        tip_unlink:             '删除所有 Zotero 域代码并与 Zotero 库断开链接',
        tip_export:             '导出文档以切换到其他文字处理器',
        tip_about:              '关于此插件',
        tip_lang:               '切换语言 / Switch language / Cambiar idioma',

        err_network:            '发生网络错误，Zotero 是否正在运行？',
        err_network_restart:    '\n您需要重新启动 Zotero。',
        err_client:             '客户端错误',
        err_server:             '服务器错误',
        err_zotero_busy:        'Zotero 正在为另一个程序服务，如果不是这种情况请重新启动。',
        err_redirect:           '收到意外的重定向消息',
        err_generic:            '发生错误 {0}，请打开开发工具，转到控制台并报告问题。',
        err_old_wps:            '您使用的是旧版 WPS，此插件可能无法正常工作！',

        dlg_export_confirm:     '将此文档转换为可供其他文字处理器导入的格式？建议先进行备份。',
        dlg_about:              'WPS-Zotero ({0})\n\n本插件遵循 GPL-3.0 许可证：<http://www.gnu.org/licenses/>，不提供任何保证。\n\n作者：Tang, Kewei\nhttps://github.com/tankwyn/WPS-Zotero',
        dlg_lang_pick:          '选择语言 / Select language / Seleccionar idioma:\n\n1 - English\n2 - Español\n3 - 中文\n\n当前 / Current / Actual: {0}\n\nOK = English',
        dlg_lang_es:            'Español? (取消 = 否)',
        dlg_lang_zh:            '中文? (取消 = 否)',
        dlg_lang_changed:       '语言已更改为 {0}。\n请重启 WPS 以应用更改。',
    }
};

// ─────────────────────────────────────────────────────────────
// Motor i18n
// ─────────────────────────────────────────────────────────────
const i18n = (function () {

    const SUPPORTED  = ['en', 'es', 'zh'];
    const FALLBACK   = 'en';
    const CFG_FILE   = 'lang.cfg';   // guardado en el directorio del addon

    // ── Persistencia en disco vía WPS FileSystem API ──────────
    function getCfgPath() {
        try {
            // GLOBAL_MAP.instDir se define en ribbon.js/OnAddinLoad
            if (typeof GLOBAL_MAP !== 'undefined' && GLOBAL_MAP.instDir) {
                const sep = GLOBAL_MAP.osSep || '/';
                return GLOBAL_MAP.instDir + sep + CFG_FILE;
            }
        } catch(e) {}
        return null;
    }

    function readFile(path) {
        try {
            // WPS expone wps.FileSystem para leer/escribir archivos
            const fs = wps.FileSystem;
            if (fs && fs.ReadAllText) {
                return fs.ReadAllText(path).trim();
            }
        } catch(e) {}
        return null;
    }

    function writeFile(path, content) {
        try {
            const fs = wps.FileSystem;
            if (fs && fs.WriteAllText) {
                fs.WriteAllText(path, content);
                return true;
            }
        } catch(e) {}
        return false;
    }

    function getSaved() {
        const path = getCfgPath();
        if (!path) return null;
        const val = readFile(path);
        return (val && SUPPORTED.includes(val)) ? val : null;
    }

    function saveLang(lang) {
        const path = getCfgPath();
        if (path) writeFile(path, lang);
    }

    // ── Detección automática del idioma de WPS ────────────────
    function detectWpsLang() {
        try {
            const raw = (wps.Env.GetLanguage() || '').toLowerCase();
            if (raw.startsWith('zh')) return 'zh';
            if (raw.startsWith('es')) return 'es';
            if (raw.startsWith('en')) return 'en';
        } catch (e) {}
        return null;
    }

    // Resolución: guardado en disco > WPS > fallback
    function resolve() {
        const saved = getSaved();
        if (saved) return saved;
        const wpsLang = detectWpsLang();
        if (wpsLang) return wpsLang;
        return FALLBACK;
    }

    let _current = resolve();

    return {
        getLang()  { return _current; },

        setLang(lang) {
            if (!SUPPORTED.includes(lang)) return;
            _current = lang;
            saveLang(lang);
        },

        /** Traduce una clave; {0}, {1}… se reemplazan por los argumentos */
        t(key, ...args) {
            const dict = TRANSLATIONS[_current] || TRANSLATIONS[FALLBACK];
            let str = dict[key] ?? TRANSLATIONS[FALLBACK][key] ?? key;
            args.forEach((arg, idx) => { str = str.replace(`{${idx}}`, arg); });
            return str;
        },

        /**
         * Reinicia la resolución del idioma.
         * Llamar después de que GLOBAL_MAP.instDir esté disponible
         * (es decir, al final de OnAddinLoad).
         */
        reload() {
            _current = resolve();
        },

        supported: SUPPORTED,
        langNames: { en: 'English', es: 'Español', zh: '中文' },
    };
})();

function t(key, ...args) { return i18n.t(key, ...args); }

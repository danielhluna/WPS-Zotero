// Shouldn't be needing this if using the latest version of WPS
const WPS_Enum = {
    msoCTPDockPositionLeft: 0,
    msoCTPDockPositionRight: 2,
    msoPropertyTypeString: 4,
    wdAlignParagraphJustify: 3,
    wdAlignTabLeft: 0,
    wdCharacter: 1,
    wdCollapseEnd: 0,
    wdCollapseStart: 1,
    wdFieldAddin: 81,
    wdLineBreak: 6,
    wdParagraph: 4
};

function zc_alert(msg) {
    alert(`WPS-Zotero: ${msg}`);
}

const GLOBAL_MAP = {};

/**
 * Refresca las etiquetas del ribbon según el idioma activo.
 */
function refreshRibbonLabels() {
    if (!wps.ribbonUI) return;
    const ids = [
        'zoteroTab', 'zoteroGroup',
        'btnAddEditCitation', 'btnAddEditBib', 'btnRefresh',
        'btnPref', 'btnAddNote', 'btnUnlink', 'btnExport',
        'btnAbout', 'menuLang',
        'btnLangEn', 'btnLangEs', 'btnLangZh'
    ];
    ids.forEach(id => {
        try { wps.ribbonUI.InvalidateControl(id); } catch(e) {}
    });
}

/**
 * Callback for plugin loading.
 */
function OnAddinLoad(ribbonUI) {
    if (typeof (wps.Enum) !== "object") {
        wps.Enum = WPS_Enum;
        zc_alert(t('err_old_wps'));
    }
    if (typeof (wps.ribbonUI) !== "object") {
        wps.ribbonUI = ribbonUI;
    }

    GLOBAL_MAP.isWin = Boolean(wps.Env.GetProgramDataPath());
    GLOBAL_MAP.osSep = GLOBAL_MAP.isWin ? '\\' : '/';
    GLOBAL_MAP.instDir = GLOBAL_MAP.isWin ?
        wps.Env.GetAppDataPath().replaceAll('/', '\\') + `\\kingsoft\\wps\\jsaddons\\wps-zotero_${VERSION}` :
        wps.Env.GetHomePath() + `/.local/share/Kingsoft/wps/jsaddons/wps-zotero_${VERSION}`;
    GLOBAL_MAP.proxyPath = GLOBAL_MAP.instDir + GLOBAL_MAP.osSep + 'proxy.py';

    // Recargar idioma desde disco ahora que instDir está disponible
    i18n.reload();
    refreshRibbonLabels();

    // Iniciar proxy
    if (GLOBAL_MAP.isWin) {
        wps.OAAssist.ShellExecute('pythonw.exe', GLOBAL_MAP.proxyPath);
    } else {
        wps.OAAssist.ShellExecute('python3', GLOBAL_MAP.proxyPath);
    }

    Application.ApiEvent.AddApiEventListener("ApplicationQuit", () => {
        postRequestXHR('http://127.0.0.1:21931/stopproxy', null);
    });

    return true;
}

/**
 * Callback for button clicking events.
 */
function OnAction(control) {
    const eleId = control.Id;
    switch (eleId) {
        case "btnAddEditCitation":
            zc_bind().command('addEditCitation');
            zc_clearRegistry();
            break;
        case "btnAddEditBib":
            zc_bind().command('addEditBibliography');
            zc_clearRegistry();
            break;
        case "btnRefresh":
            zc_bind().import();
            zc_bind().command('refresh');
            zc_clearRegistry();
            break;
        case "btnPref":
            zc_bind().command('setDocPrefs');
            zc_clearRegistry();
            break;
        case "btnExport":
            if (confirm(t('dlg_export_confirm'))) {
                zc_bind().export();
            }
            break;
        case "btnUnlink":
            zc_bind().command('removeCodes');
            zc_clearRegistry();
            break;
        case "btnAddNote":
            zc_bind().command('addNote');
            zc_clearRegistry();
            break;
        case "btnAbout":
            alert(t('dlg_about', VERSION));
            break;
        // Opciones del menú de idioma — selección directa, sin diálogos
        case "btnLangEn":
            applyLang('en');
            break;
        case "btnLangEs":
            applyLang('es');
            break;
        case "btnLangZh":
            applyLang('zh');
            break;
        default:
            break;
    }
    return true;
}

/**
 * Aplica el idioma seleccionado, refresca el ribbon y avisa al usuario.
 */
function applyLang(lang) {
    i18n.setLang(lang);
    refreshRibbonLabels();
    alert(t('dlg_lang_changed', i18n.langNames[lang]));
}

/**
 * Devuelve la etiqueta localizada de cada control del ribbon.
 */
function GetLabel(control) {
    const map = {
        zoteroTab:          t('tab_label'),
        zoteroGroup:        t('group_label'),
        btnAddEditCitation: t('btn_addEditCitation'),
        btnAddEditBib:      t('btn_addEditBib'),
        btnRefresh:         t('btn_refresh'),
        btnPref:            t('btn_pref'),
        btnAddNote:         t('btn_addNote'),
        btnUnlink:          t('btn_unlink'),
        btnExport:          t('btn_export'),
        btnAbout:           t('btn_about'),
        menuLang:           t('btn_lang'),
    };
    return map[control.Id] ?? control.Id;
}

/**
 * Devuelve el supertip localizado de cada botón.
 */
function GetSupertip(control) {
    const map = {
        btnAddEditCitation: t('tip_addEditCitation'),
        btnAddEditBib:      t('tip_addEditBib'),
        btnRefresh:         t('tip_refresh'),
        btnPref:            t('tip_pref'),
        btnAddNote:         t('tip_addNote'),
        btnUnlink:          t('tip_unlink'),
        btnExport:          t('tip_export'),
        btnAbout:           t('tip_about'),
        menuLang:           t('tip_lang'),
    };
    return map[control.Id] ?? '';
}

/**
 * Imágenes para los botones principales.
 */
function GetImage(control) {
    const map = {
        btnAddEditCitation: "images/addEditCitation.svg",
        btnAddEditBib:      "images/addEditBib.svg",
        btnRefresh:         "images/refresh.svg",
        btnPref:            "images/pref.svg",
        btnAddNote:         "images/addNote.svg",
        btnUnlink:          "images/unlink.svg",
        btnExport:          "images/export.svg",
        btnAbout:           "images/default.svg",
        menuLang:           "images/lang.svg",
    };
    return map[control.Id] ?? "images/default.svg";
}

/**
 * Imágenes para los items del menú de idioma.
 * Muestra una marca de verificación en el idioma activo.
 */
function GetImageLang(control) {
    const activeLang = i18n.getLang();
    const langMap = {
        btnLangEn: 'en',
        btnLangEs: 'es',
        btnLangZh: 'zh',
    };
    const isActive = langMap[control.Id] === activeLang;
    return isActive ? "images/lang_check.svg" : "images/lang_dot.svg";
}

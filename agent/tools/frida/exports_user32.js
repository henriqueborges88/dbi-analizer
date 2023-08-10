// Nome da DLL cujas funções queremos listar
var moduleName = 'user32.dll';

// Obter o módulo pelo nome
var module = Process.getModuleByName(moduleName);
if (module === null) {
    console.log('Módulo não encontrado: ' + moduleName);
    exit();
}

// Listar as exportações do módulo
Module.enumerateExports(module.name, {
    onMatch: function (exp) {
        send(`{ "name": "${exp.name}", "address": "${exp.address}" }`);
    },
    onComplete: function () {
        console.log('[Frida] Instrumentacao concluida.');
    }
});
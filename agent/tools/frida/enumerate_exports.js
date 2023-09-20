Process.enumerateModulesSync()
    .filter(function(m){ return m['path'].toLowerCase().indexOf('app') !=-1 ; })
    .forEach(function(m) {
        Module.enumerateExports(module.name, {
            onMatch: function (exp) {
                send(`{ "name": "${exp.name}", "address": "${exp.address}" }`);
            },
            onComplete: function () {
                console.log('[Frida] Instrumentacao concluida.');
            }
        });
    });
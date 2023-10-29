Process.enumerateModulesSync()
    .forEach(function(m) {
        Module.enumerateExports(m.name, {
            onMatch: function (exp) {
                send(`{ "name": "${exp.name}", "address": "${exp.address}" }`);
            },
            onComplete: function() {}
        });
    });
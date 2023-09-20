Process.enumerateModulesSync()
    .filter(function(m){ return m['path'].toLowerCase().indexOf('app') !=-1 ; })
    .forEach(function(m) {
        console.log(JSON.stringify(m, null, '  '));
        // to list exports use Module.enumerateExportsSync(m.name)
    });
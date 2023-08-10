function hookDispCall(moduleName) {
    hookFunction(moduleName, "DispCallFunc", {
      onEnter: function (args) {
        log("[+] DispCallFunc")
        var pvInstance = args[0]
        var oVft = args[1]
        var instance = ptr(ptr(pvInstance).readULong());
  
        log(' instance:' + instance);
        log(' oVft:' + oVft);
        var vftbPtr = instance.add(oVft)
        log(' vftbPtr:' + vftbPtr);
        var functionAddress = ptr(ptr(vftbPtr).readULong())
  
        loadModuleForAddress(functionAddress)
        var functionName = DebugSymbol.fromAddress(functionAddress)
  
        if (functionName) {
          log(' functionName:' + functionName);
        }
  
        dumpAddress(functionAddress);
  
        var currentAddress = functionAddress
        for (var i = 0; i < 10; i++) {
          try {
            var instruction = Instruction.parse(currentAddress)
            log(instruction.address + ': ' + instruction.mnemonic + ' ' + instruction.opStr)
            currentAddress = instruction.next
          } catch (err) {
            break
          }
        }
      }
    })
  }
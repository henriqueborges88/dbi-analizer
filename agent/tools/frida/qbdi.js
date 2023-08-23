var vm = new QBDI();
var state = vm.getGPRState();
vm.allocateVirtualStack(state, 0x1000000);
var funcPtr = Module.findExportByName(null, "RegCreateKeyA");
vm.addInstrumentedModuleFromAddr(funcPtr);
var icbk = vm.newInstCallback(function(vm, gpr, fpr, data) {
    var inst = vm.getInstAnalysis();
    // Display instruction dissassembly
    fmt = "0x" + inst.address.toString(16) + " " + inst.disassembly;
    console.log(fmt);
    send(fmt);
    return VMAction.CONTINUE;
});
vm.addCodeCB(InstPosition.PREINST, icbk);
vm.call(funcPtr, [42]);
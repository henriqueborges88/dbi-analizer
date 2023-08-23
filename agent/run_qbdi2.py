
import pyqbdi
import ctypes

def printInstruction(vm, gpr, fpr, data):
    inst = vm.getInstAnalysis()
    print("0x{} {}".format(inst.address, inst.disassembly))
    return pyqbdi.CONTINUE

def run():
    vm = pyqbdi.VM()
    state = vm.getGPRState()
    success, addr = pyqbdi.allocateVirtualStack(state, 0x100000)
    aLib = ctypes.cdll.LoadLibrary("aLib.so")
    funcPtr = ctypes.cast(aLib.aFunction, ctypes.c_void_p).value
    vm.addInstrumentedModuleFromAddr(funcPtr)
    vm.addCodeCB(pyqbdi.PREINST, printInstruction, None)
    vm.call(funcPtr, [42])
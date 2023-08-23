import pyqbdi

def printInstruction(vm, gpr, fpr, data):
    inst = vm.getInstAnalysis()
    print("0x{} {}".format(inst.address, inst.disassembly))
    return pyqbdi.CONTINUE

def main():
    executable_path = "user32.dll" #"C:\\Users\\henri\\OneDrive\\Documentos\\GitHub\\dbi-analizer\\agent\\in\\Autologon.exe"  # Substitua pelo caminho para o executável que deseja instrumentar
         
    # Crie uma instância do VM do PyQBDI
    vm = pyqbdi.VM()
    
    # create stack
    state = vm.getGPRState()
    addr = pyqbdi.allocateVirtualStack(state, 0x100000)
    assert addr is not None


    # Carregue o executável no PyQBDI
    add = vm.addInstrumentedModule(executable_path)
    vm.recordMemoryAccess(pyqbdi.MEMORY_READ_WRITE)
    
    # Registre o callback de instrumentação
    add_cb = vm.addCodeCB(pyqbdi.PREINST, printInstruction, None)
    
    # Execute a instrumentação no contexto do executável
    out = vm.run(0x0, 0xFFFFFFFF)
    print(out)
if __name__ == "__main__":
    main()

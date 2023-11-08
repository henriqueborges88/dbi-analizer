import json
from pathlib import Path
import sys
import vivisect
import os
from tool_runner_base import ToolRunner
from utils import ensure_directory_exists, log_error_file

class VivisectRunner(ToolRunner):
    def __init__(self, file_path, out):
        super().__init__(file_path, out)
        out_dir = os.path.join(out, "vivisect")
        self.out_dir = ensure_directory_exists(out_dir)

    @staticmethod
    @log_error_file
    def __run(file_path, out_dir):
        print("Executando Vivisect...")
        vw = vivisect.VivWorkspace(confdir="ws", autosave=True)
        vw.loadFromFile(file_path)
        res = vw.analyze()

        fcns = vw.getFunctions()
        fcns_detailed = []
        for fcn in fcns:
            fva = fcn
            fcn_detailed = {
                "getName": vw.getName(fva),
                "getFunctionApi": vw.getFunctionApi(fva),
                "getFunctionArgs": vw.getFunctionArgs(fva),
                "getFunctionBlocks": vw.getFunctionBlocks(fva),
                "getFunctionLocals": vw.getFunctionLocals(fva),
                "getFunctionMetaDict": vw.getFunctionMetaDict(fva),
            }
            fcns_detailed.append(fcn_detailed)
        analysis_result = {
            "Imports": vw.getImports(),
            "Exports": vw.getExports(),
            "Locations": vw.getLocations(),
            "Segments": vw.getSegments(),
            "PointerSize": vw.getPointerSize(),
            "LibraryDependancies": vw.getLibraryDependancies(),
            "Comments": vw.getComments(),
            "Endian": vw.getEndian(),
            "Relocations": vw.getRelocations(),
            "AnalysisModuleNames": vw.getAnalysisModuleNames(),
            "FuncAnalysisModuleNames": vw.getFuncAnalysisModuleNames(),
            "EntryPoints": vw.getEntryPoints(),
            "Stats": vw.getStats(),
            "DiscoveredInfo": vw.getDiscoveredInfo(),
            "Xrefs": vw.getXrefs(),
            "CodeBlocks": vw.getCodeBlocks(),
            "MemoryMaps": vw.getMemoryMaps(),
            "UserStructNames": vw.getUserStructNames(),
            "Names": vw.getNames(),
            "LocationDistribution": vw.getLocationDistribution(),
            "VaSetNames": vw.getVaSetNames(),
            "LeaderInfo": vw.getLeaderInfo(),
            "LeaderSessions": vw.getLeaderSessions(),
            "ColorMaps": vw.getColorMaps()
        }

        Files = vw.getFiles()
        FileMetaDict = vw.getFileMetaDict(Files[0])
        analysis_result.update({"FileMeta": FileMetaDict})
        # for VaSet in getVaSetNames:
        #     getVaSetDef = vw.getVaSetDef(VaSet)
        #     getVaSetRows = vw.getVaSetRows(VaSet)
        #     getVaSet = vw.getVaSet(VaSet)

        res_vivisect_path = os.path.join(out_dir, "vivisect.viv")
        res_vivisect_json_path = os.path.join(out_dir, "vivisect.json")

        vw.saveWorkspace(True, res_vivisect_path)
        with open(res_vivisect_json_path, "w") as file:
            json.dump(analysis_result, file)

        return res_vivisect_json_path, res_vivisect_path

    def run(self):
        return VivisectRunner.__run(self.file_path, self.out_dir)


def main():
    if len(sys.argv) < 3:
        print("Uso: python tool_vivisect.py <arquivo> <saída>")
        return 
    file = sys.argv[1]
    out = sys.argv[2]

    vivisect_runner = VivisectRunner(file, out)
    result_path = vivisect_runner.run()
    print(f"O resultado foi salvo no arquivo -> {result_path}")

if __name__ == "__main__":
    main()
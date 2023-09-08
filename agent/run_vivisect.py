import json
from pathlib import Path
import vivisect
import os

def run_vivisect(file_path, out):
    print("Executando Vivisect")

    out_dir = os.path.join(out, "die")
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    
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
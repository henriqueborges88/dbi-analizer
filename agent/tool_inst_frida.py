import os
import sys
from utils import wait_until_finish, instr_proc_task_kill, proc_kill_force
import frida
import json
from subprocess import Popen, PIPE
from time import sleep
from timer import Timer
from pathlib import Path
from tool_runner_base import ToolRunner
from utils import ensure_directory_exists, log_error_file

class FridaRunner(ToolRunner):
    def __init__(self, file_path, out):
        super().__init__(file_path, out)
        out_dir = os.path.join(out, "frida")
        self.out_dir = ensure_directory_exists(out_dir)

    @staticmethod
    @log_error_file
    def __run(file_path, out_dir):
        print("Executando Frida...")
        timer = Timer()
        timer.start()

        out_path = os.path.join(out_dir, "frida.json")
        instrumentation_errors = []
        functions_user32 = []
        frida_tool_path = os.path.abspath("./tools/frida/enumerate_exports.js") 
        file_name = os.path.basename(file_path)
        
        sample_proc = Popen(f"{file_path}", shell=True, stdout=PIPE, stderr=PIPE)
        sleep(2)
        try:
            session = frida.attach(sample_proc.pid)
        except frida.ProcessNotFoundError:
            print("Processo não encontrado. Certifique-se de que o processo esteja em execução.")
            return

        with open(frida_tool_path, "r") as file:
            script_code = file.read()
        script = session.create_script(script_code)

        # Cria um script Frida
        script = session.create_script(script_code)

        def on_destroyed(reason):
            print("Script finalizou:", reason)

        def on_message(message, data):
            if message['type'] == 'send':
                functions_user32.append(json.loads(message['payload']))
            elif message['type'] == 'error':
                instrumentation_errors.append(message['description'])

        script.on('message', on_message)
        script.on("destroyed", on_destroyed)
        script.load()
        
        wait_until_finish(sample_proc, timeout=5)
        sample_proc.terminate()
        sleep(1)
        
        instr_proc_task_kill(file_name)
        instr_proc_task_kill(file_name, True)
        proc_kill_force(sample_proc)
        
        session.detach()
        timer.stop()

        try:
            sample_out, sample_error = sample_proc.communicate()
            sample_out = sample_out.decode(errors='replace')
            sample_error = sample_error.decode(errors='replace')
            
            frida_dict = {
                "stdout": sample_out,
                "stderror": sample_error,
                "returncode": sample_proc.returncode,
                "has_error": sample_proc.returncode > 0 and False or True, # O instruction count envia a contagem para a saiída stderror, por tanto se a saída está vazía, a contagem falhou.
                "functions_user32": functions_user32,
                "instrumentation_errors": instrumentation_errors,
                "execution_time": str(timer.formatted_time()),
                "execution_timedelta": str(timer.as_timedelta())
            }
        except Exception as ex:
            frida_dict = {
                "stdout": "Tempo limite esgotado",
                "stderror": sample_error,
                "returncode": sample_proc.returncode,
                "has_error": sample_proc.returncode > 0 and False or True, # O instruction count envia a contagem para a saiída stderror, por tanto se a saída está vazía, a contagem falhou.
                "functions_user32": functions_user32,
                "instrumentation_errors": instrumentation_errors,
                "execution_time": str(timer.formatted_time()),
                "execution_timedelta": str(timer.as_timedelta())
            }

        print("[Frida] Instrumentação concluída")

        with open(out_path, 'w') as json_file:
            json.dump(frida_dict, json_file, sort_keys=False, indent=4)

        result_path = Path(out_path)
        return str(result_path)

    def run(self):
        return FridaRunner.__run(self.file_path, self.out_dir)


def main():
    if len(sys.argv) < 3:
        print("Uso: python tool_inst_frida.py <arquivo> <saída>")
        return 
    file = sys.argv[1]
    out = sys.argv[2]

    frida_runner = FridaRunner(file, out)
    result_path = frida_runner.run()
    print(f"O resultado foi salvo no arquivo -> {result_path}")

if __name__ == "__main__":
    main()

import os
import sys
from utils import wait_until_finish, task_kill, proc_kill_force
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
        functions = []
        frida_tool_path = os.path.abspath("./tools/frida/call_trace.js") # call_trace enumerate_exports
        file_name = os.path.basename(file_path)
        process = frida.spawn(file_path, stdio='pipe')
        try:
            session = frida.attach(process)
        except frida.ProcessNotFoundError:
            print("Processo não encontrado. Certifique-se de que o processo esteja em execução.")
            return
        with open(frida_tool_path, "r") as file:
            script_code = file.read()
        script = session.create_script(script_code)

        proc_finished = False
        def on_destroyed(reason):
            nonlocal proc_finished
            proc_finished = True

        def on_message(message, data):
            if message['type'] == 'send':
                functions.append(json.loads(message['payload']))
            elif message['type'] == 'error':
                print("Erro de instrumentação ->", message['description'])
                instrumentation_errors.append(message['description'])

        script.on('message', on_message)
        script.on("destroyed", on_destroyed)
        try:
            script.load()
        except Exception as ex:
            print("Erro ao carregar o script de intrumentação.", ex)
        sleep(3)
        frida.resume(process)
        
        proc_timeout = 20
        proc_time = 0
        while proc_finished == False and proc_time < proc_timeout:
            proc_time += 1
            sleep(1)

        frida.kill(process)
        session.detach()
        sleep(1)
        task_kill(file_name)
        task_kill(file_name, True)
        timer.stop()

        try:
            frida_dict = {
                "functions_call_trace": functions,
                "instrumentation_errors": instrumentation_errors,
                "execution_time": str(timer.formatted_time()),
                "execution_timedelta": str(timer.as_timedelta())
            }
        except Exception as ex:
            print("Não foi possivel salvar o resultado do frida.")

        print("[Frida] Instrumentação concluída")

        with open(out_path, 'w') as json_file:
            json.dump(frida_dict, json_file, sort_keys=False, indent=4)

        return out_path

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

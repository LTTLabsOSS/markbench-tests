"""3DMark test script"""
from argparse import ArgumentParser
import logging
from pathlib import Path
import subprocess
import sys
import time
import psutil
from utils import regex_find_score_in_xml, is_process_running, get_install_path

PARENT_DIR = str(Path(sys.path[0], ".."))
sys.path.append(PARENT_DIR)

from harness_utils.output import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json
)

#####
### Globals
#####
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR / "run"
DIR_PROCYON = Path(get_install_path())
EXECUTABLE = "ProcyonCmd.exe"
ABS_EXECUTABLE_PATH = DIR_PROCYON / EXECUTABLE
CONFIG_DIR = SCRIPT_DIR / "config"
BENCHMARK_CONFIG = {
    "All_Models_ONNX": {
        "config": f"\"{CONFIG_DIR}\\ai_textgeneration_all.def\"",
        "process_name":  "Handler.exe",
        "result_regex": r"<AIImageGenerationOverallScore>(\d+)",
        "test_name": "All LLM Model Text Generation"
    },
    "Llama_2_13B_ONNX": {
        "config": f"\"{CONFIG_DIR}\\ai_textgeneration_llama2.def\"",
        "process_name": "Handler.exe",
        "result_regex": r"<AiTextGenerationLlama2OverallScore>(\d+)",
        "test_name": "LLama 2 Text Generation"
    },
     "Llama_3_1_8B_ONNX": {
        "config": f"\"{CONFIG_DIR}\\ai_textgeneration_llama3.1.def\"",
        "process_name":  "Handler.exe",
        "result_regex": r"<AiTextGenerationLlama3OverallScore>(\d+)",
        "test_name": "Llama 3.1 Text Generation"
    },
    "Mistral_7B_ONNX": {
        "config": f"\"{CONFIG_DIR}\\ai_textgeneration_mistral.def\"",
        "process_name":  "Handler.exe",
        "result_regex": r"<AiTextGenerationMistralOverallScore>(\d+)",
        "test_name": "Mistral Text Generation"
    },
    "Phi_3_5_ONNX": {
        "config": f"\"{CONFIG_DIR}\\ai_textgeneration_phi.def\"",
        "process_name":  "Handler.exe",
        "result_regex": r"<AiTextGenerationPhiOverallScore>(\d+)",
        "test_name": "Phi Text Generation"
    },
    "All_Models_OPENVINO": {
        "config": f"\"{CONFIG_DIR}\\ai_textgeneration_all_openvino.def\"",
        "process_name":  "Handler.exe",
        "result_regex": r"<AIImageGenerationOverallScore>(\d+)",
        "test_name": "All LLM Model Text Generation"
    },
    "Llama_2_13B_OPENVINO": {
        "config": f"\"{CONFIG_DIR}\\ai_textgeneration_llama2_openvino.def\"",
        "process_name": "Handler.exe",
        "result_regex": r"<AiTextGenerationLlama2OverallScore>(\d+)",
        "test_name": "LLama 2 Text Generation"
    },
     "Llama_3_1_8B_OPENVINO": {
        "config": f"\"{CONFIG_DIR}\\ai_textgeneration_llama3.1_openvino.def\"",
        "process_name":  "Handler.exe",
        "result_regex": r"<AiTextGenerationLlama3OverallScore>(\d+)",
        "test_name": "Llama 3.1 Text Generation"
    },
    "Mistral_7B_OPENVINO": {
        "config": f"\"{CONFIG_DIR}\\ai_textgeneration_mistral_openvino.def\"",
        "process_name":  "Handler.exe",
        "result_regex": r"<AiTextGenerationMistralOverallScore>(\d+)",
        "test_name": "Mistral Text Generation"
    },
    "Phi_3_5_OPENVINO": {
        "config": f"\"{CONFIG_DIR}\\ai_textgeneration_phi_openvino.def\"",
        "process_name":  "Handler.exe",
        "result_regex": r"<AiTextGenerationPhiOverallScore>(\d+)",
        "test_name": "Phi Text Generation"
    }
}
RESULTS_FILENAME = "result.xml"
REPORT_PATH = LOG_DIR / RESULTS_FILENAME

def setup_logging():
    """setup logging"""
    setup_log_directory(LOG_DIR)
    logging.basicConfig(filename=LOG_DIR / "harness.log",
                        format=DEFAULT_LOGGING_FORMAT,
                        datefmt=DEFAULT_DATE_FORMAT,
                        level=logging.DEBUG)
    console = logging.StreamHandler()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def get_arguments():
    """get arguments"""
    parser = ArgumentParser()
    parser.add_argument(
        "--engine", dest="engine", help="Engine test type", required=True, choices=BENCHMARK_CONFIG.keys())
    argies = parser.parse_args()
    return argies


def create_procyon_command(test_option):
    """create command string"""
    command = f'\"{ABS_EXECUTABLE_PATH}\" --definition={test_option} --export=\"{REPORT_PATH}\"'
    command = command.rstrip()
    return command


def run_benchmark(process_name, command_to_run):
    """run the benchmark"""
    with subprocess.Popen(command_to_run, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) as proc:
        logging.info("Procyon AI Text Generation benchmark has started.")
        while True:
            now = time.time()
            elapsed = now - start_time
            if elapsed >= 60: #seconds
                raise ValueError("BenchMark subprocess did not start in time")
            process = is_process_running(process_name)
            if process is not None:
                process.nice(psutil.HIGH_PRIORITY_CLASS)
                break
            time.sleep(0.2)
        _, _ = proc.communicate() # blocks until 3dmark exits
        return proc

try:
    setup_logging()
    args = get_arguments()
    option = BENCHMARK_CONFIG[args.engine]["config"]
    cmd = create_procyon_command(option)
    logging.info('Starting benchmark!')
    logging.info(cmd)
    start_time = time.time()
    pr = run_benchmark(BENCHMARK_CONFIG[args.engine]["process_name"], cmd)

    if pr.returncode > 0:
        logging.error("Procyon exited with return code %d", pr.returncode)
        sys.exit(pr.returncode)

    end_time = time.time()
    elapsed_test_time = round(end_time - start_time, 2)

    if not args.engine == "All_Models_OPENVINO" and not args.engine == "All_Models_ONNX":
        results_regex = BENCHMARK_CONFIG[args.engine]["result_regex"]
        score = regex_find_score_in_xml(results_regex)

        if score is None:
            logging.error("Could not find overall score!")
            sys.exit(1)

        report = {
            "test": BENCHMARK_CONFIG[args.engine]["test_name"],
            "unit": "score",
            "score": score,
            "start_time": seconds_to_milliseconds(start_time),
            "end_time": seconds_to_milliseconds(end_time)
        }

        logging.info("Benchmark took %.2f seconds", elapsed_test_time)
        logging.info("Score was %s", score)

        write_report_json(LOG_DIR, "report.json", report)
    else:
        session_report = []

        logging.info("Benchmark took %.2f seconds", elapsed_test_time)

        for test_type in BENCHMARK_CONFIG.items():
            if test_type[0] == "All_Models_ONNX" or test_type[0] == "All_Models_OPENVINO":
                continue

            if ("ONNX" in args.engine and "ONNX" in test_type[0]) or ("OPENVINO" in args.engine and "OPENVINO" in test_type[0]):
                results_regex = test_type[1]["result_regex"]
                score = regex_find_score_in_xml(results_regex)

                logging.info("%s score was %s", test_type[0], score)

                if score is None:
                    logging.error("Could not find overall score!")
                    sys.exit(1)

                report = {
                    "test": test_type[0],
                    "unit": "score",
                    "score": score,
                    "start_time": seconds_to_milliseconds(start_time),
                    "end_time": seconds_to_milliseconds(end_time)
                }

                session_report.append(report)

        write_report_json(LOG_DIR, "report.json", session_report)

except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    sys.exit(1)

"""UL Procyon AI Text Generation test script"""

# pylint: disable=no-name-in-module
import logging
import subprocess
import sys
import time
from argparse import ArgumentParser
from pathlib import Path

import psutil
from procyon_ai_text_generation_utils import (
    find_procyon_version,
    find_test_version,
    get_install_path,
    is_process_running,
    regex_find_score_in_xml,
)

PARENT_DIR = str(Path(sys.path[0], ".."))
sys.path.append(PARENT_DIR)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.output import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
)

#####
# Globals
#####
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR / "run"
DIR_PROCYON = Path(get_install_path())
EXECUTABLE = "ProcyonCmd.exe"
ABS_EXECUTABLE_PATH = DIR_PROCYON / EXECUTABLE
CONFIG_DIR = SCRIPT_DIR / "config"
BENCHMARK_CONFIG = {
    "All_Models_ONNX": {
        "config": f'"{CONFIG_DIR}\\ai_textgeneration_all.def"',
        "process_name": "Handler.exe",
        "result_regex": r"<AIImageGenerationOverallScore>(\d+)",
        "test_name": "all_models",
        "api": "onnx",
    },
    "Llama_2_13B_ONNX": {
        "config": f'"{CONFIG_DIR}\\ai_textgeneration_llama2.def"',
        "process_name": "Handler.exe",
        "result_regex": r"<AiTextGenerationLlama2OverallScore>(\d+)",
        "test_name": "llama_2_13b",
        "api": "onnx",
    },
    "Llama_3_1_8B_ONNX": {
        "config": f'"{CONFIG_DIR}\\ai_textgeneration_llama3.1.def"',
        "process_name": "Handler.exe",
        "result_regex": r"<AiTextGenerationLlama3OverallScore>(\d+)",
        "test_name": "llama_3_1_8b",
        "api": "onnx",
    },
    "Mistral_7B_ONNX": {
        "config": f'"{CONFIG_DIR}\\ai_textgeneration_mistral.def"',
        "process_name": "Handler.exe",
        "result_regex": r"<AiTextGenerationMistralOverallScore>(\d+)",
        "test_name": "mistral_7b",
        "api": "onnx",
    },
    "Phi_3_5_ONNX": {
        "config": f'"{CONFIG_DIR}\\ai_textgeneration_phi.def"',
        "process_name": "Handler.exe",
        "result_regex": r"<AiTextGenerationPhiOverallScore>(\d+)",
        "test_name": "phi_3_5",
        "api": "onnx",
    },
    "All_Models_OPENVINO": {
        "config": f'"{CONFIG_DIR}\\ai_textgeneration_all_openvino.def"',
        "process_name": "Handler.exe",
        "result_regex": r"<AIImageGenerationOverallScore>(\d+)",
        "test_name": "all_models",
        "api": "openvino",
    },
    "Llama_2_13B_OPENVINO": {
        "config": f'"{CONFIG_DIR}\\ai_textgeneration_llama2_openvino.def"',
        "process_name": "Handler.exe",
        "result_regex": r"<AiTextGenerationLlama2OverallScore>(\d+)",
        "test_name": "llama_2_13b",
        "api": "openvino",
    },
    "Llama_3_1_8B_OPENVINO": {
        "config": f'"{CONFIG_DIR}\\ai_textgeneration_llama3.1_openvino.def"',
        "process_name": "Handler.exe",
        "result_regex": r"<AiTextGenerationLlama3OverallScore>(\d+)",
        "test_name": "llama_3_1_8b",
        "api": "openvino",
    },
    "Mistral_7B_OPENVINO": {
        "config": f'"{CONFIG_DIR}\\ai_textgeneration_mistral_openvino.def"',
        "process_name": "Handler.exe",
        "result_regex": r"<AiTextGenerationMistralOverallScore>(\d+)",
        "test_name": "mistral_7b",
        "api": "openvino",
    },
    "Phi_3_5_OPENVINO": {
        "config": f'"{CONFIG_DIR}\\ai_textgeneration_phi_openvino.def"',
        "process_name": "Handler.exe",
        "result_regex": r"<AiTextGenerationPhiOverallScore>(\d+)",
        "test_name": "phi_3_5",
        "api": "openvino",
    },
}

RESULTS_FILENAME = "result.xml"
RESULTS_XML_PATH = LOG_DIR / RESULTS_FILENAME


def setup_logging():
    """setup logging"""
    setup_log_directory(str(LOG_DIR))
    logging.basicConfig(
        filename=LOG_DIR / "harness.log",
        format=DEFAULT_LOGGING_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT,
        level=logging.DEBUG,
    )
    console = logging.StreamHandler()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)


def get_arguments():
    """get arguments"""
    parser = ArgumentParser()
    parser.add_argument(
        "--engine",
        dest="engine",
        help="Engine test type",
        required=True,
        choices=BENCHMARK_CONFIG.keys(),
    )
    argies = parser.parse_args()
    return argies


def create_procyon_command(test_option):
    """create command string"""
    command = f'"{ABS_EXECUTABLE_PATH}" --definition={test_option} --export="{RESULTS_XML_PATH}"'
    command = command.rstrip()
    return command


def run_benchmark(process_name, command_to_run):
    """run the benchmark"""
    with subprocess.Popen(
        command_to_run,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    ) as proc:
        logging.info("Procyon AI Text Generation benchmark has started.")
        while True:
            now = time.time()
            elapsed = now - start_time
            if elapsed >= 60:  # seconds
                raise ValueError("BenchMark subprocess did not start in time")
            process = is_process_running(process_name)
            if process is not None:
                process.nice(psutil.HIGH_PRIORITY_CLASS)
                break
            time.sleep(0.2)
        _, _ = proc.communicate()  # blocks until 3dmark exits
        return proc


try:
    setup_logging()
    args = get_arguments()
    option = BENCHMARK_CONFIG[args.engine]["config"]
    cmd = create_procyon_command(option)
    logging.info("Starting benchmark!")
    logging.info(cmd)
    start_time = time.time()
    pr = run_benchmark(BENCHMARK_CONFIG[args.engine]["process_name"], cmd)

    if pr.returncode > 0:
        logging.error("Procyon exited with return code %d", pr.returncode)
        sys.exit(pr.returncode)

    end_time = time.time()
    elapsed_test_time = round(end_time - start_time, 2)

    am = ArtifactManager(LOG_DIR)
    am.copy_file(RESULTS_XML_PATH, ArtifactType.RESULTS_TEXT, "results xml file")
    am.create_manifest()
    if (
        not args.engine == "All_Models_OPENVINO"
        and not args.engine == "All_Models_ONNX"
    ):
        results_regex = BENCHMARK_CONFIG[args.engine]["result_regex"]
        score = regex_find_score_in_xml(results_regex)

        if score is None:
            logging.error("Could not find overall score!")
            sys.exit(1)

        report = {
            "test": "Procyon AI Text Generation",
            "test_parameter": BENCHMARK_CONFIG[args.engine]["test_name"],
            "unit": "score",
            "score": score,
            "start_time": seconds_to_milliseconds(start_time),
            "end_time": seconds_to_milliseconds(end_time),
        }

        logging.info("Benchmark took %.2f seconds", elapsed_test_time)
        logging.info("Score was %s", score)

        write_report_json(str(LOG_DIR), "report.json", report)
    else:
        session_report = []

        logging.info("Benchmark took %.2f seconds", elapsed_test_time)

        for test_type in BENCHMARK_CONFIG.items():
            if (
                test_type[0] == "All_Models_ONNX"
                or test_type[0] == "All_Models_OPENVINO"
            ):
                continue

            if ("ONNX" in args.engine and "ONNX" in test_type[0]) or (
                "OPENVINO" in args.engine and "OPENVINO" in test_type[0]
            ):
                results_regex = test_type[1]["result_regex"]
                score = regex_find_score_in_xml(results_regex)

                logging.info("%s score was %s", test_type[0], score)

                if score is None:
                    logging.error("Could not find overall score!")
                    sys.exit(1)

                report = {
                    "start_time": seconds_to_milliseconds(start_time),
                    "end_time": seconds_to_milliseconds(end_time),
                    "test": "Procyon AI Text Generation",
                    "test_parameter": test_type[1]["test_name"],
                    "api": test_type[1]["api"],
                    "test_version": find_test_version(),
                    "procyon_version": find_procyon_version(),
                    "unit": "score",
                    "score": score,
                }

                session_report.append(report)

        write_report_json(str(LOG_DIR), "report.json", session_report)

except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    sys.exit(1)

import logging
import subprocess

logging.basicConfig(filename="logs/run.log", level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def run_script(script_name: str):
    try:
        logging.info(f"_____________{script_name} 데이터 수집을 시작합니다._____________")
        subprocess.run(["python", script_name])
    except Exception as e:
        logging.error(f"_____________{script_name} 데이터 수집 중 오류가 발생했습니다._____________")
        logging.error(e)
        logging.error("_____________________________________________________")


def main():
    run_script("get_naver_search_data.py")
    run_script("get_official_data.py")


if __name__ == "__main__":
    main()

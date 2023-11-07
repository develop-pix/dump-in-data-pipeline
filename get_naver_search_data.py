import json
import logging
import os
import time

import requests

logging.basicConfig(filename="logs/error.log", level=logging.ERROR)


def get_photo_booth_data(photo_booth: list, url: str, params: dict) -> list:
    places = []
    not_places = []
    photo_booth_category = ["사진,스튜디오", "셀프,대여스튜디오", "웨딩사진전문"]

    params["query"] = photo_booth
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return places, not_places

    try:
        first_data = response.json()
    except json.decoder.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON response for {photo_booth}: {e}")
        return places, not_places

    page_size = 20  # 한 페이지에 보여지는 데이터 수
    total_count = first_data["result"]["place"]["totalCount"]

    for i in range(total_count // page_size + 1):
        time.sleep(60 * 30)

        places_data = first_data["result"]["place"]["list"]

        # 첫 페이지 이후의 데이터를 가져오기 위해 추가 요청
        if i > 0:
            print(f"{photo_booth}, page:", i + 1)
            params["page"] = i + 1
            response = requests.get(url, params=params)

            try:
                places_data = response.json()["result"]["place"]["list"]
            except json.decoder.JSONDecodeError as e:
                logging.error(f"Failed to decode JSON response for {photo_booth}, page {i + 1}: {e}")
                continue

        for j in places_data:
            # 카테고리가 포토부스인 경우만 저장
            if any(item in j["category"] for item in photo_booth_category):
                context = {
                    "name": j["name"],
                    "operation_time": j["businessStatus"]["businessHours"],
                    "address": j["address"],
                    "road_address": j["roadAddress"],
                    "abbr_address": j["abbrAddress"],
                    "longitude": j["x"],
                    "latitude": j["y"],
                    "category": j["category"],
                    "home_page": j["homePage"],
                }

                # 포토부스 이름이 포함된 경우와 아닌 경우로 분리
                if photo_booth in j["name"]:
                    places.append(context)
                else:
                    not_places.append(context)

    return places, not_places


def save_data_to_file(photo_booth: list, places: list, not_places: list):
    directory_path = f"data/{photo_booth}"

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    with open(f"{directory_path}/{photo_booth}.json", "w", encoding="utf-8") as places_file:
        json.dump(places, places_file, ensure_ascii=False, indent=4)
    places_file.close()

    with open(f"{directory_path}/not_{photo_booth}.json", "w", encoding="utf-8") as not_places_file:
        json.dump(not_places, not_places_file, ensure_ascii=False, indent=4)
    not_places_file.close()

    print(f"{photo_booth} 데이터 수집 완료")


def run_naver_search_data_collection_script():
    requests_url = os.environ.get("NAVER_API_URL")

    photo_booths = [
        "포토시그니처",
        "포토인더박스",
        "포토하임",
        "폴라스튜디오",
        "하루필름",
        "픽닷",
        "인스포토",
        "인싸포토",
        "포토그레이",
        "포토스트리트",
        "포토아이브",
        "포토드링크",
        "포토랩플러스",
        "돈룩업",
        "그믐달 셀프 스튜디오",
        "비룸스튜디오",
        "모노맨션",
        "셀픽스",
        "스냅치즈",
        "스위치 스튜디오",
        "영카이브",
        "더필름",
        "무브먼트",
        "비키포토도쿄",
        "업텐션",
        "비키포토엘에이",
        "플랜비스튜디오",
        "808스튜디오",
        "샷업",
    ]

    params = {
        "query": None,
        "type": "all",
        "searchCoord": "127.10510576296453;37.3587808611674",  # 네이버 본사 좌표
        "page": 1,
    }

    for photo_booth in photo_booths:
        places, not_places = get_photo_booth_data(photo_booth, requests_url, params)
        save_data_to_file(photo_booth, places, not_places)


if __name__ == "__main__":
    run_naver_search_data_collection_script()

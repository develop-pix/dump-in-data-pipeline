import json
import os
import pprint

import requests
from dotenv import load_dotenv

load_dotenv()


def get_kakao_address(x: str, y: str) -> tuple:
    kakao_api_url = os.environ.get("KAKAO_API_URL")
    kakao_api_headers = {
        "Authorization": os.environ.get("KAKAO_API_KEY"),
        "content-type": "application/json;charset=UTF-8",
    }
    params = {"x": x, "y": y}
    response = requests.get(url=kakao_api_url, params=params, headers=kakao_api_headers)
    response_json = response.json()
    pprint.pprint(response_json)
    documents = response_json.get("documents")

    if documents and len(documents) > 0:
        road_address = documents[0].get("road_address", "")
        road_address_name = road_address.get("address_name", "") if road_address else ""
        building_name = road_address.get("building_name", "") if road_address else ""
        full_road_address_name = f"{road_address_name} {building_name}" if road_address_name else ""
        address = documents[0].get("address", "")
        address_name = address.get("address_name", "") if address else ""
    else:
        full_road_address_name = ""
        address_name = ""

    return full_road_address_name, address_name


def collect_photo_booth_data(photo_booth_data: list):
    name, url, form_data = photo_booth_data
    photo_booths_list = []
    directory_path = f"data/{name}"

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    photo_booths_response = requests.post(url=url, data={"board_code": form_data})
    map_data_array = [json.loads(json_str) for json_str in photo_booths_response.json()["map_data_array"]]

    for map_data in map_data_array:
        full_road_address_name, address_name = get_kakao_address(map_data["pos_x"], map_data["pos_y"])

        photo_booths_dict = {
            "name": name,
            "road_address": full_road_address_name,
            "address": address_name,
            "longitude": map_data["pos_x"],
            "latitude": map_data["pos_y"],
            "category_code": map_data["category_code"],
        }

        photo_booths_list.append(photo_booths_dict)

    with open(f"{directory_path}/{name}.json", "w", encoding="utf-8") as photo_booths_file:
        json.dump(photo_booths_list, photo_booths_file, ensure_ascii=False, indent=4)

    print(f"{name} 데이터 수집 완료")


def run_photo_booth_data_collection_script():
    photo_booths_url_datas = [
        ["인생네컷", "https://lifefourcuts.com/ajax/get_map_data.cm", "b20210114da9a94d63009f"],
        ["포토매틱", "https://www.photomatic.co.kr/ajax/get_map_data.cm", "b2020092011f9db9d68a55"],
        ["포토이즘 스튜디오", "https://photoism.co.kr/ajax/get_map_data.cm", "b2022071245de025e336e7"],
        ["포토이즘 박스", "https://photoism.co.kr/ajax/get_map_data.cm", "b202207139aa9cbd453ce3"],
        ["포토이즘 컬러드", "https://photoism.co.kr/ajax/get_map_data.cm", "b20220713ca5a26fde77a4"],
        ["플레이인더박스", "https://www.playinthebox.co.kr/ajax/get_map_data.cm", "b20221207ef9c61e33e4e7"],
    ]

    for photo_booths_url_data in photo_booths_url_datas:
        collect_photo_booth_data(photo_booths_url_data)


if __name__ == "__main__":
    run_photo_booth_data_collection_script()

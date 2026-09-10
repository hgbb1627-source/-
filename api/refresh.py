# -*- coding: utf-8 -*-
import os
import re
import json
import datetime
import urllib.request
from http.server import BaseHTTPRequestHandler
from bs4 import BeautifulSoup

# 11개 대상 전형 설정 (의약학 계열: 핵심 6 + 모니터링 5)
# ※ auto_fetch_competition.py의 UNIV_CONFIGS와 반드시 동일하게 유지할 것 (두 파일에 중복 정의됨)
UNIV_CONFIGS = [
    {
        "category": "지원 1",
        "alias": "전북대-지역의사전주권",
        "sheet": "전북대_지역의사전주권",
        "univ_name": "전북대학교",
        "admission": "학생부교과 지역의사선발전형-전주권",
        "major": "의예과",
        "quota": 9,
        "prev_year": "데이터 없음",
        "min_5yr": "데이터 없음",
        "avg_5yr": "데이터 없음",
        "url": "https://ratio.uwayapply.com/Sl5KOldCL0pmJSY6Jko3ZlRm",
        "enc": "euc-kr",
        "type": "uway",
        "target_admission_match": "지역의사선발전형-전주권",
        "target_major_match": "의예과"
    },
    {
        "category": "지원 2",
        "alias": "전북대-지역인재2전북권",
        "sheet": "전북대_지역인재2전북권",
        "univ_name": "전북대학교",
        "admission": "학생부교과 지역인재2전형-전북권",
        "major": "의예과",
        "quota": 45,
        "prev_year": "데이터 없음",
        "min_5yr": "데이터 없음",
        "avg_5yr": "데이터 없음",
        "url": "https://ratio.uwayapply.com/Sl5KOldCL0pmJSY6Jko3ZlRm",
        "enc": "euc-kr",
        "type": "uway",
        "target_admission_match": "지역인재2전형-전북권",
        "target_major_match": "의예과"
    },
    {
        "category": "지원 3",
        "alias": "가천대-의예과",
        "sheet": "가천대_의예과",
        "univ_name": "가천대학교",
        "admission": "가천의약학전형",
        "major": "의예과",
        "quota": 16,
        "prev_year": "데이터 없음",
        "min_5yr": "데이터 없음",
        "avg_5yr": "데이터 없음",
        "url": "https://addon.jinhakapply.com/RatioV1/RatioH/Ratio10190711.html",
        "enc": "utf-8",
        "type": "jinhak",
        "target_admission_match": "가천의약학전형",
        "target_major_match": "의예과"
    },
    {
        "category": "지원 4",
        "alias": "원광대-의약학치의예과",
        "sheet": "원광대_의약학치의예과",
        "univ_name": "원광대학교",
        "admission": "지역인재종합전형(전북)",
        "major": "의약학 치의예과 (자연)",
        "quota": 18,
        "prev_year": "데이터 없음",
        "min_5yr": "데이터 없음",
        "avg_5yr": "데이터 없음",
        "url": "https://ratio.uwayapply.com/Sl5Kclc4TjlXYU5KZiUmOiZKN2ZUZg==",
        "enc": "euc-kr",
        "type": "uway",
        "target_admission_match": "지역인재종합전형",
        "target_major_match": "치의예과"
    },
    {
        "category": "지원 5",
        "alias": "성균관대-약학과",
        "sheet": "성균관대_약학과",
        "univ_name": "성균관대학교",
        "admission": "학생부종합(융합인재)",
        "major": "약학과",
        "quota": 10,
        "prev_year": "데이터 없음",
        "min_5yr": "데이터 없음",
        "avg_5yr": "데이터 없음",
        "url": "https://addon.jinhakapply.com/RatioV1/RatioH/Ratio10920591.html",
        "enc": "utf-8",
        "type": "jinhak",
        "target_admission_match": "융합인재",
        "target_major_match": "약학과"
    },
    {
        "category": "지원 6",
        "alias": "한양대ERICA-약학과",
        "sheet": "한양대ERICA_약학과",
        "univ_name": "한양대학교(ERICA)",
        "admission": "학생부종합(서류형)",
        "major": "약학과",
        "quota": 15,
        "prev_year": "데이터 없음",
        "min_5yr": "데이터 없음",
        "avg_5yr": "데이터 없음",
        "url": "https://addon.jinhakapply.com/RatioV1/RatioH/Ratio11650731.html",
        "enc": "utf-8",
        "type": "jinhak",
        "target_admission_match": "서류형",
        "target_major_match": "약학과"
    },
    {
        "category": "기타",
        "alias": "전북대-지역인재2유형",
        "sheet": "전북대_지역인재2유형",
        "univ_name": "전북대학교",
        "admission": "학생부종합 지역인재2유형전형-전북권",
        "major": "의예과",
        "quota": 4,
        "prev_year": "데이터 없음",
        "min_5yr": "데이터 없음",
        "avg_5yr": "데이터 없음",
        "url": "https://ratio.uwayapply.com/Sl5KOldCL0pmJSY6Jko3ZlRm",
        "enc": "euc-kr",
        "type": "uway",
        "target_admission_match": "지역인재2유형전형-전북권",
        "target_major_match": "의예과"
    },
    {
        "category": "기타",
        "alias": "전북대-지역의사광역권",
        "sheet": "전북대_지역의사광역권",
        "univ_name": "전북대학교",
        "admission": "학생부교과 지역의사선발전형-광역권",
        "major": "의예과",
        "quota": 6,
        "prev_year": "데이터 없음",
        "min_5yr": "데이터 없음",
        "avg_5yr": "데이터 없음",
        "url": "https://ratio.uwayapply.com/Sl5KOldCL0pmJSY6Jko3ZlRm",
        "enc": "euc-kr",
        "type": "uway",
        "target_admission_match": "지역의사선발전형-광역권",
        "target_major_match": "의예과"
    },
    {
        # ⚠️ 원본 데이터에 모집단위(학과)가 명시되지 않아 "의예과"로 추정. 실제와 다르면 major/target_major_match 수정 필요.
        "category": "기타",
        "alias": "원광대-지역의사전주권",
        "sheet": "원광대_지역의사전주권",
        "univ_name": "원광대학교",
        "admission": "지역의사선발전형 진료권-전주권",
        "major": "의예과 (추정)",
        "quota": 7,
        "prev_year": "데이터 없음",
        "min_5yr": "데이터 없음",
        "avg_5yr": "데이터 없음",
        "url": "https://ratio.uwayapply.com/Sl5Kclc4TjlXYU5KZiUmOiZKN2ZUZg==",
        "enc": "euc-kr",
        "type": "uway",
        "target_admission_match": "지역의사선발전형",
        "target_major_match": "의예과"
    },
    {
        # ⚠️ 원본 데이터에 모집단위(학과)가 명시되지 않아 "의예과"로 추정. 실제와 다르면 major/target_major_match 수정 필요.
        "category": "기타",
        "alias": "원광대-지역의사광역권",
        "sheet": "원광대_지역의사광역권",
        "univ_name": "원광대학교",
        "admission": "지역의사선발전형 진료권-광역권",
        "major": "의예과 (추정)",
        "quota": 4,
        "prev_year": "데이터 없음",
        "min_5yr": "데이터 없음",
        "avg_5yr": "데이터 없음",
        "url": "https://ratio.uwayapply.com/Sl5Kclc4TjlXYU5KZiUmOiZKN2ZUZg==",
        "enc": "euc-kr",
        "type": "uway",
        "target_admission_match": "지역의사선발전형",
        "target_major_match": "의예과"
    },
    {
        "category": "기타",
        "alias": "가천대-약학과",
        "sheet": "가천대_약학과",
        "univ_name": "가천대학교",
        "admission": "가천의약학전형",
        "major": "약학과",
        "quota": 10,
        "prev_year": "데이터 없음",
        "min_5yr": "데이터 없음",
        "avg_5yr": "데이터 없음",
        "url": "https://addon.jinhakapply.com/RatioV1/RatioH/Ratio10190711.html",
        "enc": "utf-8",
        "type": "jinhak",
        "target_admission_match": "가천의약학전형",
        "target_major_match": "약학과"
    }
]

def parse_time_from_soup(soup):
    pattern = r'(\d{4})[-\.년]\s*(\d{1,2})[-\.월]\s*(\d{1,2})[일\.]?\s*(오전|오후)?\s*(\d{1,2})[:시]\s*(\d{1,2})'
    for s in soup.stripped_strings:
        m = re.search(pattern, s)
        if m:
            y, mo, d, ampm, hh, mm = m.groups()
            hh, mm = int(hh), int(mm)
            if ampm == "오후" and hh < 12:
                hh += 12
            elif ampm == "오전" and hh == 12:
                hh = 0
            date_obj = datetime.date(int(y), int(mo), int(d))
            time_obj = datetime.time(hh, mm)
            return date_obj, time_obj
    return None, None

def fetch_single(cfg):
    req = urllib.request.Request(
        cfg["url"],
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            raw = resp.read()
            try:
                html = raw.decode(cfg["enc"])
            except Exception:
                html = raw.decode("euc-kr", errors="replace")
            soup = BeautifulSoup(html, "html.parser")
            date_obj, time_obj = parse_time_from_soup(soup)

            target_adm = cfg["target_admission_match"]
            target_maj = cfg["target_major_match"]
            matched_row = None

            for table in soup.find_all("table"):
                headers = []
                curr = table
                while curr and len(headers) < 4:
                    curr = curr.find_previous(["h1", "h2", "h3", "h4", "caption", "div", "span", "p"])
                    if curr:
                        t = curr.get_text().strip()
                        if any(k in t for k in ["전형", "모집", "현황", "경쟁률"]) and len(t) < 60:
                            headers.append(t)
                header_text = " ".join(headers)

                if target_adm and target_adm not in header_text:
                    table_first_col = " ".join(
                        [tr.find(["td", "th"]).get_text() for tr in table.find_all("tr") if tr.find(["td", "th"])]
                    )
                    if target_adm not in table_first_col:
                        continue

                for tr in table.find_all("tr"):
                    cells = [td.get_text().strip() for td in tr.find_all(["td", "th"])]
                    row_str = " ".join(cells)
                    if target_maj in row_str:
                        nums = [c for c in cells if c.isdigit()]
                        if len(nums) >= 2:
                            q_str = str(cfg["quota"])
                            if q_str in cells:
                                q_idx = cells.index(q_str)
                            else:
                                q_idx = cells.index(nums[-2])
                            
                            if q_idx + 1 < len(cells) and cells[q_idx + 1].isdigit():
                                app = int(cells[q_idx + 1])
                                rate_str = cells[q_idx + 2] if q_idx + 2 < len(cells) else f"{app / cfg['quota']:.2f} : 1"
                                matched_row = {
                                    "applicants": app,
                                    "rate_str": rate_str
                                }
                                break
                if matched_row:
                    break

            if matched_row:
                return {
                    "date": date_obj or datetime.date.today(),
                    "time": time_obj or datetime.time(datetime.datetime.now().hour, 0),
                    "applicants": matched_row["applicants"],
                    "rate_str": matched_row["rate_str"]
                }
    except Exception:
        pass
    return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. 기존 records.json 로드
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_dir, "data", "records.json")
        
        fallback_data = {"universities": []}
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    fallback_data = json.load(f)
            except Exception:
                pass

        univ_dict = {u["alias"]: u for u in fallback_data.get("universities", [])}

        # 2. 실시간 크롤링 수행
        latest_time_str = fallback_data.get("updated_at", "10:00").split()[-1]
        
        for cfg in UNIV_CONFIGS:
            alias = cfg["alias"]
            live_res = fetch_single(cfg)
            if live_res:
                cur_app = live_res["applicants"]
                cur_rate = round(cur_app / cfg["quota"], 2)
                t_str = live_res["time"].strftime("%H:%M")
                d_str = live_res["date"].strftime("%Y-%m-%d")

                if t_str > latest_time_str:
                    latest_time_str = t_str

                # 전년도 경쟁률 데이터가 없으면(예: "데이터 없음") 진행률을 계산하지 않고 None 처리
                progress_pct = None
                if ":" in cfg["prev_year"]:
                    prev_yr_num = float(cfg["prev_year"].split(":")[0].strip())
                    if prev_yr_num > 0:
                        progress_pct = round((cur_rate / prev_yr_num) * 100, 1)

                existing = univ_dict.get(alias)
                history = existing.get("history", []) if existing else []

                # history 마지막과 비교하여 새 시점이면 추가
                if history:
                    last_h = history[-1]
                    if last_h.get("time") != t_str or last_h.get("date") != d_str:
                        if cur_app >= last_h.get("applicants", 0):
                            history.append({
                                "date": d_str,
                                "time": t_str,
                                "datetime_label": f"{d_str[-5:]} {t_str}",
                                "applicants": cur_app,
                                "rate": cur_rate
                            })
                else:
                    history.append({
                        "date": d_str,
                        "time": t_str,
                        "datetime_label": f"{d_str[-5:]} {t_str}",
                        "applicants": cur_app,
                        "rate": cur_rate
                    })

                diff = 0
                if len(history) >= 2:
                    diff = history[-1]["applicants"] - history[-2]["applicants"]

                univ_dict[alias] = {
                    "category": cfg["category"],
                    "alias": alias,
                    "univ_name": cfg["univ_name"],
                    "admission": cfg["admission"],
                    "major": cfg["major"],
                    "quota": cfg["quota"],
                    "applicants": cur_app,
                    "diff": diff,
                    "rate": cur_rate,
                    "rate_str": f"{cur_rate:.2f} : 1",
                    "prev_year": cfg["prev_year"],
                    "progress_pct": progress_pct,
                    "min_5yr": cfg["min_5yr"],
                    "avg_5yr": cfg["avg_5yr"],
                    "latest_time": t_str,
                    "url": cfg["url"],
                    "history": history
                }

        final_univs = []
        for cfg in UNIV_CONFIGS:
            if cfg["alias"] in univ_dict:
                final_univs.append(univ_dict[cfg["alias"]])

        today_str = datetime.date.today().strftime("%Y-%m-%d")
        response_payload = {
            "updated_at": f"{today_str} {latest_time_str}",
            "total_target_colleges": len(final_univs),
            "universities": final_univs,
            "live_refreshed": True
        }

        # 3. JSON 응답 전송
        body = json.dumps(response_payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

# -*- coding: utf-8 -*-
import os
import re
import json
import datetime
import urllib.request
from http.server import BaseHTTPRequestHandler
from bs4 import BeautifulSoup

UNIV_CONFIGS = [
    {
        "category": "지원 1",
        "alias": "단국대",
        "sheet": "단국대",
        "univ_name": "단국대학교",
        "admission": "DKU인재-서류형",
        "major": "일본학전공",
        "quota": 9,
        "prev_year": "20.33 : 1",
        "min_5yr": "8.11 : 1",
        "avg_5yr": "12.39 : 1",
        "url": "http://addon.jinhakapply.com/RatioV1/RatioH/Ratio10420521.html",
        "enc": "utf-8",
        "type": "jinhak",
        "target_admission_match": "서류형",
        "target_major_match": "일본학전공"
    },
    {
        "category": "지원 2",
        "alias": "동덕여대",
        "sheet": "동덕여자대학교",
        "univ_name": "동덕여대",
        "admission": "동덕창의리더전형",
        "major": "일어일본학전공",
        "quota": 11,
        "prev_year": "7.60 : 1",
        "min_5yr": "7.60 : 1",
        "avg_5yr": "10.54 : 1",
        "url": "http://ratio.uwayapply.com/Sl5KOTpWcldhVkpmJSY6Jko3ZlRm",
        "enc": "euc-kr",
        "type": "uway",
        "target_admission_match": "동덕창의리더",
        "target_major_match": "일어일본학전공"
    },
    {
        "category": "지원 3",
        "alias": "전남대",
        "sheet": "전남대",
        "univ_name": "전남대학교",
        "admission": "고교생활우수자 Ⅰ",
        "major": "일어일문학과",
        "quota": 12,
        "prev_year": "8.75 : 1",
        "min_5yr": "8.25 : 1",
        "avg_5yr": "10.08 : 1",
        "url": "http://ratio.uwayapply.com/Sl5KOlcvSmYlJjomSjdmVGY=",
        "enc": "euc-kr",
        "type": "uway",
        "target_admission_match": "고교생활우수자",
        "target_major_match": "일어일문학과"
    },
    {
        "category": "지원 4",
        "alias": "한남대",
        "sheet": "한남대",
        "univ_name": "한남대학교",
        "admission": "한남인재 Ⅰ",
        "major": "일어일문학과",
        "quota": 6,
        "prev_year": "7.30 : 1",
        "min_5yr": "3.80 : 1",
        "avg_5yr": "6.24 : 1",
        "url": "http://addon.jinhakapply.com/RatioV1/RatioH/Ratio11560931.html",
        "enc": "utf-8",
        "type": "jinhak",
        "target_admission_match": "한남인재",
        "target_major_match": "일어일문학"
    },
    {
        "category": "지원 5",
        "alias": "백석대",
        "sheet": "백석대학교",
        "univ_name": "백석대학교",
        "admission": "창의인재전형",
        "major": "어문학부",
        "quota": 7,
        "prev_year": "9.80 : 1",
        "min_5yr": "9.80 : 1",
        "avg_5yr": "9.80 : 1",
        "url": "http://ratio.uwayapply.com/Sl5KOkJKZiUmOiZKN2ZUZg==",
        "enc": "euc-kr",
        "type": "uway",
        "target_admission_match": "창의인재",
        "target_major_match": "어문학부"
    },
    {
        "category": "지원 6",
        "alias": "서울여대",
        "sheet": "서울여자대학교",
        "univ_name": "서울여대",
        "admission": "바롬인재면접전형",
        "major": "일어일문학과",
        "quota": 8,
        "prev_year": "16.60 : 1",
        "min_5yr": "16.40 : 1",
        "avg_5yr": "20.58 : 1",
        "url": "http://addon.jinhakapply.com/RatioV1/RatioH/Ratio10860821.html",
        "enc": "utf-8",
        "type": "jinhak",
        "target_admission_match": "바롬인재면접",
        "target_major_match": "일어일문학과"
    },
    {
        "category": "기타",
        "alias": "가톨릭대",
        "sheet": "가톨릭대학교",
        "univ_name": "가톨릭대",
        "admission": "잠재능력우수자면접전형",
        "major": "일어일본문화학과",
        "quota": 6,
        "prev_year": "34.17 : 1",
        "min_5yr": "16.30 : 1",
        "avg_5yr": "26.65 : 1",
        "url": "http://addon.jinhakapply.com/RatioV1/RatioH/Ratio10030381.html",
        "enc": "utf-8",
        "type": "jinhak",
        "target_admission_match": "잠재능력",
        "target_major_match": "일어일본문화"
    },
    {
        "category": "기타",
        "alias": "충남대",
        "sheet": "충남대",
        "univ_name": "충남대학교",
        "admission": "학생부종합 Ⅰ 면접",
        "major": "일어일문학과",
        "quota": 3,
        "prev_year": "29.67 : 1",
        "min_5yr": "10.67 : 1",
        "avg_5yr": "18.27 : 1",
        "url": "http://addon.jinhakapply.com/RatioV1/RatioH/Ratio11400471.html",
        "enc": "utf-8",
        "type": "jinhak",
        "target_admission_match": "면접전형",
        "target_major_match": "일어일문"
    },
    {
        "category": "기타",
        "alias": "경기대",
        "sheet": "경기대학교",
        "univ_name": "경기대학교",
        "admission": "KGU 학생부종합전형",
        "major": "글로벌어문학부",
        "quota": 55,
        "prev_year": "16.38 : 1",
        "min_5yr": "6.87 : 1",
        "avg_5yr": "13.69 : 1",
        "url": "http://ratio.uwayapply.com/Sl5KJXJyV2FiOUpmJSY6Jko3ZlRm",
        "enc": "euc-kr",
        "type": "uway",
        "target_admission_match": "KGU",
        "target_major_match": "글로벌어문학부"
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

                prev_yr_num = float(cfg["prev_year"].split(":")[0].strip()) if ":" in cfg["prev_year"] else 1.0
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

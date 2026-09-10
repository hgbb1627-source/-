# -*- coding: utf-8 -*-
"""
Netlify Functions용 즉시 새로고침 함수 (AWS Lambda 스타일 handler(event, context) 시그니처).

api/refresh.py(Vercel용)와 로직은 완전히 동일하며, 호출 규약만 Netlify Functions에
맞게 이식했습니다.
※ UNIV_CONFIGS는 auto_fetch_competition.py / api/refresh.py / 이 파일 세 군데에
  중복 정의되어 있습니다 — 대학·전형 정보를 바꿀 때는 반드시 세 파일 모두 동일하게
  수정하세요.
※ Netlify에서 이 함수를 직접 테스트해 보지 못했습니다(이 개발 환경에는 Netlify
  런타임/계정이 없음). 배포 후 "/api/refresh" 응답을 한 번 확인해 주세요. 실패하더라도
  index.html이 자동으로 data/records.json 정적 데이터로 폴백하므로 대시보드 자체는
  정상 동작합니다.
"""
import os
import re
import json
import datetime
import urllib.request
from bs4 import BeautifulSoup

# 11개 대상 전형 설정 (의약학 계열: 핵심 6 + 모니터링 5)
UNIV_CONFIGS = [
    {
        "category": "지원 1",
        "alias": "전북대-지역의사전주권",
        "sheet": "전북대_지역의사전주권",
        "univ_name": "전북대학교",
        "admission": "학생부교과 지역의사선발전형-전주권",
        "major": "의예과",
        "quota": 9,
        "prev_year": "신설",
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
        "prev_year": "10.00 : 1",
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
        "prev_year": "40.00 : 1",
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
        "prev_year": "6.10 : 1",
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
        "prev_year": "신설",
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
        "prev_year": "35.70 : 1",
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
        "prev_year": "신설",
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
        "prev_year": "신설",
        "url": "https://ratio.uwayapply.com/Sl5KOldCL0pmJSY6Jko3ZlRm",
        "enc": "euc-kr",
        "type": "uway",
        "target_admission_match": "지역의사선발전형-광역권",
        "target_major_match": "의예과"
    },
    {
        "category": "기타",
        "alias": "원광대-지역의사전주권",
        "sheet": "원광대_지역의사전주권",
        "univ_name": "원광대학교",
        "admission": "지역의사선발전형 진료권-전주권",
        "major": "의예과",
        "quota": 7,
        "prev_year": "신설",
        "url": "https://ratio.uwayapply.com/Sl5Kclc4TjlXYU5KZiUmOiZKN2ZUZg==",
        "enc": "euc-kr",
        "type": "uway",
        "target_admission_match": "지역의사선발전형",
        "target_major_match": "의예과"
    },
    {
        "category": "기타",
        "alias": "원광대-지역의사광역권",
        "sheet": "원광대_지역의사광역권",
        "univ_name": "원광대학교",
        "admission": "지역의사선발전형 진료권-광역권",
        "major": "의예과",
        "quota": 4,
        "prev_year": "신설",
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
        "prev_year": "50.00 : 1",
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
        with urllib.request.urlopen(req, timeout=8) as resp:
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


def _load_fallback_json():
    """data/records.json을 여러 후보 경로에서 찾아 로드 (Netlify 번들 경로가 환경마다 달라질 수 있어 방어적으로 처리)"""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "..", "..", "data", "records.json"),   # 로컬: netlify/functions/ -> repo root
        os.path.join(here, "data", "records.json"),               # included_files로 함수 폴더에 번들된 경우
        os.path.join(os.getcwd(), "data", "records.json"),        # 런타임 작업 디렉터리가 repo root인 경우
        os.environ.get("LAMBDA_TASK_ROOT", "") and os.path.join(os.environ["LAMBDA_TASK_ROOT"], "data", "records.json"),
    ]
    for path in candidates:
        if path and os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                continue
    return {"universities": []}


def handler(event, context):
    # 1. 기존 records.json 로드 (폴백용)
    fallback_data = _load_fallback_json()
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

            # 전년도 경쟁률 데이터가 없으면(예: "신설") 진행률을 계산하지 않고 None 처리
            progress_pct = None
            if ":" in cfg["prev_year"]:
                prev_yr_num = float(cfg["prev_year"].split(":")[0].strip())
                if prev_yr_num > 0:
                    progress_pct = round((cur_rate / prev_yr_num) * 100, 1)

            existing = univ_dict.get(alias)
            history = existing.get("history", []) if existing else []

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

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json; charset=utf-8",
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"
        },
        "body": json.dumps(response_payload, ensure_ascii=False)
    }

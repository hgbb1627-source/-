# 🎓 2027 수시 실시간 경쟁률 모니터링 시스템 템플릿

본 패키지는 Apple 휴먼 인터페이스 가이드라인 기반의 프리미엄 대시보드 웹앱과, 대학별 실시간 경쟁률 자동 스크래핑 파이프라인을 포함하고 있습니다.

---

## 📁 포함된 파일 구성

1. **index.html**: Apple 디자인 모바일/PC 반응형 실시간 대시보드 (Chart.js 시계열 차트 내장)
2. **auto_fetch_competition.py**: 6~9개 대학 실시간 경쟁률 자동 스크래핑 및 엑셀/JSON 동기화 엔진
3. **api/refresh.py**: Vercel 웹에서 '새로고침' 클릭 시 즉시 실시간 크롤링을 수행하는 서버리스 함수
4. **vercel.json**: Vercel 배포 설정 (서울 리전 icn1, 캐시 방지)
5. **requirements.txt**: Vercel 서버리스 함수용 파이썬 의존성 (beautifulsoup4)
6. **.github/workflows/update_competition.yml**: GitHub Actions 정기 자동 수집 워크플로우
7. **netlify.toml**: Netlify 배포 설정 (캐시 방지, `/api/refresh` → Netlify Function 리다이렉트)
8. **netlify/functions/refresh.py**: Netlify용 즉시 새로고침 서버리스 함수 (api/refresh.py와 동일 로직)

---

## ⚙️ 내 자녀 대학으로 변경하는 방법 (딱 1곳!)

auto_fetch_competition.py, api/refresh.py, netlify/functions/refresh.py **세 파일 모두**에 있는 **UNIV_CONFIGS** 목록을 자녀의 목표 대학 6개로 동일하게 수정합니다:

```python
UNIV_CONFIGS = [
    {
        'category': '지원 1',                     # '지원 1' ~ '지원 6'
        'alias': '고려대',                        # 짧은 대학명
        'sheet': '고려대',                        # 엑셀 시트명
        'univ_name': '고려대학교',                # 정식 대학명
        'admission': '학교추천',                  # 전형명
        'major': '경영대학',                      # 모집단위(학과)
        'quota': 45,                             # 모집정원 (숫자)
        'prev_year': '12.50 : 1',                # 전년도(2026) 경쟁률 (없으면 '데이터 없음')
        'url': 'http://ratio.uwayapply.com/...', # 진학사 또는 유웨이 실시간 경쟁률 URL
        'enc': 'euc-kr',                         # 유웨이는 euc-kr, 진학사는 utf-8
        'type': 'uway',                          # 'uway' 또는 'jinhak'
        'target_admission_match': '학교추천',      # 웹페이지 전형 키워드
        'target_major_match': '경영'              # 웹페이지 학과 키워드
    },
    # ... 총 6개 등록
]
```

---

## 🚀 Vercel 무료 웹 호스팅 배포 방법 (3단계)

1. **GitHub 저장소 생성**: 본 파일들을 GitHub 새 Repository에 업로드(Push)합니다.
2. **Vercel 연동**: [Vercel](https://vercel.com) 로그인 후 **Add New... > Project**에서 해당 저장소를 Import합니다.
3. **배포 완료**: Framework Preset은 Other 그대로 두고 **Deploy** 클릭!
   - 1분 만에 고유 URL(예: https://my-admission.vercel.app)이 생성되며, 스마트폰/PC 어디서든 실시간 경쟁률을 모니터링할 수 있습니다.

---

## 🌐 Netlify 무료 웹 호스팅 배포 방법 (3단계)

Vercel 대신 Netlify를 쓰고 싶다면 `netlify.toml`과 `netlify/functions/refresh.py`가 이미 준비되어 있습니다.

1. **GitHub 저장소 생성**: 본 파일들을 GitHub 새 Repository에 업로드(Push)합니다. (Vercel과 동일 저장소를 그대로 써도 무방합니다 — `vercel.json`과 `netlify.toml`은 서로 충돌하지 않습니다.)
2. **Netlify 연동**: [Netlify](https://app.netlify.com) 로그인 후 **Add new site → Import an existing project**에서 해당 저장소를 선택합니다.
3. **배포 완료**: Build command는 비워두고 Publish directory는 `.`(저장소 루트) 그대로 두고 **Deploy site** 클릭!
   - 1~2분 만에 고유 URL(예: https://my-admission.netlify.app)이 생성됩니다.
   - **배포 후 꼭 확인**: `https://[내사이트].netlify.app/api/refresh`에 접속해서 JSON이 정상 응답되는지 확인하세요. Netlify Python Functions는 계정/리전마다 동작이 다를 수 있어 사전 검증을 못 했습니다. 혹시 이 경로가 실패해도 대시보드 자체(`data/records.json` 기반 초기 데이터, 30분 자동 새로고침)는 정상 동작합니다 — "새로고침" 버튼의 즉시 크롤링 기능만 영향을 받습니다.
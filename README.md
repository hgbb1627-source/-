# 🎓 2027 수시 실시간 경쟁률 모니터링 시스템 템플릿

본 패키지는 Apple 휴먼 인터페이스 가이드라인 기반의 프리미엄 대시보드 웹앱과, 대학별 실시간 경쟁률 자동 스크래핑 파이프라인을 포함하고 있습니다.

---

## 📁 포함된 파일 구성

1. **index.html**: Apple 디자인 모바일/PC 반응형 실시간 대시보드 (Chart.js 시계열 차트 내장)
2. **uto_fetch_competition.py**: 6~9개 대학 실시간 경쟁률 자동 스크래핑 및 엑셀/JSON 동기화 엔진
3. **pi/refresh.py**: Vercel 웹에서 '새로고침' 클릭 시 즉시 실시간 크롤링을 수행하는 서버리스 함수
4. **ercel.json**: Vercel 배포 설정 (서울 리전 icn1, 캐시 방지)
5. **
equirements.txt**: 서버리스 함수용 파이썬 의존성 (beautifulsoup4)
6. **.github/workflows/update_competition.yml**: GitHub Actions 정기 자동 수집 워크플로우

---

## ⚙️ 내 자녀 대학으로 변경하는 방법 (딱 1곳!)

uto_fetch_competition.py와 pi/refresh.py 상단의 **UNIV_CONFIGS** 목록을 자녀의 목표 대학 6개로 수정합니다:

`python
UNIV_CONFIGS = [
    {
        'category': '지원 1',                     # '지원 1' ~ '지원 6'
        'alias': '고려대',                        # 짧은 대학명
        'sheet': '고려대',                        # 엑셀 시트명
        'univ_name': '고려대학교',                # 정식 대학명
        'admission': '학교추천',                  # 전형명
        'major': '경영대학',                      # 모집단위(학과)
        'quota': 45,                             # 모집정원 (숫자)
        'prev_year': '12.50 : 1',                # 전년도(2026) 경쟁률
        'min_5yr': '8.20 : 1',                   # 5개년 최저
        'avg_5yr': '11.40 : 1',                  # 5개년 평균
        'url': 'http://ratio.uwayapply.com/...', # 진학사 또는 유웨이 실시간 경쟁률 URL
        'enc': 'euc-kr',                         # 유웨이는 euc-kr, 진학사는 utf-8
        'type': 'uway',                          # 'uway' 또는 'jinhak'
        'target_admission_match': '학교추천',      # 웹페이지 전형 키워드
        'target_major_match': '경영'              # 웹페이지 학과 키워드
    },
    # ... 총 6개 등록
]
`

---

## 🚀 Vercel 무료 웹 호스팅 배포 방법 (3단계)

1. **GitHub 저장소 생성**: 본 파일들을 GitHub 새 Repository에 업로드(Push)합니다.
2. **Vercel 연동**: [Vercel](https://vercel.com) 로그인 후 **Add New... > Project**에서 해당 저장소를 Import합니다.
3. **배포 완료**: Framework Preset은 Other 그대로 두고 **Deploy** 클릭!
   - 1분 만에 고유 URL(예: https://my-admission.vercel.app)이 생성되며, 스마트폰/PC 어디서든 실시간 경쟁률을 모니터링할 수 있습니다.
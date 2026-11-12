# Practice Portfolio — BigQuery · dbt · Superset 분석 파이프라인

이커머스 매출/마진 KPI와 검색 퍼널(노출 → 클릭 → SDP 진입 → 장바구니 → 구매) 데이터를
**BigQuery(raw) → dbt(staging/marts) → Superset(대시보드)** 순서로 처리하는 포트폴리오 프로젝트입니다.

> 모든 데이터는 synthetic(가상) 데이터이며 실제 기업 데이터가 아닙니다.

## 폴더 구조

```
practice_portfolio/
├── bq_dbt_portfolio/
│   ├── bigquery/                         # 1단계: raw 레이어 구축
│   │   ├── raw_schema_bigquery.sql       #   raw 데이터셋/테이블 DDL (서울 리전)
│   │   └── load_to_bigquery.py           #   CSV → BigQuery raw 테이블 적재 스크립트
│   └── dbt_portfolio/                    # 2단계: dbt 변환
│       ├── dbt_project.yml               #   프로젝트 설정 (staging=view, marts=table)
│       ├── packages.yml                  #   dbt_utils 의존성
│       ├── profiles.yml.example          #   접속 프로필 예시 (실제 profiles.yml은 커밋 안 함)
│       └── models/
│           ├── staging/                  #   raw 정제 레이어
│           │   ├── _staging__sources.yml
│           │   ├── _staging__models.yml
│           │   ├── stg_sales_kpi_daily.sql
│           │   ├── stg_search_funnel_daily.sql
│           │   └── stg_keyword_dim.sql
│           └── marts/                    #   분석/대시보드용 레이어
│               ├── _marts__models.yml
│               ├── mart_sales_margin_daily.sql          # 서브카테고리×일자 매출/마진
│               ├── mart_kpi_monthly_summary.sql         # 서브카테고리×월 KPI + MoM/YoY
│               ├── mart_search_funnel_daily.sql         # 키워드×일자 퍼널 전환율
│               └── mart_search_funnel_monthly_trend.sql # 서브카테고리×월 퍼널 추이
└── superset_portfolio/                   # 3단계: 시각화
    ├── docker-compose.yml                #   Superset + 메타 DB(Postgres) 로컬 실행
    ├── SUPERSET_SETUP.md                 #   실행·BigQuery 연결·데이터셋 등록 가이드
    └── dashboard_design_spec.md          #   대시보드 2종 차트 설계안
```

## 실행 순서

1. **BigQuery raw 레이어**
   ```bash
   gcloud auth application-default login
   # raw_schema_bigquery.sql 실행 후
   cd bq_dbt_portfolio/bigquery
   python load_to_bigquery.py --project <GCP_PROJECT_ID> --data-dir <CSV 폴더>
   ```
2. **dbt 변환**
   ```bash
   # profiles.yml.example 을 ~/.dbt/profiles.yml 로 복사 후 <GCP_PROJECT_ID> 수정
   cd bq_dbt_portfolio/dbt_portfolio
   dbt deps
   dbt build
   ```
3. **Superset 대시보드** — `superset_portfolio/SUPERSET_SETUP.md` 참고

## 보안 / 커밋 제외 항목

`.gitignore`로 다음 파일은 저장소에 올라가지 않습니다.

- `profiles.yml` (dbt 접속 정보) — 예시인 `profiles.yml.example`만 커밋
- `*.json` (GCP 서비스 계정 키 등), `*.pem`, `*.key`, `.env`
- dbt 산출물(`target/`, `dbt_packages/`, `logs/`), 원본 CSV 데이터

`superset_portfolio/docker-compose.yml`의 비밀번호·`SUPERSET_SECRET_KEY`는 **로컬 데모용 기본값**입니다.
외부에 배포할 때는 반드시 `.env` 파일로 분리하고 값을 바꿔서 사용하세요.

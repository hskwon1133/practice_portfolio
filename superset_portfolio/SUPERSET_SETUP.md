# Superset 설정 가이드

이 문서는 `dbt_portfolio/`의 mart 모델이 BigQuery에 올라간 **이후** 진행하는 단계입니다.
(BigQuery 연결 전이라면 `bigquery/`, `dbt_portfolio/` 먼저 완료)

## 1. Superset 실행

```bash
docker compose up -d
# 최초 1회: 관리자 계정 생성 + DB 마이그레이션
docker exec -it superset_app superset fab create-admin \
  --username admin --firstname Admin --lastname User \
  --email admin@example.com --password admin
docker exec -it superset_app superset db upgrade
docker exec -it superset_app superset init
```

http://localhost:8088 접속 → 위에서 만든 admin 계정으로 로그인

## 2. BigQuery 연결 (Database 등록)

1. Superset 컨테이너에 BigQuery 드라이버 설치 필요:
   ```bash
   docker exec -it superset_app pip install sqlalchemy-bigquery
   docker restart superset_app
   ```
2. Settings → Database Connections → + Database → BigQuery 선택
3. 서비스 계정 JSON 키 업로드 (GCP Console → IAM → 서비스 계정 → 키 생성, `BigQuery Data Viewer` + `BigQuery Job User` 역할만 부여 — 최소 권한 원칙)
4. SQLAlchemy URI 예시: `bigquery://<GCP_PROJECT_ID>`
5. "Test Connection" 통과 확인 후 저장

## 3. Dataset 등록 (dbt marts 기준)

Data → Datasets → + Dataset 에서 아래 4개를 등록합니다 (전부 `marts` 스키마):

| Dataset | 용도 |
|---|---|
| `marts.mart_kpi_monthly_summary` | 매출/마진 KPI 대시보드 — MoM/YoY 성장률 포함 |
| `marts.mart_sales_margin_daily` | 매출/마진 일별 상세 (드릴다운용) |
| `marts.mart_search_funnel_monthly_trend` | 검색 Funnel 전환율 추이 (SDP 개선 스토리) |
| `marts.mart_search_funnel_daily` | 검색 Funnel 일별 상세, Funnel 차트용 |

## 4. 차트/대시보드 구성

`dashboard_design_spec.md` 참고해서 차트 하나씩 만든 뒤 대시보드 2개(매출/마진, 검색 Funnel)로 묶으세요.

## 5. 포트폴리오용 공유

- Superset은 기본적으로 외부 공개 링크가 없으므로(사내 BI 툴 성격), 포트폴리오에는 **스크린샷 + 대시보드 설계 문서**를 README에 넣는 방식을 권장
- 만약 외부에 인터랙티브 데모가 꼭 필요하면 Superset을 무료 클라우드(Fly.io, Render 등)에 배포하거나, 같은 마트 데이터를 Tableau Public에도 한 번 더 퍼블리시하는 걸 대안으로 고려

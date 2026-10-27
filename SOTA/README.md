# 기존 방법 비교 코드

> 2026-10-27 업로드 기준. 이 디렉터리는 비교 하네스의 **개발 초안**이며, 기존 방법 대비 최종 우위가 검증됐다는 뜻이 아닙니다.

## 현재 파일

| 역할 | 위치 | 상태 |
|---|---|---|
| 실행·비교 진입점 | [run.py](dayoung/run.py), [compare.py](dayoung/compare.py) | 코드 업로드 |
| 입력·생성·채점·통계 | [artifacts.py](dayoung/artifacts.py), [generate.py](dayoung/generate.py), [scoring.py](dayoung/scoring.py), [stats.py](dayoung/stats.py) | P9/A0 산출물과 공용 프롬프트 필요 |
| 자체 기준선 | [ours_lookup.py](dayoung/ours_lookup.py), [ours_router.py](dayoung/ours_router.py) | 저장된 행동 결과로 P8S 기준선·Router 평가 |
| CAD / AdaCAD | [sota_contrastive.py](dayoung/sota_contrastive.py) | 구현 코드 있음; 이 정리에서 실행 검증하지 않음 |
| SpARE / SHIFT / COIECD / CoCoA | [sota_stubs.py](dayoung/sota_stubs.py) | `NotImplementedError`인 미구현 stub |

## 실행 전 해결할 사항

현재 Python 파일들은 `dayoung/` 바로 아래에 있지만, import는 `common.*`와 `methods.*` 패키지 배치를 전제로 합니다. 해당 디렉터리가 없어 **현 상태에서 안내 명령만으로 benchmark를 실행할 수 없습니다**.

패키지 구조를 맞춘 뒤에도 다음 외부 자료가 필요합니다.

- `ABENCH_P9`: hidden·라벨·row manifest·model revision·동결 프롬프트가 있는 P9 공유 폴더
- `ABENCH_A0`: A0 행동별 `gen_*.parquet`
- 모듈에서 요구하는 프롬프트 MD5와 생성·채점 환경
- 생성 방법을 실행할 경우 모델 접근 권한·GPU

[팀원 원본 실행 설계](dayoung/README.md)의 `common/`·`methods/` 경로는 의도한 구조이며 현재 실제 배치와 구분해야 합니다. 외부 ConFiQA·NQ-Swap 평가도 이 하네스에 아직 연결되지 않았습니다.

## 결과 비교 원칙

이 프로젝트의 외부 보고는 C± 모두 원래 사실 정답으로 채점합니다. 문맥 충실도 기준의 원 논문 점수를 그대로 가져와 우위를 주장하지 않습니다. 동일 데이터·질문·프롬프트·생성·채점 조건에서 비교하며, 학습 라벨과 추론 비용도 함께 보고합니다.

P8S 기준선의 보고값은 Base 0.5310, Always 0.5997, late Router 0.6078입니다. Packed 및 외부 보고와의 비교 조건은 [연구 결과](../docs/research_status.md)에 정리했습니다.

# Team Contributions

> 평가자가 GitHub 레포 안에서 **팀원별 실제 기여**를 빠르게 확인할 수 있도록 정리한 문서입니다.  
> AI 도구는 초안·리팩토링·문서 정리 보조에 활용되었으며, **연구 방향·실험 설계·결과 해석·최종 판단은 팀**이 수행했습니다. 상세: [`docs/ai_transparency_report.md`](ai_transparency_report.md).

| 팀원 | 주요 담당 | GitHub evidence |
|------|-----------|-------------------|
| **박세령** (@ryeong03) | conflict 문제 정의, RAG pipeline 설계·구현, verification·CI, 데모/smoke 문서 | [PR #81](https://github.com/Ontology0/Graduation-Project/pull/81) (GitHub Actions + evaluate Arm 1·2), [PR #76](https://github.com/Ontology0/Graduation-Project/pull/76) (CI scaffold), [PR #71](https://github.com/Ontology0/Graduation-Project/pull/71) (README 실행 결과물), [issue #59](https://github.com/Ontology0/Graduation-Project/issues/59) (verification checklist) |
| **이다영** (@dev-ldy03) | 데이터 파이프라인, 평가 설계, 파일럿 실험 결과 정리 | [PR #80](https://github.com/Ontology0/Graduation-Project/pull/80) (exp1 설계·채점 구분), [PR #68](https://github.com/Ontology0/Graduation-Project/pull/68) / [issue #56](https://github.com/Ontology0/Graduation-Project/issues/56) (5-arm 평가 하네스), [issue #55](https://github.com/Ontology0/Graduation-Project/issues/55) (benchmark train/eval split) |
| **손현경** (@bbberylll) | DPO 학습 방향 설계, LoRA fine-tuning scaffold, 발표·문서 | [PR #69](https://github.com/Ontology0/Graduation-Project/pull/69) (DPO training), [issue #54](https://github.com/Ontology0/Graduation-Project/issues/54) (DPO 파이프라인), [PR #74](https://github.com/Ontology0/Graduation-Project/pull/74) (main 반영) |

## 협업 방식 (요약)

- **브랜치:** `dev` 통합 → milestone 시 `main` (see `CONTRIBUTING.md`)
- **이슈·PR:** `feat/`, `docs/`, `fix/` 태그 + 이슈 번호 참조
- **Co-authored-by:** AI 보조 커밋에 `Co-authored-by: Cursor` 등 명시 (투명성)

## 관련 문서

- [`docs/rq_to_implementation_map.md`](rq_to_implementation_map.md) — RQ ↔ 코드 정합성
- [`docs/verification_checklist.md`](verification_checklist.md) — 재현·운영 검증 기록
- [`docs/ai_transparency_report.md`](ai_transparency_report.md) — AI 활용 투명성

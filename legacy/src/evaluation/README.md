# src/evaluation/

벤치마크·지표가 **확정된 뒤** RAG 예측을 채점하는 **평가 하네스**용 모듈입니다. 현재는 인터페이스만 있고 실제 점수는 계산하지 않습니다.

## 파일별 역할

| 파일 | 역할 |
|------|------|
| `evaluate.py` | `evaluate_placeholder()` — 미래 메트릭용 시그니처, 빈 `metrics` 반환 |

## 상태

**스캐폴드:** RAGAS·LLM-as-judge·human eval 등은 **후보만** (`docs/experiment_design.md`, `docs/benchmark_selection.md`). 가짜 accuracy·RAGAS 수치·벤치마크 표를 만들지 않습니다.

## 실행

```bash
python -m src.evaluation.evaluate
```

산출물은 프로토콜 확정 후 `outputs/` 하위에 둘 예정입니다.

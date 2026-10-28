# src/training/

context–memory **지식 충돌** 대응을 위한 **DPO + LoRA** 미세조정 진입점입니다. preference 데이터·실제 학습 루프는 아직 연결 전입니다.

## 파일별 역할

| 파일 | 역할 |
|------|------|
| `train.py` | `TrainingConfig`, `run_training()` — DPO+LoRA 설정 검증용 스캐폴드 |

## 실행

```bash
python -m src.training.train
```

실험 arm YAML(스캐폴드): `configs/experiments/lora_*.yaml`  
계획 데이터: `data/synthetic/` (DPO preference pairs)

## 상태

**스캐폴드:** `run_training()`은 `status: not_implemented`를 반환합니다. TRL `DPOTrainer` + PEFT 연동 예정. **학습 결과·벤치마크 점수는 아직 없습니다.**

관련: `docs/decision_log.md`, `docs/experiment_design.md`

# 초기 연구와 개발 자료

현재 연구는 [Routing·Steering 실험](../experiments/README.md)입니다. 이 폴더에는 초기 RAG·DPO/LoRA 구상, 웹·Telegram 봇 구현, 수업 제출물과 파일럿 결과를 모았습니다.

## 보관 자료

| 자료 | 내용 |
|---|---|
| [src/](src/) | 초기 RAG, 학습·평가, Telegram 봇 코드 |
| [configs/](configs/) | RAG·LoRA 실험 설정과 프롬프트 |
| [app.py](app.py) | 초기 Gradio 웹 데모 |
| [course/](course/) | 이전 학기 프로젝트 소개·관련 연구·팀 규칙·활용 기록 |
| [experiments/](experiments/) · [outputs/](outputs/) | 기존 파일럿 실험과 저장 결과 |
| [requirements.txt](requirements.txt) · [pyproject.toml](pyproject.toml) | 초기 구현의 설치·패키지 설정 |
| [requirements_bot.txt](requirements_bot.txt) · [Procfile](Procfile) · [railway.json](railway.json) | 초기 봇의 설치·배포 설정 |
| [.env.example](.env.example) | 초기 앱·봇용 환경변수 예시 |
| [Makefile](Makefile) | 초기 RAG 실행 명령 |
| [.vscode/](.vscode/) | 이전 발표자료의 Marp 편집 설정 |
| [ci/test.yml](ci/test.yml) · [requirements-ci.txt](requirements-ci.txt) | 기존 RAG용 CI 설정 보관본 |

연구 방향과 당시 기록은 [이전 연구 문서](../docs/archive/README.md)에서 이어 볼 수 있습니다. 현재 사용하는 `data/p8s_pairs.csv`, `prompt/`, `experiments/`, `SOTA/`는 저장소 루트에 유지했습니다.

## 초기 코드의 작업 경로

초기 코드의 작업 디렉터리는 `legacy/`입니다. `src` 패키지, `configs/`, `outputs/` 사이의 상대 경로를 유지했으며, 설정 로더는 이 폴더를 기준으로 파일을 찾습니다.

```bash
cd legacy
```

원래 설치 파일을 참고해 별도 환경을 준비하고, 필요한 키는 이 폴더의 `.env`에 설정합니다. 기존 로컬 `.env`나 실제 배포 서비스의 설정은 이번 정리에서 변경하지 않았습니다.

RAG 실행은 보존된 모듈 진입점을 사용합니다.

```bash
python -m src.rag.pipeline \
  --config configs/experiments/rag_base.yaml \
  --docs /absolute/path/to/documents \
  --question "What is knowledge conflict in RAG?"
```

봇은 `python -m src.chatbot.telegram_bot --config configs/experiments/rag_github_bot.yaml --docs __repo__`로 실행하며, 저장소 문서 검색은 상위 저장소의 README와 `docs/`를 사용합니다. 보관된 배포 명령의 작업 디렉터리도 `legacy/`로 설정해야 합니다.

원래 설정이 가리키는 `data/sample_docs/`·학습 입력과 예전 `tests/`는 현재 저장소에 포함돼 있지 않습니다. 입력 데이터와 실행 환경을 별도로 준비해야 하며, 이번 이동에서는 모델·API 실행이나 재배포를 하지 않았습니다.

## 현재 저장소 검증

루트의 [Repository checks](../.github/workflows/repository.yml)는 현재 안내 문서의 로컬 링크, Python 문법, 노트북·JSON 구조를 검사합니다. `ci/test.yml`은 과거 설정의 보관본이며 실행되지 않습니다.

[현재 연구](../README.md) · [실험 안내](../experiments/README.md) · [전체 활동](../docs/review_guide.md)

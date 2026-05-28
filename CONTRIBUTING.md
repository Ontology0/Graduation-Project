# Contributing Guide

## 브랜치 전략

```
main ← 최종 제출 / 배포용 
      ├── feat/data/설명
      ├── feat/dpo/설명
      ├── feat/rag/설명
      ├── feat/eval/설명
      ├── docs/설명
      ├── chore/설명
      └── fix/설명
```


### 작업 순서
```
1. dev 브랜치에서 새 브랜치 생성
2. 작업 후 dev로 PR
3. 팀원 리뷰 후 merge
```

---

## 커밋 메시지 규칙

형식: `태그: 내용(#이슈번호)`

| 태그 | 언제 |
|---|---|
| `feat` | 새 기능 추가 |
| `fix` | 버그 수정 |
| `docs` | 문서 수정 |
| `refactor` | 코드 구조 변경 |
| `chore` | 설정, 패키지, 파일구조 변경 등 기타 |

### 예시
```
feat: ClashEval 전처리 스크립트 추가(#2)
fix: RAG 파이프라인 임포트 오류 수정(#3)
docs: README 실험 설계 업데이트(#13)
chore: doc/ 하위 폴더 구조 추가(#99)
```

---

## 주의사항

- `main`에 직접 push 금지
-  issue를 먼저 생성 후 작업하는 것을 권장
- `.DS_Store`, `.env` 커밋 금지 (.gitignore에 기록해서 깃허브로 안 넘어가게 관리)
- PR은 본인이 merge하지 말고 팀원 리뷰 후 merge
- PR 올리기 전에 로컬에서 먼저 테스트

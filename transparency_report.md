# AI 투명성 리포트

## 1. 단계별 AI 활용 현황

<table>
  <thead>
    <tr>
      <th width="170px">연구 단계</th>
      <th width="170px">사용 도구</th>
      <th>구체적 활용 내용 및 범위</th>
      <th>검증 및 비고</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>선행 연구 분석</b></td>
      <td>Claude 3.5 Sonnet<br>NotebookLM</td>
      <td>• PA-RAG, DPA-RAG, ClashEval 등 관련 논문 분석<br>• 핵심 방법론(DPO, LoRA, RAFT 등) 정리<br>• 벤치마크 구조 정리 및 질의</td>
      <td>NotebookLM 폐쇄형 설정으로<br>외부 데이터 혼입 방지 및 원문 근거 확인</td>
    </tr>
    <tr>
      <td><b>데이터 구성 (예정)</b></td>
      <td>ChatGPT-3.5</td>
      <td>• RAG-aware preference 데이터 자동 생성<br>• chosen/rejected 쌍 생성으로 비용 효율성 확보</td>
      <td>데이터 샘플링 통한 품질, 정합성 검수 필수</td>
    </tr>
    <tr>
      <td><b>실험 설계 및 평가 <br>(예정)</b></td>
      <td>GPT-4o<br>Gemini 1.5 Pro</td>
      <td>• Baseline vs Hybrid 대조군 설정 자문<br>• Faithfulness Score 등 주관적 지표 평가<br>• LLM-as-a-judge 방식 도입</td>
      <td>RAGAS 지표와 병행 교차 검증<br>(RTX 3090 × 4 환경 고려)</td>
    </tr>
    <tr>
      <td><b>코드 구현 및 최적화 (예정)</b></td>
      <td>Cursor<br>Claude (Code)</td>
      <td>• PyTorch 기반 학습 루프 구현 보조<br>• DeepSpeed 커스텀 설정 및 오류 디버깅</td>
      <td>단위 테스트 수행 및<br>핵심 로직 수식 대조 검증</td>
    </tr>
  </tbody>
</table>


## 2. 인간 주도 핵심 연구 영역

연구의 독창성과 신뢰성을 담보하기 위해 다음 영역은 AI의 보조 없이 연구진이 직접 수행함.

* **DPO 학습 데이터 품질 검토**: AI가 생성한 선호도 데이터 쌍을 직접 샘플링하여 연구 목적과의 정합성 및 편향 여부를 직접 판단.
* **핵심 가설 및 로직 설계**: 기존 논문에서 발견한 지식 충돌 및 병목 지점을 해결하기 위한 **독창적 하이브리드 지식 주입 방법론**을 고안.
* **최종 의사결정 및 해석**: AI가 제시한 다양한 실험 선택지 중 최적의 방법론을 채택하고, 도출된 데이터에 대한 의미론적 분석을 수행.
* **결과 검증**: AI가 요약·정리한 모든 내용과 실제 논문의 수식, 수치 데이터를 대조하여 정보의 정확성을 최종 확인.

## 3. AI 활용 원칙 및 윤리
* **교차 검증 원칙**: AI 도구의 답변을 무비판적으로 수용하지 않으며, 모든 기술적 인용구와 수치는 원문 논문을 직접 대조하여 검증.
* **데이터 보안 및 제한**: NotebookLM 등 활용 시 개인정보나 비공개 데이터는 업로드하지 않으며, 모든 처리는 연구용으로 공개된 벤치마크 데이터셋에 한정.

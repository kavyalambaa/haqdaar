# HAQDAAR M2 Development Baseline & Model Benchmark

## Executive Summary
* **Selected Production Candidate**: `gemini-3.5-flash-lite` (Selected as provisional MVP due to lower latency and consistent response times).
* **Baseline Dataset**: `data/eval/dev_extractor.json` (14 development test cases).
* **System Prompt & Schema Version**: Fixed 10-Field Schema (`LandInfo` nested object contract).

---

## 1. Evaluation Protocol Summary

### Protocol 1: Fixed 10-Field Protocol (140 Comparisons)
* **Fields Evaluated**: `age`, `gender`, `occupation`, `land`, `is_pregnant`, `pregnancy_month`, `pregnant_person`, `ration_card_type`, `state`, `district`.
* **Rules**: Evaluates all 10 fields across 14 cases ($14 \times 10 = 140$). Unmentioned attributes in target cases are evaluated as `null`.

### Protocol 2: Sparse Annotated Protocol (26 Comparisons)
* **Rules**: Evaluates only explicitly present ground-truth keys annotated in `dev_extractor.json`. Empty expected cases (`dev11`) are tracked separately.

---

## 2. Benchmark Comparison Matrix

| Metric | `gemini-3.5-flash-lite` (Provisional MVP) | `gemini-3.1-flash-lite` |
| :--- | :---: | :---: |
| **Total Cases Attempted** | 14 | 14 |
| **Successful API Calls** | 14 (100%) | 14 (100%) |
| **API Errors / Failures** | 0 | 0 |
| **Fixed 10-Field Protocol** | **122 / 140 (87.14%)** | **122 / 140 (87.14%)** |
| **Full Case Matches (Fixed)** | **4 / 14 cases** | **4 / 14 cases** |
| **Sparse Annotated Protocol** | **9 / 26 (34.62%)** | **9 / 26 (34.62%)** |
| **Average Latency per Case** | **~1.33s** | **~4.32s** (Spikes up to 25.4s) |
| **Primary Advantage** | **3.2x faster response time** | Identical accuracy, higher latency |

---

## 3. Preserved Evaluation Output Reports
All generated evaluation runs are saved separately inside `data/eval/results/` and preserved:
* `data/eval/results/eval_gemini-3.5-flash-lite.json`
* `data/eval/results/eval_gemini-3.1-flash-lite.json`
* `data/eval/results/eval_v2_gemini-3.5-flash-lite.json`
* `data/eval/results/eval_v2_gemini-3.1-flash-lite.json`

---

## 4. Known Mismatch Limitations (18 Field Discrepancies)
1. **Land Unit Naming**: Extractor outputs local Hindi/Roman script (`"unit": "बीघा"`), whereas target expected dataset strictly mandates English string tokens (`"unit": "bigha"`).
2. **Multi-Subject Contexts (`dev03`, `dev06`, `dev12`)**: When pregnancy mentions involve third parties (e.g. wife/mother vs self), fields like `pregnant_person` return `null` without multi-entity parsing.
3. **Implicit Caste/Ration Inferences (`dev04`)**: Colors like `"पीला"` require explicit normalization mapping inside the evaluation layer.
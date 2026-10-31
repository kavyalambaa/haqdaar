import argparse
import json
import os
import time
from typing import Dict, Any, Tuple
from extractor import extract, MODEL

DEV_DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "eval", "dev_extractor.json")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "eval", "results")

FIXED_10_FIELDS = [
    "age", "gender", "occupation", "land", 
    "is_pregnant", "pregnancy_month", "pregnant_person", 
    "ration_card_type", "state", "district"
]

def normalize_str(val: Any) -> Any:
    """Consistently normalizes strings for comparison."""
    if isinstance(val, str):
        return val.strip().lower()
    return val

def check_value_match(pred: Any, expected: Any, field_name: str = "") -> bool:
    """
    Refined matching rules:
    1. Null handling: If expected is None, pred must be None, {}, or [].
    2. Land object matching: Compare value and unit only; ignore extra fields like unit_as_said.
    3. List alternatives: If expected is a list, match if normalized pred equals any normalized item.
    4. String/primitive comparison: Direct normalized match.
    """
    if expected is None:
        return pred is None or pred == {} or pred == []

    # Task 1: Land field comparison (value & unit only)
    if field_name == "land" or (isinstance(expected, dict) and "value" in expected):
        if not isinstance(pred, dict):
            return False
        
        # Compare expected keys (value and unit) while ignoring unit_as_said
        for k in ["value", "unit"]:
            if k in expected:
                exp_v = normalize_str(expected.get(k))
                pred_v = normalize_str(pred.get(k))
                
                # Check for alternative options if unit is a list (e.g., ["kattha", "katha"])
                if isinstance(exp_v, list):
                    if pred_v not in [normalize_str(item) for item in exp_v]:
                        return False
                elif pred_v != exp_v:
                    return False
        return True

    # Task 2: Alternative answers in option lists
    if isinstance(expected, list):
        norm_expected = [normalize_str(item) for item in expected]
        if isinstance(pred, list):
            return any(normalize_str(p) in norm_expected for p in pred)
        return normalize_str(pred) in norm_expected

    # General dictionary matching
    if isinstance(expected, dict):
        if not isinstance(pred, dict):
            return False
        return all(check_value_match(pred.get(k), v, k) for k, v in expected.items())

    # Primitive string/number/boolean direct match
    return normalize_str(pred) == normalize_str(expected)

def evaluate_fixed_10_fields(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> Tuple[int, int, bool, Dict[str, Any]]:
    correct_count = 0
    total_count = len(FIXED_10_FIELDS)
    field_failures = {}

    for field in FIXED_10_FIELDS:
        expected_val = ground_truth.get(field, None)
        pred_val = prediction.get(field)

        if check_value_match(pred_val, expected_val, field_name=field):
            correct_count += 1
        else:
            field_failures[field] = {"expected": expected_val, "predicted": pred_val}

    is_fully_correct = (correct_count == total_count)
    return correct_count, total_count, is_fully_correct, field_failures

def evaluate_sparse_fields(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> Tuple[int, int, bool, Dict[str, Any], bool]:
    if not ground_truth:
        return 0, 0, True, {}, True

    correct_count = 0
    total_count = len(ground_truth)
    field_failures = {}

    for field, expected_val in ground_truth.items():
        pred_val = prediction.get(field)
        if check_value_match(pred_val, expected_val, field_name=field):
            correct_count += 1
        else:
            field_failures[field] = {"expected": expected_val, "predicted": pred_val}

    is_fully_correct = (correct_count == total_count)
    return correct_count, total_count, is_fully_correct, field_failures, False

def run_evaluation(model_name: str) -> Dict[str, Any]:
    with open(DEV_DATASET_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        dataset = raw_data.get("cases", raw_data) if isinstance(raw_data, dict) else raw_data

    total_cases = len(dataset)
    successful_cases = 0
    failed_cases = 0
    api_errors = 0

    fixed_correct_fields = 0
    fixed_total_fields = 0
    fixed_fully_correct_cases = 0

    sparse_correct_fields = 0
    sparse_total_fields = 0
    sparse_fully_correct_cases = 0
    empty_expected_cases = 0

    case_details = []

    print(f"\n====================================================")
    print(f" Running Final Evaluation: {model_name}")
    print(f"====================================================")

    for idx, sample in enumerate(dataset, 1):
        if not isinstance(sample, dict):
            continue

        sample_id = sample.get("id", f"case_{idx}")
        input_text = sample.get("text") or sample.get("input", "")
        ground_truth = sample.get("expected", {})

        start_time = time.time()
        try:
            prediction = extract(input_text, model_name=model_name)
            latency_sec = round(time.time() - start_time, 3)
            successful_cases += 1

            f_correct, f_total, f_case_pass, f_failures = evaluate_fixed_10_fields(prediction, ground_truth)
            fixed_correct_fields += f_correct
            fixed_total_fields += f_total
            if f_case_pass:
                fixed_fully_correct_cases += 1

            s_correct, s_total, s_case_pass, s_failures, is_empty = evaluate_sparse_fields(prediction, ground_truth)
            if is_empty:
                empty_expected_cases += 1
            else:
                sparse_correct_fields += s_correct
                sparse_total_fields += s_total
                if s_case_pass:
                    sparse_fully_correct_cases += 1

            case_details.append({
                "id": sample_id,
                "status": "SUCCESS",
                "latency_sec": latency_sec,
                "fixed_10_field_eval": {
                    "correct_fields": f_correct,
                    "total_fields": f_total,
                    "fully_correct": f_case_pass,
                    "failures": f_failures
                },
                "sparse_annotated_eval": {
                    "is_empty_expected": is_empty,
                    "correct_fields": s_correct,
                    "total_fields": s_total,
                    "fully_correct": s_case_pass,
                    "failures": s_failures
                },
                "prediction": prediction,
                "expected": ground_truth
            })
            print(f"[✓] {sample_id} ({latency_sec}s) - Fixed: {f_correct}/{f_total} | Sparse: {s_correct}/{s_total}")

        except Exception as e:
            latency_sec = round(time.time() - start_time, 3)
            api_errors += 1
            failed_cases += 1
            case_details.append({
                "id": sample_id,
                "status": "API_ERROR",
                "latency_sec": latency_sec,
                "error": str(e)
            })
            print(f"[X] {sample_id} - API Error ({latency_sec}s): {str(e)}")

    fixed_acc = (fixed_correct_fields / fixed_total_fields * 100) if fixed_total_fields > 0 else 0.0
    sparse_acc = (sparse_correct_fields / sparse_total_fields * 100) if sparse_total_fields > 0 else 0.0

    report = {
        "model": model_name,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_cases_attempted": total_cases,
        "successful_cases": successful_cases,
        "failed_cases": failed_cases,
        "api_errors": api_errors,
        "fixed_10_field_protocol": {
            "cases_fully_correct": fixed_fully_correct_cases,
            "total_cases": total_cases,
            "fields_correct": fixed_correct_fields,
            "total_fields_evaluated": fixed_total_fields,
            "field_accuracy_pct": round(fixed_acc, 2)
        },
        "sparse_field_protocol": {
            "non_empty_cases_fully_correct": sparse_fully_correct_cases,
            "total_non_empty_cases": total_cases - empty_expected_cases,
            "empty_expected_cases": empty_expected_cases,
            "fields_correct": sparse_correct_fields,
            "total_fields_evaluated": sparse_total_fields,
            "field_accuracy_pct": round(sparse_acc, 2)
        },
        "cases": case_details
    }

    os.makedirs(RESULTS_DIR, exist_ok=True)
    safe_model_filename = model_name.replace("/", "_").replace(":", "_")
    output_filepath = os.path.join(RESULTS_DIR, f"eval_v2_{safe_model_filename}.json")

    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n================ EVALUATION SUMMARY ================")
    print(f"Model Evaluated        : {model_name}")
    print(f"Total Cases Attempted  : {total_cases}")
    print(f"Successful API Cases   : {successful_cases}")
    print(f"API Errors             : {api_errors}")
    print("----------------------------------------------------")
    print(f"Fixed 10-Field Protocol : {fixed_correct_fields}/{fixed_total_fields} fields ({fixed_acc:.2f}%) | {fixed_fully_correct_cases}/{total_cases} cases full match")
    print(f"Sparse Field Protocol   : {sparse_correct_fields}/{sparse_total_fields} fields ({sparse_acc:.2f}%) | Empty expected cases: {empty_expected_cases}")
    print(f"Detailed Results Saved : {output_filepath}")
    print("====================================================\n")

    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Gemini Extractor.")
    parser.add_argument("--model", type=str, default=MODEL, help=f"Gemini model identifier (default: {MODEL})")
    args = parser.parse_args()

    run_evaluation(model_name=args.model)
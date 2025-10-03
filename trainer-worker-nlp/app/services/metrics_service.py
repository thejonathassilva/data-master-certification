from typing import List, Tuple, Dict
from sklearn.metrics import f1_score

def macro_f1_intents(y_true: List[str], y_pred: List[str]) -> float:
    labels = sorted(set(y_true + y_pred))
    return float(f1_score(y_true, y_pred, average="macro", labels=labels))

def entity_f1(pred_spans: List[Tuple[str,int,int]], gold_spans: List[Tuple[str,int,int]]) -> float:
    pred_set = set(pred_spans)
    gold_set = set(gold_spans)
    tp = len(pred_set & gold_set)
    fp = len(pred_set - gold_set)
    fn = len(gold_set - pred_set)
    if tp == 0 and (fp + fn) == 0:
        return 1.0
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec  = tp / (tp + fn) if (tp + fn) else 0.0
    if prec + rec == 0:
        return 0.0
    return 2 * prec * rec / (prec + rec)

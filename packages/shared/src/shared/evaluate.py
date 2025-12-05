import pandas as pd

from shared.metrics import compute_precision, compute_recall


def create_evaluation_table(
    ground_truth_df: pd.DataFrame,
    agent_responses_df: pd.DataFrame,
) -> pd.DataFrame:
    evaluation_df = pd.merge(
        ground_truth_df,
        agent_responses_df,
        on=["id", "name"],
        suffixes=("_ground_truth", "_agent_response"),
        how="outer",
        validate="1:1",
    )

    return evaluation_df


def calculate_overall_metrics(evaluation_df: pd.DataFrame) -> dict[str, float]:
    # Among the material changes identified, what is the % correct?
    materiality_precision = compute_precision(
        evaluation_df,
        expected_value_col="latest_yoy_pct_ground_truth",
        extracted_value_col="latest_yoy_pct_agent_response",
    )

    # Among the material changes we expected, what is the % correct?
    materiality_recall = compute_recall(
        evaluation_df,
        expected_value_col="latest_yoy_pct_ground_truth",
        extracted_value_col="latest_yoy_pct_agent_response",
    )

    return {
        "materiality_precision": materiality_precision,
        "materiality_recall": materiality_recall,
    }

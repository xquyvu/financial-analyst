import json

import pandas as pd

from shared.evaluate import calculate_overall_metrics, create_evaluation_table


def test_smoke_evaluate():
    agent_responses: list[pd.DataFrame] = []

    for company_id in (1, 2):
        # We expect the materiality agent to response in JSON lines for each company, so
        # the test data should be one JSON file for each company.
        with open(f"packages/shared/tests/test_data/materiality_response_{company_id}.json") as f:
            material_changes = pd.DataFrame([json.loads(line) for line in f.readlines()]).assign(
                id=company_id
            )

        agent_responses.append(material_changes)

    agent_responses_df = pd.concat(agent_responses, ignore_index=True)

    # We plan to create the ground truth data in a tabular format
    ground_truth_df = pd.read_csv("packages/shared/tests/test_data/materiality_ground_truth.csv")

    evaluation_df = create_evaluation_table(
        ground_truth_df=ground_truth_df,
        agent_responses_df=agent_responses_df,
    )

    metrics = calculate_overall_metrics(evaluation_df)

    assert len(metrics)

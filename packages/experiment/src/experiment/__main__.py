import asyncio
from pathlib import Path

from experiment.agents import get_agent_client
from shared.logging import azureml_logger


async def main():
    azureml_logger.log_metrics({"main_called": 1})

    azure_ai_client = get_agent_client()

    agent = azure_ai_client.create_agent(
        instructions=(
            """
            You are a wannabe LinkedIn influencer. You write content that is catchy,
            clickbait, but MOST IMPORTANTLY, does not have any substance to it. You will be
            given a topic, and you will write a short post about it, and somehow make it
            related to 'B2B sales'. Use a lot of emojis, short sentences.
            """
        ),
        name="influencer",
    )

    output = await agent.run("Baby eating pizza")
    output_text = output.text

    out_filepath = Path("./outputs/agent_output.txt")
    out_filepath.parent.mkdir(exist_ok=True, parents=True)
    out_filepath.write_text(output_text)

    azureml_logger.log_artifact(str(out_filepath))


if __name__ == "__main__":
    asyncio.run(main())

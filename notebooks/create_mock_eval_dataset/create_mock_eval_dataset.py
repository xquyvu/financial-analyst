import asyncio
import itertools
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from types import CoroutineType
from typing import Any

import pandas as pd
from agent_framework import ChatAgent, ChatMessage, DataContent, Role, TextContent
from jinja2 import Environment, FileSystemLoader, Template
from pydantic import BaseModel, Field

from shared.agents import get_agent_client
from shared.llm_utils import get_image_data_urls

# Configure logging to print to terminal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

# Extraction params
PAGES_PER_CALL = 2
TEMPLATE_ENV = Environment(loader=FileSystemLoader(Path(__file__).parent / "prompts"))
SYSTEM_PROMPT_TEMPLATE: Template = TEMPLATE_ENV.get_template("system_prompt.jinja2")
USER_PROMPT_TEMPLATE: Template = TEMPLATE_ENV.get_template("user_prompt.jinja2")

# Paths
SOURCE_DATA_PATH = Path("data/mock/Tesco AR report extracted.pdf")

EXTRACTED_DATASET_DIR = Path("data/mock_eval_dataset")
PARSED_IMAGES_DIR = EXTRACTED_DATASET_DIR / "parsed_images"
DATA_OUTPUT_DIR = EXTRACTED_DATASET_DIR / "extracted_data"

LLM_EXTRACTION_SEMAPHORE = asyncio.Semaphore(10)


@dataclass
class LLMInput:
    image_data_url: str


class Reference(BaseModel):
    file_name: str = Field(..., description="Name of the file containing the reference")
    page_number: int = Field(..., description="Page number in the referred file")


class ReasonForChange(BaseModel):
    reason: str = Field(
        ...,
        description=dedent("""
            A specific, detailed explanation for why the material change occurred. Examples:
            - "Acquisition of new subsidiaries increased total assets"
            - "Restructuring costs led to reduced operating profit"
            - "Currency exchange rate fluctuations impacted international revenue"
        """),
    )
    suporting_text: str = Field(
        ...,
        description=dedent("""
            The actual text extracted from the PDF that supports the stated reason. This should be:
            - A direct quote or close paraphrase from the document
            - Specific enough to validate the reason
            - Include relevant numerical data when available
        """),
    )
    reference: Reference = Field(..., description="Reference to the source of the supporting text")


class MaterialChange(BaseModel):
    material_change: str = Field(
        ...,
        description=dedent("""
            A clear, concise description of the material change observed in the company's financials. This could include:
            - Significant revenue increases or decreases
            - Major changes in profit margins
            - Substantial shifts in asset values
            - Notable changes in debt levels
            - Material changes in operational metrics
        """),
    )
    reasons_for_change: list[ReasonForChange] = Field(
        ...,
        description=dedent(
            """
            List of reasons for the material change. If there are multiple factors, list
            them as separate entries. For example, if the report says "sales increased
            thanks to investment and new product launch, there will be 2 reasons for
            changes entries, which are "sales" and "product launch". """,
        ),
    )


class MaterialChangesReport(BaseModel):
    material_changes: list[MaterialChange] = Field(
        ...,
        description="List of material changes identified in the financial report",
    )


async def call_agent(
    agent: ChatAgent,
    messages: ChatMessage,
) -> MaterialChangesReport:
    await LLM_EXTRACTION_SEMAPHORE.acquire()

    try:
        agent_run_response = await agent.run(
            messages=messages,
            response_format=MaterialChangesReport,
            temperature=0.0,
        )

        output = agent_run_response.value

        if not isinstance(output, MaterialChangesReport):
            raise ValueError("Agent did not return a MaterialChangesReport")

        return output
    finally:
        LLM_EXTRACTION_SEMAPHORE.release()


async def extract_eval_data(
    agent: ChatAgent,
    llm_input_by_page: dict[str, LLMInput],
) -> MaterialChangesReport:
    """Parses Markdown content into a TallySheet object."""

    tasks: list[CoroutineType[Any, Any, MaterialChangesReport]] = []

    available_pages = list(llm_input_by_page.keys())

    for page_numbers_to_extract in itertools.batched(available_pages, PAGES_PER_CALL):
        image_data_urls = [
            llm_input_by_page[page_num].image_data_url for page_num in page_numbers_to_extract
        ]

        messages = ChatMessage(
            role=Role.USER,
            contents=[
                TextContent(text=USER_PROMPT_TEMPLATE.render(file_name=SOURCE_DATA_PATH.stem)),
                *[DataContent(uri=image_data_uri) for image_data_uri in image_data_urls],
            ],
        )

        tasks.append(
            call_agent(
                agent,
                messages,
            )
        )

    material_changes_reports: list[MaterialChangesReport] = await asyncio.gather(*tasks)

    # Combine the results from all the pages
    all_material_changes: list[MaterialChange] = []

    for extracted_material_changes_report in material_changes_reports:
        all_material_changes.extend(extracted_material_changes_report.material_changes)

    return MaterialChangesReport(material_changes=all_material_changes)


async def gather_and_cache_llm_input(
    pdf_input_path: Path,
    parsed_image_dir: Path,
) -> dict[str, LLMInput]:
    """Extracts text and images from the PDF and prepares the input for the LLM extraction"""

    # Convert the PDF to images
    image_data_url_by_page = await get_image_data_urls(pdf_input_path, parsed_image_dir)

    # Gather all inputs to the LLM
    llm_input_by_page = {
        page_num: LLMInput(
            image_data_url=image_data_url_by_page[page_num],
        )
        for page_num in image_data_url_by_page.keys()
    }

    return llm_input_by_page


def to_tabular_format(material_changes_report: MaterialChangesReport) -> pd.DataFrame:
    """Converts the MaterialChangesReport into a tabular format for easier analysis"""

    records = []

    for material_change in material_changes_report.material_changes:
        for reason in material_change.reasons_for_change:
            records.append(
                {
                    "material_change": material_change.material_change,
                    "reason": reason.reason,
                    "supporting_text": reason.suporting_text,
                    "reference_file_name": reason.reference.file_name,
                    "reference_page_number": reason.reference.page_number,
                }
            )

    return pd.DataFrame.from_records(records)


async def main():
    logger.info("Setting up")
    PARSED_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    DATA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    AGENT_CLIENT = get_agent_client(model_deployment_name="gpt-4.1")
    EXTRACTION_AGENT = AGENT_CLIENT.create_agent(
        instructions=SYSTEM_PROMPT_TEMPLATE.render(),
        name="extraction",
    )

    logger.info("Gathering and caching LLM input")
    llm_input_by_page = await gather_and_cache_llm_input(
        SOURCE_DATA_PATH,
        PARSED_IMAGES_DIR,
    )

    logger.info("Extracting evaluation data")
    material_changes_report = await extract_eval_data(
        agent=EXTRACTION_AGENT,
        llm_input_by_page=llm_input_by_page,
    )

    logger.info("Saving output to JSON")
    output_filepath = DATA_OUTPUT_DIR / "material_changes_report.json"
    output_filepath.write_text(material_changes_report.model_dump_json(indent=2))

    logger.info("Saving output to CSV")
    tabular_output_filepath = DATA_OUTPUT_DIR / "material_changes_report.csv"
    material_changes_table = to_tabular_format(material_changes_report)
    material_changes_table.assign(id=SOURCE_DATA_PATH.stem).to_csv(
        tabular_output_filepath, index=False
    )

    shutil.copy(SOURCE_DATA_PATH, EXTRACTED_DATASET_DIR / SOURCE_DATA_PATH.name)


if __name__ == "__main__":
    asyncio.run(main())

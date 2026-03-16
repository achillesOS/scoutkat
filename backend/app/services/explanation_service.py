import json
from pathlib import Path

from app.schemas.explanations import ExplanationOutput


class ExplanationService:
    def __init__(self, prompt_path: Path, schema_path: Path) -> None:
        self.prompt_path = prompt_path
        self.schema_path = schema_path

    def system_prompt(self) -> str:
        return self.prompt_path.read_text()

    def schema(self) -> dict:
        return json.loads(self.schema_path.read_text())

    def validate_output(self, payload: dict) -> ExplanationOutput:
        return ExplanationOutput.model_validate(payload)


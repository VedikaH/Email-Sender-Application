import pandas as pd
from io import StringIO
from typing import List, Dict, Optional
from pydantic import BaseModel

class TemplateData(BaseModel):
    template: str
    subject_template: str
    placeholder_columns: str

class CSVService:
    @staticmethod
    async def process_csv(file_contents: str, template_data: TemplateData) -> List[Dict]:
        df = pd.read_csv(StringIO(file_contents))

        # Validate all required placeholder columns exist
        available_columns = list(df.columns)
        print(available_columns)
        df = pd.read_csv(StringIO(file_contents))

    # Validate all required placeholder columns exist
        available_columns = list(df.columns)
        placeholder_columns = [col.strip() for col in template_data.placeholder_columns.split(",")]

        print(placeholder_columns)
        missing_columns = [col for col in placeholder_columns if col not in available_columns]
        print(missing_columns)
        if missing_columns:
            raise ValueError(f"CSV is missing required columns for template: {', '.join(missing_columns)}")

        # For each row, create a mapping of placeholders to values
        processed_rows = []
        for _, row in df.iterrows():
            template_mapping = {col: str(row[col]) for col in placeholder_columns}
            email_body = template_data.template
            email_subject = template_data.subject_template

            for placeholder, value in template_mapping.items():
                email_body = email_body.replace(f"{{{placeholder}}}", value)
                email_subject = email_subject.replace(f"{{{placeholder}}}", value)

            processed_rows.append({
                "email_content": email_body,
                "email_subject": email_subject,
                "template_data": template_mapping,
                **row.to_dict()
            })

        return processed_rows
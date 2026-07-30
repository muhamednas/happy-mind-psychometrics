from uuid import UUID
import os
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jinja2 import Environment, FileSystemLoader
from app.models.candidate import Candidate
from app.models.candidate_progress import CandidateProgress
from app.models.package import Package


TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


class ReportService:
    @staticmethod
    def generate_report(candidate_name: str, package_title: str, results: list, output_path: str) -> tuple[str, bool]:
        """Generate a branded report. Returns a tuple of (file_path, is_pdf)."""
        template = _env.get_template("report.html")

        html_content = template.render(
            candidate_name=candidate_name,
            package_title=package_title,
            results=results,
            generated_at=datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC"),
            current_year=datetime.utcnow().year,
        )

        try:
            from weasyprint import HTML
            HTML(string=html_content, base_url=f"file://{TEMPLATE_DIR}/").write_pdf(output_path)
            return output_path, True
        except (ImportError, OSError) as e:
            # Fallback to saving as static HTML report
            html_path = output_path.replace(".pdf", ".html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            return html_path, False

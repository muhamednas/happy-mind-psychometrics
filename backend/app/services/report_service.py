import os
from datetime import datetime, timezone
from jinja2 import Environment, FileSystemLoader


TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


class ReportService:
    @staticmethod
    def generate_report_bytes(candidate_name: str, package_title: str, results: list) -> tuple[bytes, bool]:
        """Render the report and return (content_bytes, is_pdf).

        Renders in-memory (no writes to the working directory). Falls back to
        HTML bytes if WeasyPrint's native libraries are unavailable.
        """
        template = _env.get_template("report.html")
        now = datetime.now(timezone.utc)
        html_content = template.render(
            candidate_name=candidate_name,
            package_title=package_title,
            results=results,
            generated_at=now.strftime("%B %d, %Y at %H:%M UTC"),
            current_year=now.year,
        )

        try:
            from weasyprint import HTML

            pdf_bytes = HTML(string=html_content, base_url=f"file://{TEMPLATE_DIR}/").write_pdf()
            return pdf_bytes, True
        except (ImportError, OSError):
            return html_content.encode("utf-8"), False

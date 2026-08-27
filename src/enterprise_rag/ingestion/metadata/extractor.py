import re
from datetime import datetime

from enterprise_rag.domain.metadata import DocumentMetadata


class DocumentMetadataExtractor:
    """Extract structured metadata from document text."""

    VERSION_PATTERN = re.compile(
        r"\bVersion\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)*)",
        re.IGNORECASE,
    )

    EFFECTIVE_DATE_PATTERN = re.compile(
        r"\bEffective\s*[:\-]?\s*"
        r"([A-Za-z]+\s+\d{1,2},\s+\d{4})",
        re.IGNORECASE,
    )

    POLICY_OWNER_PATTERN = re.compile(
    r"\bPolicy\s+Owner\s*[:\-]?\s*(.+?)(?=\s+\d+\.\s|\s*$)",
    re.IGNORECASE,
    )

    def extract(
        self,
        text: str,
    ) -> DocumentMetadata:
        """Extract metadata from document text."""

        return DocumentMetadata(
            document_version=self._extract_version(text),
            effective_date=self._extract_effective_date(
                text
            ),
            policy_owner=self._extract_policy_owner(
                text
            ),
        )

    def _extract_version(
        self,
        text: str,
    ) -> str | None:
        match = self.VERSION_PATTERN.search(text)

        if not match:
            return None

        return match.group(1).strip()

    def _extract_effective_date(
        self,
        text: str,
    ):
        match = self.EFFECTIVE_DATE_PATTERN.search(text)

        if not match:
            return None

        return datetime.strptime(
            match.group(1).strip(),
            "%B %d, %Y",
        ).date()

    def _extract_policy_owner(
        self,
        text: str,
    ) -> str | None:
        marker = re.search(
        r"\bPolicy\s+Owner\s*:",
        text,
        re.IGNORECASE,
    )

        if not marker:
            return None

        value = text[marker.end():].strip()

        # Stop at the beginning of the first numbered section.
        section_marker = re.search(
        r"\s+\d+\.\s+",
        value,
        )

        if section_marker:
            value = value[:section_marker.start()]

        value = value.strip(" |:-")

        value = re.sub(
        r"\s+",
        " ",
        value,
        )

        return value or None
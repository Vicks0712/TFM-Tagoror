from dataclasses import dataclass, asdict


@dataclass
class DocumentMetadata:
    legislature: str
    date: str
    n_ds: str
    p_id: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ProcessedDocument:
    order: int
    text: str
    PK: str
    metadata: DocumentMetadata

    def to_dict(self) -> dict:
        """
        Convert to dictionary, ensuring nested dataclasses are also converted.
        """
        data = asdict(self)
        data["metadata"] = self.metadata.to_dict()
        return data

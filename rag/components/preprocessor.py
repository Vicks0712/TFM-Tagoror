import json
import re
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any
import tiktoken

from rag.config.logger import logger
from rag.databases.qdrant.schemas import ProcessedDocument, DocumentMetadata

tokenizer = tiktoken.get_encoding("o200k_base")
MAX_TOKENS = 30000


class Preprocessor:
    def __init__(self, date_prob: float = 1.0):
        """
        Initializes the custom preprocessor for JSON-formatted documents.
        It processes paragraphs, cleans text, and generates metadata for each document chunk.

        Args:
            date_prob (float): Probability of including the publication date
                               at the beginning of the text (default: 1.0).
        """
        self.date_prob = date_prob

    def run(self, file_path: Path) -> List[ProcessedDocument]:
        """
        Main entry point to process a JSON file containing paragraphs.
        It orchestrates loading, grouping, cleaning, and preparing document chunks.

        Args:
            file_path (Path): Path to the JSON file.

        Returns:
            List[ProcessedDocument]: A list of processed document chunks with metadata.
        """
        try:
            docs = self._load_json(file_path)
            grouped, metadata = self._group_paragraphs(docs)
            processed_docs = self._create_chunks(grouped, metadata)
            logger.info(f"Processed {len(processed_docs)} chunks from {file_path}")
            return processed_docs
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            raise e

    def _load_json(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Loads and parses a JSON file.

        Args:
            file_path (Path): Path to the JSON file.

        Returns:
            List[Dict[str, Any]]: Parsed JSON content.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _group_paragraphs(self, docs: List[Dict[str, Any]]) -> (Dict[str, Dict[int, List[str]]],
                                                                 Dict[str, Dict[str, str]]):
        """
        Groups paragraphs by document ID and paragraph order.

        Args:
            docs (List[Dict[str, Any]]): List of parsed documents.

        Returns:
            tuple:
                - grouped (Dict): Paragraphs grouped by doc_id and order.
                - metadata (Dict): Metadata for each document ID.
        """
        grouped = defaultdict(lambda: defaultdict(list))
        metadata = {}

        for doc in docs:
            doc_id = doc["id_ds"]
            metadata[doc_id] = {
                "legislature": doc["legislatura"],
                "date": doc["f_publicacion"],
                "n_ds": doc["n_ds"]
            }
            for paragraph in doc["parrafos"]:
                order = paragraph["orden"]
                if order == 0:
                    continue  # Skip introductions
                text = paragraph["texto"].strip("'")
                grouped[doc_id][order].append(text)

        return grouped, metadata

    def _create_chunks(
        self,
        grouped: Dict[str, Dict[int, List[str]]],
        metadata: Dict[str, Dict[str, str]]
    ) -> List[ProcessedDocument]:
        """
        Creates document chunks with cleaned text and attached metadata.

        Args:
            grouped (Dict): Grouped paragraphs by document ID and order.
            metadata (Dict): Metadata for each document.

        Returns:
            List[ProcessedDocument]: List of processed document chunks.
        """
        results = []

        for doc_id, orders in grouped.items():
            meta = metadata[doc_id]
            for order, texts in orders.items():
                raw_text = " ".join(texts)
                p_id = self.extract_p_id(texts)

                preprocessed_text = self.remove_new_lines_tabs_extra_spaces(raw_text)
                preprocessed_text = self.maybe_add_date(preprocessed_text, meta["date"], self.date_prob)

                token_count = self.num_tokens(preprocessed_text)
                if token_count > MAX_TOKENS:
                    logger.warning(f"Skipping {doc_id}_{order} due to excessive token count: {token_count}")
                    continue

                doc = ProcessedDocument(
                    order=order,
                    text=preprocessed_text,
                    PK=f"{doc_id}_{order}",
                    metadata=DocumentMetadata(
                        legislature=meta["legislature"],
                        date=meta["date"],
                        n_ds=meta["n_ds"],
                        p_id=p_id
                    )
                )
                results.append(doc)

        return results

    @staticmethod
    def remove_new_lines_tabs_extra_spaces(text: str) -> str:
        """
        Removes newlines, tabs, and extra spaces from the given text.

        Args:
            text (str): The input text.

        Returns:
            str: Cleaned text.
        """
        text = re.sub(r'\n', ' ', text)
        text = re.sub(r'\t', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def maybe_add_date(text: str, date: str, prob: float) -> str:
        """
        Optionally prepends the publication date to the text based on the given probability.

        Args:
            text (str): The original text.
            date (str): The publication date.
            prob (float): Probability of prepending the date.

        Returns:
            str: The text with the date prepended, or the original text.
        """
        import random
        if random.random() < prob:
            return f"{date}: {text}"
        return text

    @staticmethod
    def extract_p_id(texts: List[str]) -> str:
        """
        Extracts the first matching 'p_id' pattern from the list of texts.
        Replace this implementation with your own logic as needed.

        Args:
            texts (List[str]): List of text fragments.

        Returns:
            str: The extracted 'p_id' if found, otherwise None.
        """
        pattern = r"\b\d+L(?:/\w+)+-\d+\b"

        for text in texts:
            cleaned = text.lstrip("·•* ").strip()
            match = re.search(pattern, cleaned)
            if match:
                return match.group()
        return None

    @staticmethod
    def num_tokens(text: str) -> int:
        """
        Counts the number of tokens in the given text.

        Args:
            text (str): The text to analyze.

        Returns:
            int: The number of tokens.
        """
        return len(tokenizer.encode(text))

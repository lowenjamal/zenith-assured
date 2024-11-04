from enum import Enum


class TransactionStatus(Enum):
    processing = "processing"
    not_approved = "not_approved"
    approved = "approved"

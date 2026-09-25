import datetime
import pycountry
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, model_validator

class Transaction(BaseModel):
    date: datetime.date = Field(..., description="The date of the transaction")
    description: str = Field(min_length=1, description="A brief description of the transaction")  
    debit: Decimal | None = Field(default=None, ge=0, description="Money leaving the account, as a positive number. Null if this row is a credit.")
    credit: Decimal | None = Field(default=None, ge=0, description="The credit amount of the transaction")
    balance: Decimal | None = Field(default=None, description="The balance after the transaction")

    @model_validator(mode="after")
    def validate_transaction(self):
        if self.debit is not None and self.credit is not None:
            raise ValueError("A transaction cannot have both debit and credit values")
        if self.debit is None and self.credit is None:
            raise ValueError("A transaction must have either a debit or credit value")
        return self

class BankStatement(BaseModel):
    bank_name: str | None= Field(..., min_length=1, max_length=100, description="The name of the bank")
    account_last_four_digits: str | None = Field(pattern=r"^\d{4}$", min_length=4, max_length=4, description="The last four digits of the account number")
    currency: str = Field(..., min_length=3, max_length=3, description="The currency of the statement")
    period_start: datetime.date = Field(..., description="The start date of the statement period")
    period_end: datetime.date = Field(..., description="The end date of the statement period")
    opening_balance: Decimal  = Field(..., description="The opening balance of the statement")
    closing_balance: Decimal  = Field(..., description="The closing balance of the statement")
    transactions: list[Transaction] = Field(..., description="A list of transactions in the statement")



    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value):
        value = value.upper()

        if not pycountry.currencies.get(alpha_3=value):
            raise ValueError(f"Invalid currency code: {value}")

        return value
    
    @model_validator(mode="after")
    def validate_period(self):
        if self.period_start and self.period_end:
            if self.period_start > self.period_end:
                raise ValueError("Period start date must be before period end date")
        return self
    
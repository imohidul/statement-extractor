import random
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from faker import Faker
from statement_extractor.models import BankStatement


def random_amount(
    rng: random.Random,
    min_cents: int,
    max_cents: int,
) -> Decimal:
    """Return a random amount with two decimal places."""

    cents = rng.randint(min_cents, max_cents)

    return Decimal(f"{cents / 100:.2f}")


def random_description(
    rng: random.Random,
    fake: Faker,
    is_credit: bool,
) -> str:
    """Return a random description string."""

    if is_credit:
        return rng.choice([
            "SALARY",
            f"TRANSFER FROM {fake.name().upper()}",
            f"REFUND {fake.company().upper()}",
        ])

    return rng.choice([
        f"POS {fake.company().upper()}",
        "ATM WITHDRAWAL",
        f"TRANSFER TO {fake.name().upper()}",
        f"BILL PAYMENT {fake.company().upper()}",
    ])


def generate_statement(seed: int) -> BankStatement:
    # 1. RNG + seeded Faker
    rng = random.Random(seed)

    fake = Faker()
    fake.seed_instance(seed)

    # 2. Pick currency, month, opening balance
    currency = rng.choice(["USD", "EUR", "GBP"])

    year = rng.randint(2020, 2026)
    month = rng.randint(1, 12)

    opening_balance = random_amount(
        rng,
        100_000,
        1_000_000,
    )

    # 3. Make 15–40 sorted dates inside the month
    transaction_count = rng.randint(15, 40)

    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)

    first_day = date(year, month, 1)

    days_in_month = (next_month - first_day).days

    dates = sorted(
        date(
            year,
            month,
            rng.randint(1, days_in_month),
        )
        for _ in range(transaction_count)
    )

    # 4. Generate transactions
    transactions = []
    running_balance = opening_balance

    for transaction_date in dates:

        is_credit = rng.random() < 0.2

        if is_credit:
            amount = random_amount(rng, 50_000, 300_000)   # 500.00 to 3,000.00
        else:
            amount = random_amount(rng, 100, 30_000)       # 1.00 to 300.00

        description = random_description(
            rng,
            fake,
            is_credit,
        )

        if is_credit:
            running_balance += amount

            transactions.append({
                "date": transaction_date,
                "description": description,
                "credit": amount,
                "debit": None,
                "balance": running_balance,
            })

        else:
            running_balance -= amount

            transactions.append({
                "date": transaction_date,
                "description": description,
                "credit": None,
                "debit": amount,
                "balance": running_balance,
            })

    # 5. Closing balance
    closing_balance = running_balance

    #fake bank names
    bank_name=rng.choice(["Synthetic Bank", "Example Trust Bank", "Demo Savings Bank"]),

    # 6. Return BankStatement
    return BankStatement(
        bank_name=bank_name[rng.randint(0, len(bank_name) - 1)],
        account_last_four_digits=f"{rng.randint(0, 9999):04d}",
        period_start=first_day,
        period_end=next_month - timedelta(days=1),
        currency=currency,
        opening_balance=opening_balance,
        closing_balance=closing_balance,
        transactions=transactions,
    )


if __name__ == "__main__":
    output_dir = Path("data/synthetic")
    output_dir.mkdir(parents=True, exist_ok=True)

    for seed in range(1, 6):
        statement = generate_statement(seed)
        path = output_dir / f"stmt_{seed:04d}.json"
        path.write_text(statement.model_dump_json(indent=2))
        print(f"wrote {path}  ({len(statement.transactions)} transactions)")
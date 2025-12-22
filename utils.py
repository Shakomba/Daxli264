import secrets
from datetime import datetime

def generate_join_code(length: int = 8) -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(secrets.choice(alphabet) for _ in range(length))

def current_month_yyyy_mm() -> str:
    return datetime.now().strftime("%Y-%m")

def format_iqd(n: float | int) -> str:
    try:
        n_int = int(round(n))
    except Exception:
        n_int = 0
    return f"{n_int:,} IQD"

def compute_net_balances(users, expenses, participants_map):
    """
    Returns net dict: user_id -> net_iqd (positive = is owed, negative = owes)
    Splits each expense equally among selected participants, using integer-safe splitting:
      share_floor = amount // n
      remainder = amount % n
      first 'remainder' participants pay +1 IQD
    """
    paid = {u.id: 0 for u in users}
    consumed = {u.id: 0 for u in users}

    # stable order for remainder distribution
    for e in expenses:
        paid[e.payer_id] += e.amount_iqd
        parts = sorted(participants_map.get(e.id, []))
        n = len(parts)
        if n <= 0:
            continue

        share_floor = e.amount_iqd // n
        remainder = e.amount_iqd % n
        for idx, uid in enumerate(parts):
            share = share_floor + (1 if idx < remainder else 0)
            consumed[uid] += share

    net = {uid: paid[uid] - consumed[uid] for uid in paid.keys()}
    return net

def simplify_debts(net_by_user_id):
    """
    Given net balances:
      positive => should receive
      negative => should pay
    Produce transfers: list of (from_id, to_id, amount_iqd)
    """
    creditors = [(uid, amt) for uid, amt in net_by_user_id.items() if amt > 0]
    debtors = [(uid, -amt) for uid, amt in net_by_user_id.items() if amt < 0]

    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1], reverse=True)

    transfers = []
    i = j = 0
    while i < len(debtors) and j < len(creditors):
        d_uid, d_amt = debtors[i]
        c_uid, c_amt = creditors[j]
        pay = min(d_amt, c_amt)
        if pay > 0:
            transfers.append((d_uid, c_uid, pay))
            d_amt -= pay
            c_amt -= pay

        if d_amt == 0:
            i += 1
        else:
            debtors[i] = (d_uid, d_amt)

        if c_amt == 0:
            j += 1
        else:
            creditors[j] = (c_uid, c_amt)

    return transfers

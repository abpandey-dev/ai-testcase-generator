# API: Create EMI payment

`POST /api/v1/loans/{loanId}/payments`

Headers: `Authorization: Bearer <token>` (customer token; a customer may only pay their own loans)

Request body:

```json
{
  "amount": 5250.00,
  "currency": "INR",
  "method": "UPI",
  "idempotencyKey": "b1f7c2e0-..."
}
```

Rules:
- `amount` must be > 0 and <= outstanding balance, with at most 2 decimal places.
- `currency` must be `INR`.
- `method` is one of `UPI`, `NETBANKING`, `DEBIT_CARD`.
- Repeating a request with the same `idempotencyKey` within 24 hours returns the original payment instead of creating a new one.

Responses:
- `201 Created` with `{ "paymentId", "status": "PENDING" }`
- `400` for validation errors, `401` without a valid token, `403` for another customer's loan, `404` for an unknown loan, `409` if the loan is already closed.

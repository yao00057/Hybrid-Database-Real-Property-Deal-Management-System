# Hybrid Database Real Property Deal Management System
## Using Python, MongoDB, and MySQL

---

## 1. Project Title

**Hybrid Database Real Property Deal Management System Using Python, MongoDB, and MySQL**

---

## 2. Project Background & Motivation

Real property transactions involve multiple stakeholders, complex workflows, diverse data structures, and strict financial and legal requirements. In a single property deal, participants may include:

- Buyer
- Seller
- Buyer Lawyer
- Seller Lawyer
- Buyer Agent
- Seller Agent

Additionally, properties can be categorized as **residential** or **commercial**, each with significantly different attributes.

### The Challenge

Traditional relational databases struggle with this level of variability without introducing:
- Excessive joins
- Nullable fields
- Frequent schema changes

Conversely, NoSQL databases such as MongoDB offer flexibility but lack strong constraint enforcement required for financial accuracy.

### The Solution

This project proposes a **hybrid database architecture** using **MongoDB + MySQL**, implemented with **Python**, to balance flexibility, scalability, and data integrity.

---

## 3. Project Objectives

The objectives of this project are to:

1. Design a real-world property deal management system
2. Use MongoDB to manage flexible, schema-variant data
3. Use MySQL to handle financial and strongly constrained data
4. Implement the system using Python-based backend technologies
5. Demonstrate best practices in hybrid database architecture
6. Ensure data consistency, auditability, and maintainability

---

## 4. System Scope

### In Scope

| Feature | Description |
|---------|-------------|
| User Role Management | Buyers, sellers, agents, lawyers |
| Property Management | Residential and commercial properties |
| Deal Lifecycle Management | Full workflow from listing to closing |
| Financial Transaction Tracking | Deposits, payments, trust accounts |
| Secure Data Storage | Encrypted, role-based access |
| RESTful API | Complete API implementation |

### Out of Scope

- Payment gateway integration
- Government land registry integration
- Advanced AI valuation models

---

## 5. System Architecture Overview

The system follows a **three-tier architecture** with a hybrid data layer.

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│              Vue 3 + Element Plus + Vite                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│                  FastAPI (Python)                            │
│         Business Logic, Validation, Workflow Control         │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│        MongoDB          │     │         MySQL           │
│   Flexible Domain Data  │     │   Financial & Audit     │
│  - Users & Roles        │     │  - Transactions         │
│  - Properties           │     │  - Trust Accounts       │
│  - Deal Workflows       │     │  - Audit Logs           │
└─────────────────────────┘     └─────────────────────────┘
```

---

## 6. Why MongoDB Is Well-Suited for This System

### 6.1 Flexible User Roles

Each participant role has different attributes. MongoDB allows role-specific fields without schema redesign.

```json
{
  "role": "buyer_agent",
  "name": "Jane Smith",
  "license_number": "RECO-12345",
  "brokerage": "ABC Realty"
}
```

### 6.2 Property Type Variability

Residential and commercial properties have different data requirements.

```json
{
  "type": "commercial",
  "attributes": {
    "zoning": "C2",
    "cap_rate": 6.3,
    "lease_terms": "5 years"
  }
}
```

MongoDB handles this naturally through document-based storage.

### 6.3 Deal-Centric Modeling

A property deal naturally aggregates multiple participants and workflow states.

```json
{
  "property_id": "...",
  "participants": {
    "buyer": "...",
    "seller": "...",
    "buyer_lawyer": "...",
    "seller_lawyer": "..."
  },
  "status": "Conditional",
  "conditions": ["Financing", "Inspection"]
}
```

This reduces complex joins and improves performance for deal-oriented queries.

### 6.4 Rapid Evolution

Real estate regulations, business rules, and workflows change frequently. MongoDB allows:

- Minimal schema migrations
- Faster iteration
- Easier extension of data models

---

## 7. MongoDB Limitations in Financial & Legal Domains

Despite its strengths, MongoDB has limitations:

### 7.1 Weak Native Constraint Enforcement

- No foreign key enforcement
- Cross-document constraints are not guaranteed
- Referential integrity depends on application logic

### 7.2 Financial Data Risks

- Ledger-style data requires strict consistency
- Partial updates can lead to invalid financial states if misused
- Auditing requires manual implementation

### 7.3 Compliance & Audit Challenges

- No native immutable rows
- No built-in accounting safeguards
- Requires custom history tracking

---

## 8. Why MySQL Is Used Alongside MongoDB

MySQL is used for financial and strongly constrained data, such as:

- Deposits
- Trust account balances
- Payments
- Transaction histories
- Audit logs

### Key Advantages of MySQL

| Feature | Benefit |
|---------|---------|
| ACID-compliant transactions | Data consistency guaranteed |
| Foreign key enforcement | Referential integrity |
| CHECK constraints | Business rule enforcement |
| Strong data typing | Prevents invalid data |
| Mature auditing | Compliance support |

### Example MySQL Table

```sql
CREATE TABLE transactions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  deal_id VARCHAR(50) NOT NULL,
  amount DECIMAL(12,2) CHECK (amount > 0),
  transaction_type ENUM('deposit', 'payment'),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

This ensures financial correctness at the database level, not just in application code.

---

## 9. Hybrid Data Strategy

| Data Category | Database | Reason |
|---------------|----------|--------|
| Users & Roles | MongoDB | Flexible schema for different role types |
| Property Details | MongoDB | Variable attributes per property type |
| Deal Workflow | MongoDB | Complex nested documents, frequent changes |
| Financial Records | MySQL | ACID compliance, strict constraints |
| Audit Logs | MySQL | Immutability, compliance requirements |

This approach combines **flexibility + safety**, commonly used in real production systems.

---

## 10. Why Python Is the Best Choice

### 10.1 Excellent Database Support

- **PyMongo / Motor** for MongoDB
- **SQLAlchemy / aiomysql** for MySQL

### 10.2 Rapid Development

- Clear syntax
- Faster prototyping
- Lower development overhead

### 10.3 Strong Web Framework Ecosystem

- **FastAPI**: High performance, built-in validation, auto-generated docs

### 10.4 Business Logic & Validation

Python excels at:
- Workflow orchestration
- Data validation (Pydantic)
- Transaction coordination across databases

---

## 11. Security & Data Integrity Considerations

- Environment-based credential management (`.env` files)
- Input validation at API level (Pydantic)
- MongoDB transactions for critical updates
- MySQL transactions for financial operations
- Role-based access control
- Audit logging for sensitive operations

---

## 12. Cross-Database Data Consistency Strategy

### 12.1 The Dual-Write Problem

In a hybrid database architecture, one of the biggest challenges is maintaining data consistency when a single business operation requires writes to **both** MySQL and MongoDB.

**Example Scenario:**
```
User pays a deposit for a property deal:
1. MySQL: Record transaction in `transactions` table ✓
2. MongoDB: Update deal.status to "Deposit Paid" ✗ (fails due to network error)

Result: Money is deducted but deal status is inconsistent!
```

This is known as the **Dual-Write Problem** — a classic distributed systems challenge.

### 12.2 Application-Level Compensation Strategy

For this academic project, we implement an **Application-Level Compensation Mechanism** rather than heavy solutions like Kafka or Two-Phase Commit (2PC).

**Design Principles:**

1. **MySQL First, MongoDB Second**
   - Always perform MySQL operations first (financial data is harder to rollback)
   - MongoDB operations follow after MySQL commit succeeds

2. **Explicit Rollback on Failure**
   - If MongoDB operation fails, explicitly rollback MySQL changes
   - Log the failure for manual review if rollback also fails

3. **Idempotency Keys**
   - Use unique transaction IDs to prevent duplicate operations
   - Enable safe retries without side effects

**Compensation Flow Diagram:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Transaction Flow                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   START TRANSACTION                                              │
│         │                                                        │
│         ▼                                                        │
│   ┌─────────────┐                                                │
│   │ MySQL Write │ ──── FAIL ────→ Return Error                   │
│   └─────────────┘                                                │
│         │                                                        │
│       SUCCESS                                                    │
│         │                                                        │
│         ▼                                                        │
│   ┌──────────────┐                                               │
│   │ MongoDB Write │ ──── FAIL ────→ Rollback MySQL               │
│   └──────────────┘                      │                        │
│         │                               ▼                        │
│       SUCCESS                    Log Error + Alert               │
│         │                                                        │
│         ▼                                                        │
│   COMMIT & RETURN SUCCESS                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Pseudo-code Example:**

```python
async def record_deposit(deal_id: str, amount: float) -> Result:
    mysql_session = get_mysql_session()

    try:
        # Step 1: MySQL operation (financial record)
        transaction = Transaction(
            deal_id=str(deal_id),  # Explicit ObjectId → str conversion
            amount=amount,
            transaction_type="deposit"
        )
        mysql_session.add(transaction)
        await mysql_session.commit()

        try:
            # Step 2: MongoDB operation (deal status update)
            await mongodb.deals.update_one(
                {"_id": ObjectId(deal_id)},
                {"$set": {"status": "deposit_paid", "updated_at": datetime.utcnow()}}
            )
            return Result.success()

        except Exception as mongo_error:
            # Step 3: Compensation - Rollback MySQL
            await mysql_session.delete(transaction)
            await mysql_session.commit()

            # Log for manual review
            await log_compensation_event(deal_id, "deposit", mongo_error)

            raise ConsistencyError("MongoDB update failed, MySQL rolled back")

    except SQLAlchemyError as mysql_error:
        await mysql_session.rollback()
        raise DatabaseError("MySQL operation failed")
```

### 12.3 Participant Data as Snapshots

**Design Decision:** Deal participant information is stored as **point-in-time snapshots**, not live references.

**Rationale:**

| Approach | Pros | Cons |
|----------|------|------|
| **Live Reference** | Always current data | Legal issues (contract shows wrong name) |
| **Snapshot** ✓ | Legally accurate, audit-friendly | May show "outdated" info |

**Implementation:**

When a deal is created, participant information is **copied** from the users collection:

```json
{
  "_id": ObjectId("..."),
  "property_id": ObjectId("..."),
  "participants_snapshot": {
    "buyer": {
      "user_id": ObjectId("..."),
      "name": "John Doe",           // Snapshot at deal creation
      "email": "john@example.com",  // Snapshot at deal creation
      "phone": "555-1234"           // Snapshot at deal creation
    },
    "seller": {
      "user_id": ObjectId("..."),
      "name": "Jane Smith",
      "email": "jane@example.com",
      "phone": "555-5678"
    }
  },
  "snapshot_timestamp": ISODate("2024-01-15T10:30:00Z"),
  "status": "active"
}
```

**Benefits:**

1. **Legal Compliance** — Contract reflects information at signing time
2. **Audit Trail** — Historical accuracy preserved
3. **Performance** — No joins needed to display deal information
4. **Consistency** — Deal data is self-contained

### 12.4 ObjectId Type Safety

MongoDB uses `ObjectId` (24-character hex string), while MySQL uses `VARCHAR(50)` for `deal_id`.

**Potential Issue:**
```python
# This will cause a type error in MySQL
mysql_transaction.deal_id = mongodb_deal["_id"]  # ObjectId object, not string!
```

**Solution:** Explicit type conversion at the service layer boundary:

```python
# Always convert ObjectId to string when crossing database boundaries
deal_id_str = str(mongodb_deal["_id"])
mysql_transaction.deal_id = deal_id_str
```

This is enforced through Pydantic schema configuration (see Technical Architecture document).

---

## 13. Expected Outcomes

1. A realistic property deal management system
2. Demonstrated understanding of NoSQL vs SQL trade-offs
3. Proper use of hybrid database architecture
4. Portfolio-ready, interview-ready project
5. Industry-aligned design decisions

---

## 14. Future Enhancements

- User authentication & authorization (JWT)
- Document management (contracts, agreements)
- Workflow automation
- Analytics dashboard
- Regulatory compliance extensions

---

## 15. Conclusion

This project demonstrates how MongoDB and MySQL can be effectively combined to support a real property deal system. MongoDB provides flexibility for diverse roles and property types, while MySQL ensures financial accuracy and strong data integrity. Python serves as an ideal integration layer, offering rapid development, robust validation, and maintainable backend logic.

This hybrid approach reflects **real-world enterprise system design**, balancing scalability, flexibility, and reliability.

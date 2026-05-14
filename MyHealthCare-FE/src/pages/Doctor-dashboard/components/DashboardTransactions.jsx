// src/Doctor/components/DashboardTransactions.jsx
import React from "react";

export default function DashboardTransactions({ transactions, variant }) {
  const containerClass =
    "dd-transactions-card " +
    (variant === "desktop"
      ? "dd-transactions-card--desktop"
      : "dd-transactions-card--mobile");

  return (
    <div className={containerClass}>
      <div className="dd-card-header">
        <h3>Recent Transactions</h3>
      </div>
      <ul className="dd-transaction-list">
        {transactions.map((tx) => (
          <li key={tx.id}>
            <div
              className={
                "dd-transaction-icon " +
                (tx.type === "card"
                  ? "dd-transaction-icon--card"
                  : tx.type === "paypal"
                  ? "dd-transaction-icon--paypal"
                  : "dd-transaction-icon--user")
              }
            />
            <div className="dd-transaction-main">
              <p className="dd-transaction-title">{tx.title}</p>
              <p className="dd-transaction-meta">{tx.date}</p>
            </div>
            <div
              className={
                "dd-transaction-amount " +
                (tx.positive
                  ? "dd-transaction-amount--pos"
                  : "dd-transaction-amount--neg")
              }
            >
              {tx.amount}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

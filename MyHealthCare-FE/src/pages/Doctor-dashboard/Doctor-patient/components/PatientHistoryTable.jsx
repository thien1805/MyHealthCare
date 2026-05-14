import React from "react";

export default function PatientHistoryTable({ history }) {
  return (
    <section className="patient-view-section">
      <h2 className="patient-subtitle">History</h2>

      <div className="patient-history-wrapper">
        <table className="patient-history-table">
          <thead>
            <tr>
              <th>Type</th>
              <th>Bill type</th>
              <th>Title</th>
              <th>DATE</th>
              <th>Invoice</th>
              <th>STATUS</th>
            </tr>
          </thead>
          <tbody>
            {history.map((row) => (
              <tr key={row.id}>
                <td>{row.type}</td>
                <td>{row.billType}</td>
                <td>{row.title}</td>
                <td>{row.date}</td>
                <td>{row.invoice}</td>
                <td>
                  {row.status === "-" ? (
                    "-"
                  ) : (
                    <span
                      className={
                        "status-pill status-pill--" + row.statusType
                      }
                    >
                      {row.status}
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

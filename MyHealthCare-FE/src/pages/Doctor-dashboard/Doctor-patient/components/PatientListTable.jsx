import React from "react";

export default function PatientListTable({
  patients,
  search = "",
  onSearchChange,
}) {
  return (
    <div className="patient-card">
      <div className="patient-header-row">
        <h2 className="patient-title">Patient List</h2>

        <div className="patient-header-right">
          <div className="patient-search-input">
            <span className="icon">🔍</span>
            <input
              placeholder="Search patient name"
              value={search}
              onChange={(e) => onSearchChange?.(e.target.value)}
            />
          </div>
        </div>
      </div>

      <div className="patient-table-wrapper">
        <table className="patient-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Gender</th>
              <th>Number</th>
              <th>Age</th>
              <th>Email address</th>
              <th>Medical record</th>
            </tr>
          </thead>
          <tbody>
            {patients.map((p) => (
              <tr key={p.id}>
                <td>
                  <div className="patient-name-cell">
                    <div
                      className="patient-avatar"
                      style={{ background: p.avatarColor }}
                    />
                    <span>{p.name}</span>
                  </div>
                </td>
                <td>
                  <span
                    className={
                      "gender-pill " +
                      (p.gender === "Male"
                        ? "gender-pill--male"
                        : "gender-pill--female")
                    }
                  >
                    {p.gender}
                  </span>
                </td>
                <td>{p.number}</td>
                <td>{p.age}</td>
                <td>{p.email}</td>
                <td>
                  <div className="patient-record-cell">
                    {p.medicalRecords && p.medicalRecords.length > 0 ? (
                      <div className="patient-record-scroll">
                        {p.medicalRecords.map((rec, idx) => (
                          <div key={idx} className="patient-record-item">
                            {rec.title || rec.diagnosis || `Record #${idx + 1}`}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <span className="patient-record-empty">No record</span>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="patient-footer">
          <span>Showing 1–09 of 78</span>
          <div className="patient-pagination">
            <button className="pager-btn">{"<"}</button>
            <button className="pager-btn">{">"}</button>
          </div>
        </div>
      </div>
    </div>
  );
}

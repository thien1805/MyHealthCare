import { useState } from "react";

export function useDoctorSettings() {
  const [hud, setHud] = useState({
    transactions: true,
    appointments: true,
    prescriptions: false,
    reports: false,
    patients: false,
    calendar: false,
    inbox: false,
    store: false,
  });

  const [currency, setCurrency] = useState("USD");
  const [timezone, setTimezone] = useState(
    "(GMT-12:00) International Date Line West"
  );

  const toggleHud = (key) => {
    setHud((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSave = (e) => {
    e.preventDefault();
    console.log("Settings:", { hud, currency, timezone });
    alert("Saved settings (demo)");
  };

  return { hud, toggleHud, currency, setCurrency, timezone, setTimezone, handleSave };
}

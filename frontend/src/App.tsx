import { Routes, Route } from "react-router-dom";
import { AppLayout } from "@/components/layout/AppLayout";
import Landing from "@/pages/Landing";
import Setup from "@/pages/Setup";
import Dashboard from "@/pages/Dashboard";
import Coaching from "@/pages/Coaching";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route element={<AppLayout />}>
        <Route path="/setup" element={<Setup />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/coaching" element={<Coaching />} />
      </Route>
    </Routes>
  );
}

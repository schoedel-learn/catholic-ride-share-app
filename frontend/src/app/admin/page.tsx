"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  listDrivers,
  verifyDriver,
  getParishStats,
  type DriverProfileResponse,
  type ParishStats,
} from "@/lib/api";
import { useAuth } from "@/lib/auth";
import Navbar from "@/components/Navbar";

export default function AdminDashboardPage() {
  const router = useRouter();
  const { user, token, loading } = useAuth();
  const [drivers, setDrivers] = useState<DriverProfileResponse[]>([]);
  const [stats, setStats] = useState<ParishStats | null>(null);
  const [dataLoading, setDataLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  
  // Edit state
  const [editingDriver, setEditingDriver] = useState<number | null>(null);
  const [editForm, setEditForm] = useState({
    background_check_status: "",
    training_completed_date: "",
    training_expiration_date: "",
    admin_notes: "",
  });
  const [saveLoading, setSaveLoading] = useState(false);

  const isGlobalAdmin = user?.role === "admin";
  const isCoordinator = user?.role === "coordinator";
  const hasAccess = isGlobalAdmin || isCoordinator;

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    } else if (!loading && user && !hasAccess) {
      router.push("/dashboard");
    }
  }, [loading, user, router, hasAccess]);

  useEffect(() => {
    if (!token || !hasAccess) return;

    const loadData = async () => {
      setDataLoading(true);
      setError(null);
      try {
        const [driversList, parishStats] = await Promise.all([
          listDrivers(token),
          getParishStats(token),
        ]);
        setDrivers(driversList);
        setStats(parishStats);
      } catch (err) {
        setError((err as Error).message || "Failed to load data.");
      } finally {
        setDataLoading(false);
      }
    };

    void loadData();
  }, [token, hasAccess]);

  const handleEditClick = (driver: DriverProfileResponse) => {
    setEditingDriver(driver.user_id);
    
    const formatDate = (dateString?: string | null) => {
      if (!dateString) return "";
      return new Date(dateString).toISOString().split('T')[0];
    };
    
    setEditForm({
      background_check_status: driver.background_check_status || "pending",
      training_completed_date: formatDate(driver.training_completed_date),
      training_expiration_date: formatDate(driver.training_expiration_date),
      admin_notes: driver.admin_notes || "",
    });
  };

  const handleCancelEdit = () => {
    setEditingDriver(null);
  };

  const handleSaveDriver = async (userId: number) => {
    if (!token) return;
    setSaveLoading(true);
    setError(null);
    setMessage(null);

    try {
      // Build payload — coordinators CANNOT send background_check_status
      const payload: Record<string, unknown> = {
        training_completed_date: editForm.training_completed_date 
          ? new Date(editForm.training_completed_date).toISOString() 
          : null,
        training_expiration_date: editForm.training_expiration_date
          ? new Date(editForm.training_expiration_date).toISOString()
          : null,
        admin_notes: editForm.admin_notes,
      };

      // Only admins include background_check_status
      if (isGlobalAdmin) {
        payload.background_check_status = editForm.background_check_status;
      }

      const updated = await verifyDriver(token, userId, payload as Parameters<typeof verifyDriver>[2]);
      
      setDrivers((prev) => 
        prev.map((drv) => (drv.user_id === userId ? updated : drv))
      );
      
      setEditingDriver(null);
      setMessage("Driver record updated.");
    } catch (err) {
      setError((err as Error).message || "Failed to update driver.");
    } finally {
      setSaveLoading(false);
    }
  };

  if (loading || !user || !hasAccess) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-100">
        <p className="text-sm text-slate-300">Checking permissions...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <Navbar />
      <div className="mx-auto max-w-6xl px-4 py-8 space-y-6">
        <header className="space-y-1">
          <div className="flex items-center gap-2">
            <p className="text-xs text-slate-400">
              {isGlobalAdmin ? "Global Administration" : "Parish Coordination"}
            </p>
            {isCoordinator && (
              <span className="rounded-full bg-blue-900/40 text-blue-300 px-2 py-0.5 text-[10px] font-medium uppercase">
                Coordinator
              </span>
            )}
          </div>
          <h1 className="text-2xl font-semibold tracking-tight">
            {isGlobalAdmin ? "Volunteer Dashboard" : "Parish Dashboard"}
          </h1>
          <p className="text-sm text-slate-400">
            {isGlobalAdmin
              ? "Review and vet drivers, update background check statuses, and manage safe environment training."
              : "Monitor your parish drivers, update training records, and view ride activity. Background check status changes require a diocesan admin."}
          </p>
        </header>

        {error && (
          <div
            className="rounded-md bg-red-900/30 border border-red-700 px-3 py-2 text-xs text-red-200"
            role="alert"
          >
            {error}
          </div>
        )}
        {message && (
          <div className="rounded-md bg-emerald-900/30 border border-emerald-700 px-3 py-2 text-xs text-emerald-200">
            {message}
          </div>
        )}

        {/* Stats cards */}
        {stats && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4 text-center">
              <p className="text-2xl font-bold text-slate-100">{stats.total_drivers}</p>
              <p className="text-[10px] text-slate-400 uppercase tracking-wide mt-1">Total Drivers</p>
            </div>
            <div className="rounded-lg border border-emerald-800/50 bg-emerald-950/20 p-4 text-center">
              <p className="text-2xl font-bold text-emerald-400">{stats.verified_drivers}</p>
              <p className="text-[10px] text-slate-400 uppercase tracking-wide mt-1">Verified</p>
            </div>
            <div className="rounded-lg border border-amber-800/50 bg-amber-950/20 p-4 text-center">
              <p className="text-2xl font-bold text-amber-400">{stats.pending_drivers}</p>
              <p className="text-[10px] text-slate-400 uppercase tracking-wide mt-1">Pending</p>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4 text-center">
              <p className="text-2xl font-bold text-slate-100">{stats.completed_rides}</p>
              <p className="text-[10px] text-slate-400 uppercase tracking-wide mt-1">Completed Rides</p>
            </div>
          </div>
        )}

        {/* Coordinator permissions notice */}
        {isCoordinator && (
          <div className="rounded-md border border-blue-800/40 bg-blue-950/20 px-4 py-3 text-xs text-blue-200/80">
            <strong className="text-blue-300">Coordinator Access:</strong> You can view drivers in your assigned parishes, update safe environment training dates, and add notes. To change a driver&apos;s background check status, contact your diocesan administrator.
          </div>
        )}

        <section className="rounded-xl border border-slate-800 bg-slate-900/70 p-4 space-y-4 overflow-hidden">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-200">
              {isGlobalAdmin ? "All Registered Drivers" : "Parish Drivers"}
            </h2>
            {dataLoading && <span className="text-[10px] text-slate-400">Loading...</span>}
          </div>

          {!dataLoading && drivers.length === 0 ? (
            <p className="text-xs text-slate-500 py-4 text-center">No drivers found.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950/50 text-slate-400">
                  <tr>
                    <th className="px-3 py-2 font-medium">Driver ID / User ID</th>
                    <th className="px-3 py-2 font-medium">Vehicle</th>
                    <th className="px-3 py-2 font-medium">BGC Status</th>
                    <th className="px-3 py-2 font-medium">Safe Env Trained</th>
                    <th className="px-3 py-2 font-medium">Safe Env Exp</th>
                    <th className="px-3 py-2 font-medium">Admin Notes</th>
                    <th className="px-3 py-2 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {drivers.map((driver) => {
                    const isEditing = editingDriver === driver.user_id;
                    return (
                      <tr key={driver.id} className="hover:bg-slate-800/30">
                        <td className="px-3 py-3 font-semibold text-slate-200">
                          {driver.id} / #{driver.user_id}
                        </td>
                        <td className="px-3 py-3">
                          {driver.vehicle_make} {driver.vehicle_model} {driver.vehicle_year ? `(${driver.vehicle_year})` : ""}
                        </td>
                        
                        {isEditing ? (
                          <>
                            <td className="px-3 py-2">
                              {isGlobalAdmin ? (
                                <select 
                                  value={editForm.background_check_status}
                                  onChange={(e) => setEditForm({ ...editForm, background_check_status: e.target.value })}
                                  className="block w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                                >
                                  <option value="pending">Pending</option>
                                  <option value="approved">Approved</option>
                                  <option value="rejected">Rejected</option>
                                </select>
                              ) : (
                                <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium uppercase tracking-wide ${
                                  driver.background_check_status === 'approved' ? 'bg-emerald-900/50 text-emerald-400' :
                                  driver.background_check_status === 'rejected' ? 'bg-red-900/50 text-red-400' :
                                  'bg-amber-900/50 text-amber-400'
                                }`}>
                                  {driver.background_check_status}
                                </span>
                              )}
                            </td>
                            <td className="px-3 py-2">
                              <input 
                                type="date"
                                value={editForm.training_completed_date}
                                onChange={(e) => setEditForm({ ...editForm, training_completed_date: e.target.value })}
                                className="block w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                              />
                            </td>
                            <td className="px-3 py-2">
                              <input 
                                type="date"
                                value={editForm.training_expiration_date}
                                onChange={(e) => setEditForm({ ...editForm, training_expiration_date: e.target.value })}
                                className="block w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                              />
                            </td>
                            <td className="px-3 py-2">
                              <input 
                                type="text"
                                value={editForm.admin_notes}
                                onChange={(e) => setEditForm({ ...editForm, admin_notes: e.target.value })}
                                placeholder="Notes..."
                                className="block w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                              />
                            </td>
                            <td className="px-3 py-2 text-right space-x-2 whitespace-nowrap">
                              <button
                                type="button"
                                disabled={saveLoading}
                                onClick={handleCancelEdit}
                                className="rounded text-slate-400 hover:text-slate-200 px-2 py-1 border border-transparent disabled:opacity-50"
                              >
                                Cancel
                              </button>
                              <button
                                type="button"
                                disabled={saveLoading}
                                onClick={() => handleSaveDriver(driver.user_id)}
                                className="rounded bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-semibold px-2 py-1 disabled:opacity-50"
                              >
                                {saveLoading ? "Saving" : "Save"}
                              </button>
                            </td>
                          </>
                        ) : (
                          <>
                            <td className="px-3 py-3">
                              <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium uppercase tracking-wide ${
                                driver.background_check_status === 'approved' ? 'bg-emerald-900/50 text-emerald-400' :
                                driver.background_check_status === 'rejected' ? 'bg-red-900/50 text-red-400' :
                                'bg-amber-900/50 text-amber-400'
                              }`}>
                                {driver.background_check_status}
                              </span>
                            </td>
                            <td className="px-3 py-3">
                              {driver.training_completed_date 
                                ? new Date(driver.training_completed_date).toLocaleDateString()
                                : <span className="text-slate-500">None</span>
                              }
                            </td>
                            <td className="px-3 py-3">
                              {driver.training_expiration_date 
                                ? new Date(driver.training_expiration_date).toLocaleDateString()
                                : <span className="text-slate-500">None</span>
                              }
                            </td>
                            <td className="px-3 py-3 truncate max-w-[150px]" title={driver.admin_notes || ""}>
                              {driver.admin_notes || <span className="text-slate-500">None</span>}
                            </td>
                            <td className="px-3 py-3 text-right">
                              <button
                                type="button"
                                onClick={() => handleEditClick(driver)}
                                className="text-emerald-400 hover:text-emerald-300 font-medium"
                              >
                                {isGlobalAdmin ? "Verify / Edit" : "Update Training"}
                              </button>
                            </td>
                          </>
                        )}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}

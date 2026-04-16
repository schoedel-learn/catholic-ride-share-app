/**
 * API client for Catholic Ride Share backend
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Types
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string | null;
  role: "rider" | "driver" | "both" | "coordinator" | "admin";
  parish_id?: number | null;
  profile_photo_url?: string | null;
  is_active: boolean;
  is_verified: boolean;
  last_known_latitude?: number | null;
  last_known_longitude?: number | null;
}

export interface Diocese {
  id: number;
  name: string;
  state: string;
}

export interface Parish {
  id: number;
  name: string;
  diocese_id?: number | null;
  address?: string | null;
  city?: string | null;
  state?: string | null;
  zip_code?: string | null;
  latitude?: number | null;
  longitude?: number | null;
}

export interface RideRequest {
  id: number;
  ride_id?: number | null;
  rider_id: number;
  destination_type: "mass" | "confession" | "prayer_event" | "social" | "other";
  parish_id?: number | null;
  requested_datetime: string;
  notes?: string | null;
  passenger_count: number;
  pickup: { latitude: number; longitude: number };
  dropoff: { latitude: number; longitude: number };
  status: "pending" | "accepted" | "in_progress" | "completed" | "cancelled";
  created_at: string;
  updated_at: string;
}

export interface DonationIntent {
  payment_intent_id: string;
  client_secret: string;
  amount: number;
  currency: string;
}

export interface Donation {
  id: number;
  ride_id: number;
  amount: number;
  currency: string;
  stripe_status: string;
  created_at: string;
  completed_at?: string | null;
  stripe_fee_cents: number;
  net_amount_cents: number;
}

export interface DonationPreferences {
  auto_donation_enabled: boolean;
  auto_donation_type: "fixed" | "distance_based";
  auto_donation_amount?: number | null;
  auto_donation_multiplier?: number | null;
}

export interface DonationPreferencesUpdate {
  auto_donation_enabled?: boolean;
  auto_donation_type?: "fixed" | "distance_based";
  auto_donation_amount?: number | null;
  auto_donation_multiplier?: number | null;
}

export interface RideReviewResponse {
  id: number;
  ride_id: number;
  rating: number;
  comment?: string | null;
  created_at: string;
  donation?: Donation | null;
  donation_intent?: DonationIntent | null;
}

export interface Ride {
  id: number;
  ride_request_id: number;
  driver_id: number;
  rider_id: number;
  status:
    | "accepted"
    | "driver_enroute"
    | "arrived"
    | "picked_up"
    | "in_progress"
    | "completed"
    | "cancelled";
  pickup: { latitude: number; longitude: number };
  dropoff: { latitude: number; longitude: number };
  accepted_at: string;
  auto_donation_intent?: DonationIntent | null;
  completed_at?: string | null;
}

// Admin / Driver Profile
export interface DriverProfileResponse {
  id: number;
  user_id: number;
  vehicle_make?: string | null;
  vehicle_model?: string | null;
  vehicle_year?: number | null;
  vehicle_color?: string | null;
  license_plate?: string | null;
  vehicle_capacity: number;
  insurance_verified: boolean;
  background_check_status: string;
  training_completed_date?: string | null;
  training_expiration_date?: string | null;
  admin_notes?: string | null;
  is_available: boolean;
  total_rides: number;
  average_rating: number;
  created_at: string;
  updated_at: string;
}

// Helper for API requests
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed: ${response.status}`);
  }

  return response.json();
}

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

// Auth endpoints
export async function login(
  email: string,
  password: string
): Promise<{ access_token: string; token_type: string }> {
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);

  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData.toString(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Login failed");
  }

  return response.json();
}

export async function register(data: {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
  role?: string;
  parish_id?: number;
}): Promise<User> {
  return apiFetch<User>("/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// Alias for register (used by register page)
export const registerUser = register;

// Email verification
export async function verifyEmail(
  email: string,
  code: string
): Promise<{ message: string }> {
  return apiFetch<{ message: string }>("/auth/verify-email", {
    method: "POST",
    body: JSON.stringify({ email, code }),
  });
}

export async function resendVerification(
  email: string
): Promise<{ message: string }> {
  return apiFetch<{ message: string }>("/auth/resend-verification", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export async function getCurrentUser(token: string): Promise<User> {
  return apiFetch<User>("/users/me", {
    headers: authHeaders(token),
  });
}

export async function updateCurrentUser(
  token: string,
  data: Partial<{
    first_name: string;
    last_name: string;
    phone: string;
    parish_id: number;
  }>
): Promise<User> {
  return apiFetch<User>("/users/me", {
    method: "PUT",
    headers: authHeaders(token),
    body: JSON.stringify(data),
  });
}

export async function updateLocation(
  token: string,
  latitude: number,
  longitude: number
): Promise<User> {
  return apiFetch<User>("/users/me/location", {
    method: "PUT",
    headers: authHeaders(token),
    body: JSON.stringify({ latitude, longitude }),
  });
}

export async function uploadProfilePhoto(
  token: string,
  file: File
): Promise<User> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/users/me/photo`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Photo upload failed");
  }

  return response.json();
}

export async function deleteProfilePhoto(token: string): Promise<User> {
  return apiFetch<User>("/users/me/photo", {
    method: "DELETE",
    headers: authHeaders(token),
  });
}

// Password reset
export async function forgotPassword(
  email: string
): Promise<{ message: string }> {
  return apiFetch<{ message: string }>("/auth/forgot-password", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export async function validateResetToken(
  token: string
): Promise<{ valid: boolean }> {
  return apiFetch<{ valid: boolean }>(`/auth/validate-reset-token/${token}`);
}

export async function resetPassword(
  token: string,
  newPassword: string
): Promise<{ message: string }> {
  return apiFetch<{ message: string }>("/auth/reset-password", {
    method: "POST",
    body: JSON.stringify({ token, new_password: newPassword }),
  });
}

// Parishes
export async function listParishes(): Promise<Parish[]> {
  return apiFetch<Parish[]>("/parishes/");
}

// Ride requests
export async function createRideRequest(
  token: string,
  data: {
    pickup: { latitude: number; longitude: number };
    dropoff: { latitude: number; longitude: number };
    destination_type: string;
    requested_datetime: string;
    parish_id?: number;
    notes?: string;
    passenger_count: number;
  }
): Promise<RideRequest> {
  return apiFetch<RideRequest>("/rides/", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(data),
  });
}

export async function listMyRideRequests(token: string): Promise<RideRequest[]> {
  return apiFetch<RideRequest[]>("/rides/mine", {
    headers: authHeaders(token),
  });
}

export async function listOpenRideRequests(
  token: string
): Promise<RideRequest[]> {
  return apiFetch<RideRequest[]>("/rides/open", {
    headers: authHeaders(token),
  });
}

// Rides
export async function acceptRideRequest(
  token: string,
  rideRequestId: number
): Promise<Ride> {
  return apiFetch<Ride>(`/rides/${rideRequestId}/accept`, {
    method: "POST",
    headers: authHeaders(token),
  });
}

export async function listAssignedRides(token: string): Promise<Ride[]> {
  return apiFetch<Ride[]>("/rides/assigned", {
    headers: authHeaders(token),
  });
}

export async function updateRideStatus(
  token: string,
  rideId: number,
  status: Ride["status"]
): Promise<Ride> {
  return apiFetch<Ride>(`/rides/${rideId}/status`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify({ status }),
  });
}

// Donations / reviews
export async function getDonationPreferences(
  token: string
): Promise<DonationPreferences> {
  return apiFetch<DonationPreferences>("/users/me/donation-preferences", {
    headers: authHeaders(token),
  });
}

export async function updateDonationPreferences(
  token: string,
  data: DonationPreferencesUpdate
): Promise<DonationPreferences> {
  return apiFetch<DonationPreferences>("/users/me/donation-preferences", {
    method: "PUT",
    headers: authHeaders(token),
    body: JSON.stringify(data),
  });
}

export async function listMyDonations(token: string): Promise<Donation[]> {
  return apiFetch<Donation[]>("/users/me/donations", {
    headers: authHeaders(token),
  });
}

export async function createRideDonationIntent(
  token: string,
  rideId: number,
  donationAmount: number
): Promise<DonationIntent> {
  return apiFetch<DonationIntent>(`/rides/${rideId}/donate`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ donation_amount: donationAmount }),
  });
}

export async function getRideDonationIntent(
  token: string,
  rideId: number
): Promise<DonationIntent> {
  return apiFetch<DonationIntent>(`/rides/${rideId}/donation-intent`, {
    headers: authHeaders(token),
  });
}

export async function submitRideReview(
  token: string,
  rideId: number,
  data: {
    rating: number;
    comment?: string;
    donation_amount?: number;
  }
): Promise<RideReviewResponse> {
  return apiFetch<RideReviewResponse>(`/rides/${rideId}/review`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(data),
  });
}

// Admin API
export async function listDrivers(token: string): Promise<DriverProfileResponse[]> {
  return apiFetch<DriverProfileResponse[]>("/admin/drivers", {
    headers: authHeaders(token),
  });
}

export async function verifyDriver(
  token: string,
  userId: number,
  data: {
    background_check_status?: string | null;
    training_completed_date?: string | null;
    training_expiration_date?: string | null;
    admin_notes?: string | null;
  }
): Promise<DriverProfileResponse> {
  return apiFetch<DriverProfileResponse>(`/admin/drivers/${userId}/verify`, {
    method: "PUT",
    headers: authHeaders(token),
    body: JSON.stringify(data),
  });
}

export async function updateDriverAvailability(
  token: string,
  isAvailable: boolean
): Promise<DriverProfileResponse> {
  return apiFetch<DriverProfileResponse>("/drivers/me/availability", {
    method: "PUT",
    headers: authHeaders(token),
    body: JSON.stringify({ is_available: isAvailable }),
  });
}

export async function createDriverProfile(
  token: string,
  data: {
    vehicle_make?: string;
    vehicle_model?: string;
    vehicle_year?: number;
    vehicle_color?: string;
    license_plate?: string;
    vehicle_capacity?: number;
  }
): Promise<DriverProfileResponse> {
  return apiFetch<DriverProfileResponse>("/drivers/profile", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(data),
  });
}

export async function updateDriverProfile(
  token: string,
  data: {
    vehicle_make?: string;
    vehicle_model?: string;
    vehicle_year?: number;
    vehicle_color?: string;
    license_plate?: string;
    vehicle_capacity?: number;
  }
): Promise<DriverProfileResponse> {
  return apiFetch<DriverProfileResponse>("/drivers/me", {
    method: "PUT",
    headers: authHeaders(token),
    body: JSON.stringify(data),
  });
}

export async function cancelRideRequest(
  token: string,
  rideRequestId: number,
  reason?: string
): Promise<RideRequest> {
  return apiFetch<RideRequest>(`/rides/${rideRequestId}/cancel`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ reason: reason ?? null }),
  });
}

// Public-facing driver profile (no license plate)
export interface AvailableDriver {
  id: number;
  user_id: number;
  vehicle_make?: string | null;
  vehicle_model?: string | null;
  vehicle_year?: number | null;
  vehicle_color?: string | null;
  vehicle_capacity: number;
  total_rides: number;
  average_rating: number;
}

export async function getAvailableDrivers(
  token: string,
  options?: {
    latitude?: number;
    longitude?: number;
    radiusMiles?: number;
  }
): Promise<AvailableDriver[]> {
  const params = new URLSearchParams();
  if (options?.latitude !== undefined) params.set("latitude", String(options.latitude));
  if (options?.longitude !== undefined) params.set("longitude", String(options.longitude));
  if (options?.radiusMiles !== undefined)
    params.set("radius_miles", String(options.radiusMiles));
  const qs = params.toString() ? `?${params.toString()}` : "";
  return apiFetch<AvailableDriver[]>(`/drivers/available${qs}`, {
    headers: authHeaders(token),
  });
}

export async function approveDriver(
  token: string,
  userId: number
): Promise<DriverProfileResponse> {
  return apiFetch<DriverProfileResponse>(`/admin/drivers/${userId}/approve`, {
    method: "POST",
    headers: authHeaders(token),
  });
}

export async function rejectDriver(
  token: string,
  userId: number,
  reason?: string
): Promise<DriverProfileResponse> {
  return apiFetch<DriverProfileResponse>(`/admin/drivers/${userId}/reject`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ reason: reason ?? null }),
  });
}

export async function getDioceses(): Promise<Diocese[]> {
  return apiFetch<Diocese[]>("/dioceses/");
}

export async function getParishes(dioceseId?: number): Promise<Parish[]> {
  const url = dioceseId ? `/parishes/?diocese_id=${dioceseId}` : "/parishes/";
  return apiFetch<Parish[]>(url);
}

export async function getDriverProfile(token: string): Promise<DriverProfileResponse> {
  return apiFetch<DriverProfileResponse>("/drivers/me", {
    headers: authHeaders(token),
  });
}

export interface ParishStats {
  total_drivers: number;
  verified_drivers: number;
  pending_drivers: number;
  total_ride_requests: number;
  completed_rides: number;
}

export async function getParishStats(token: string): Promise<ParishStats> {
  return apiFetch<ParishStats>("/admin/parish/stats", {
    headers: authHeaders(token),
  });
}

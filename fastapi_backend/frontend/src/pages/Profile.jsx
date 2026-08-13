import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import { apiFetch, getCurrentUser } from "../api";

function Profile() {
  const [user, setUser] = useState(
    getCurrentUser()
  );

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  useEffect(() => {
    loadProfile();
  }, []);

  async function loadProfile() {
    setLoading(true);

    try {
      const response =
        await apiFetch("/auth/me");

      if (!response.ok) {
        return;
      }

      const data =
        await response.json();

      setUser(data);

      localStorage.setItem(
        "user",
        JSON.stringify(data)
      );
    } catch {
      setError(
        "Unable to load profile"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <Navbar />

      <main className="container">
        <div className="profile-card">
          <h1>
            My Profile
          </h1>

          {loading && (
            <p>
              Loading profile...
            </p>
          )}

          {error && (
            <div className="message error">
              {error}
            </div>
          )}

          {user && (
            <>
              <div className="profile-row">
                <strong>
                  Name
                </strong>

                <span>
                  {user.name}
                </span>
              </div>

              <div className="profile-row">
                <strong>
                  Email
                </strong>

                <span>
                  {user.email}
                </span>
              </div>

              <div className="profile-row">
                <strong>
                  Role
                </strong>

                <span>
                  {user.role}
                </span>
              </div>

              <div className="profile-row">
                <strong>
                  User ID
                </strong>

                <span>
                  {user.id}
                </span>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}

export default Profile;
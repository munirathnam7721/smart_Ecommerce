import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth0 } from "@auth0/auth0-react";

const API_URL = "http://localhost:8000";

function Login() {
  const navigate = useNavigate();

  const {
    loginWithRedirect,
    getAccessTokenSilently,
    isAuthenticated,
    isLoading,
  } = useAuth0();

  const auth0Processed = useRef(false);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [processingAuth0, setProcessingAuth0] = useState(false);

  useEffect(() => {
    if (isLoading || !isAuthenticated || auth0Processed.current) {
      return;
    }

    auth0Processed.current = true;
    handleAuth0Login();
  }, [isAuthenticated, isLoading]);

  async function handleAuth0Login() {
    setProcessingAuth0(true);
    setMessage("Completing Google login...");

    try {
      const auth0AccessToken = await getAccessTokenSilently({
        authorizationParams: {
          audience: import.meta.env.VITE_AUTH0_AUDIENCE,
        },
      });

      const response = await fetch(`${API_URL}/auth/auth0`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          access_token: auth0AccessToken,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setMessage(data.detail || "Backend Auth0 login failed");
        setProcessingAuth0(false);
        auth0Processed.current = false;
        return;
      }

      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);

      if (data.user) {
        localStorage.setItem("user", JSON.stringify(data.user));
      }

      navigate("/products", { replace: true });
    } catch (error) {
      console.error(error);
      setMessage(error.message || "Google login failed");
      setProcessingAuth0(false);
      auth0Processed.current = false;
    }
  }

  async function handleLogin(event) {
    event.preventDefault();
    setMessage("");

    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email.trim(),
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setMessage(data.detail || "Login failed");
        return;
      }

      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);

      if (data.user) {
        localStorage.setItem("user", JSON.stringify(data.user));
      }

      navigate("/products", { replace: true });
    } catch (error) {
      console.error(error);
      setMessage("Cannot connect to backend");
    }
  }

  async function handleGoogleLogin() {
    try {
      setMessage("");

      await loginWithRedirect({
        authorizationParams: {
          audience: import.meta.env.VITE_AUTH0_AUDIENCE,
          redirect_uri: window.location.origin,
          scope: "openid profile email",
        },
      });
    } catch (error) {
      console.error(error);
      setMessage("Could not start Google login");
    }
  }

  function handleRegister() {
    navigate("/register");
  }

  if (isLoading) {
    return (
      <div>
        <h1>Smart E-Commerce</h1>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div
      style={{
        maxWidth: "400px",
        margin: "60px auto",
        padding: "30px",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1>Smart E-Commerce</h1>

      <h2>Login</h2>

      <form onSubmit={handleLogin}>
        <label>Email</label>

        <input
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
          style={{
            width: "100%",
            padding: "10px",
            marginTop: "5px",
            boxSizing: "border-box",
          }}
        />

        <br />
        <br />

        <label>Password</label>

        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
          style={{
            width: "100%",
            padding: "10px",
            marginTop: "5px",
            boxSizing: "border-box",
          }}
        />

        <br />
        <br />

        <button
          type="submit"
          style={{
            width: "100%",
            padding: "12px",
          }}
        >
          Login
        </button>
      </form>

      {message && <p>{message}</p>}

      <div
        style={{
          margin: "25px 0",
          textAlign: "center",
        }}
      >
        OR
      </div>

      <button
        type="button"
        onClick={handleGoogleLogin}
        disabled={processingAuth0}
        style={{
          width: "100%",
          padding: "12px",
        }}
      >
        {processingAuth0 ? "Signing in..." : "Continue with Google"}
      </button>

      <br />
      <br />

      <button
        type="button"
        onClick={handleRegister}
        style={{
          width: "100%",
          padding: "12px",
        }}
      >
        Register
      </button>
    </div>
  );
}

export default Login;
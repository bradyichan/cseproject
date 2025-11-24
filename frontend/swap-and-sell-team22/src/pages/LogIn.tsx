import { useState } from "react";
import { Link } from "react-router-dom";

interface LogInProps {
  setIsAuthenticated: (val: boolean) => void;
}

function LogIn({ setIsAuthenticated }: LogInProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async () => {
    if (!username || !password) {
      alert("Please fill in all fields");
      return;
    }

    try {
      const response = await fetch("http://localhost:6767/users/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username,
          password: password,
        }),
      });

      const data = await response.json();

      if (response.ok && data.status === "success") {
        const userId = data.data.userId.toString();
        const usernameFromBackend = data.data.username;

        localStorage.setItem("userId", userId);
        localStorage.setItem("username", usernameFromBackend);

        console.log("Stored in localStorage:", {
          userId,
          username: usernameFromBackend,
        });
        setIsAuthenticated(true);
      } else {
        const errorMessage = data.error?.message || "Login failed";
        alert(errorMessage);
      }
    } catch (error) {
      console.error("Login error:", error);
      alert("An error occurred during login. Please try again.");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6">
      <div
        style={{
          backgroundColor: "white",
          padding: "40px",
          borderRadius: "10px",
          boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
          width: "400px",
        }}
      >
        <h1 style={{ color: "black", marginBottom: "20px" }}>Log In</h1>

        <div style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
          <div>
            <label
              style={{
                display: "block",
                marginBottom: "5px",
                color: "black",
              }}
            >
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{
                width: "100%",
                padding: "10px",
                borderRadius: "5px",
                border: "1px solid #ccc",
              }}
              required
            />
          </div>

          <div>
            <label
              style={{
                display: "block",
                marginBottom: "5px",
                color: "black",
              }}
            >
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: "100%",
                padding: "10px",
                borderRadius: "5px",
                border: "1px solid #ccc",
              }}
              required
            />
          </div>

          <button
            onClick={handleSubmit}
            style={{
              backgroundColor: "blue",
              color: "white",
              padding: "12px",
              borderRadius: "5px",
              border: "none",
              fontSize: "16px",
              fontWeight: "bold",
              cursor: "pointer",
            }}
          >
            Log In
          </button>
        </div>

        <p style={{ marginTop: "20px", color: "black" }}>
          Don't have an account?{" "}
          <Link to="/signup" style={{ color: "blue" }}>
            Sign Up
          </Link>
        </p>

        <Link
          to="/"
          style={{ color: "gray", display: "block", marginTop: "10px" }}
        >
          ← Back
        </Link>
      </div>
    </div>
  );
}

export default LogIn;

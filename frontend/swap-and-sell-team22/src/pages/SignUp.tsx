import { useState } from "react";
import { Link } from "react-router-dom";

interface SignUpProps {
  setIsAuthenticated: (val: boolean) => void;
}

function SignUp({ setIsAuthenticated }: SignUpProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleSubmit = async () => {
    if (!username || !password || !confirmPassword) {
      alert("Please fill in all fields");
      return;
    }

    if (password !== confirmPassword) {
      alert("Passwords don't match!");
      return;
    }

    try {
      const response = await fetch("http://localhost:6767/users/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username,
          email: `${username}@placeholder.com`, // required by backend
          password: password,
        }),
      });

      const data = await response.json();

      if (response.ok && data.status === "success") {
        localStorage.setItem("userId", data.data.userId.toString());
        localStorage.setItem("username", data.data.username);
        setIsAuthenticated(true);
      } else {
        const errorMessage = data.error?.message || "Registration failed";
        alert(errorMessage);
      }
    } catch (error) {
      console.error("Registration error:", error);
      alert("An error occurred during registration. Please try again.");
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
        <h1 style={{ color: "black", marginBottom: "20px" }}>Sign Up</h1>

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

          <div>
            <label
              style={{
                display: "block",
                marginBottom: "5px",
                color: "black",
              }}
            >
              Confirm Password
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
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
              backgroundColor: "green",
              color: "white",
              padding: "12px",
              borderRadius: "5px",
              border: "none",
              fontSize: "16px",
              fontWeight: "bold",
              cursor: "pointer",
            }}
          >
            Sign Up
          </button>
        </div>

        <p style={{ marginTop: "20px", color: "black" }}>
          Already have an account?{" "}
          <Link to="/login" style={{ color: "blue" }}>
            Log In
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

export default SignUp;

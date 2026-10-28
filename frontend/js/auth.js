
// Login, logout and role-based redirects.
import { api } from "./api.js";

const HOME = {
  admin: "/admin/dashboard.html",
  lecturer: "/view/timetable.html",
  student: "/view/timetable.html"
};

// Handle the login form.
export async function handleLoginForm(form) {
  const errorMessage = document.getElementById("login-error");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (errorMessage) {
      errorMessage.textContent = "";
    }

    const usernameInput = form.querySelector(
      '[name="username"], #username'
    );

    const passwordInput = form.querySelector(
      '[name="password"], #password'
    );

    if (!usernameInput || !passwordInput) {
      if (errorMessage) {
        errorMessage.textContent = "Login form fields were not found.";
      }
      return;
    }

    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    if (!username || !password) {
      if (errorMessage) {
        errorMessage.textContent =
          "Please enter your username and password.";
      }
      return;
    }

    const submitButton = form.querySelector(
      'button[type="submit"], input[type="submit"]'
    );

    if (submitButton) {
      submitButton.disabled = true;
    }

    try {
      const result = await api.post("/api/auth/login", {
        username,
        password
      });

      const data = result.data || result;
      const user = data.user || data;
      const role = String(user.role || "").toLowerCase();

      if (HOME[role]) {
        window.location.href = HOME[role];
      } else {
        if (errorMessage) {
          errorMessage.textContent =
            "Your account does not have a valid role.";
        }
      }
    } catch (error) {
      if (error.status === 401 || error.statusCode === 401) {
        if (errorMessage) {
          errorMessage.textContent =
            "Wrong username or password";
        }
      } else if (errorMessage) {
        errorMessage.textContent =
          error.message || "Login failed. Please try again.";
      }
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
      }
    }
  });
}

// Check the signed-in user and redirect to the correct page.
export async function redirectByRole() {
  try {
    const result = await api.get("/api/auth/me");
    const data = result.data || result;
    const user = data.user || data;
    const role = String(user.role || "").toLowerCase();

    if (HOME[role]) {
      window.location.href = HOME[role];
    } else {
      window.location.href = "/login.html";
    }
  } catch (error) {
    window.location.href = "/login.html";
  }
}

// Only allow users with the required roles to continue.
export async function requireRole(...roles) {
  try {
    const result = await api.get("/api/auth/me");
    const data = result.data || result;
    const user = data.user || data;
    const role = String(user.role || "").toLowerCase();

    if (!HOME[role]) {
      window.location.href = "/login.html";
      return false;
    }

    const allowedRoles = roles.map(item =>
      String(item).toLowerCase()
    );

    if (!allowedRoles.includes(role)) {
      window.location.href = HOME[role];
      return false;
    }

    return true;
  } catch (error) {
    window.location.href = "/login.html";
    return false;
  }
}

// Log out the current user.
export function handleLogout(button) {
  button.addEventListener("click", async () => {
    button.disabled = true;

    try {
      await api.post("/api/auth/logout", {});
    } catch (error) {
      console.error("Logout request failed:", error);
    } finally {
      window.location.href = "/login.html";
    }
  });
}
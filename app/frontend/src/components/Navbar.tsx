import { useNavigate } from "react-router-dom";

function NavBar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Clear the JWT token from localStorage
    localStorage.removeItem("access_token");

    // Redirect to login page
    navigate("/login");
  };
  return (
    <div className="d-flex align-items-center justify-content-left bg-dark text-light">
      <img
        src="../main-logo-white-transparent.svg"
        alt="FinSight Logo"
        style={{ width: "80px", height: "80px", marginRight: "12px" }}
      />
      <div className="">
        <h3 className="mb-1">FinSight</h3>
        <p className="small mb-0">Helping you make sense of financial data.</p>
      </div>
      <div className="navbar-nav ms-auto">
        <button
          className="btn btn-outline-light btn-sm m-3"
          onClick={handleLogout}
        >
          <i className="bi bi-box-arrow-right me-1"></i>
          Logout
        </button>
      </div>
    </div>
  );
}

export default NavBar;

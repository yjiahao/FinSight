function NavBar() {
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
    </div>
  );
}

export default NavBar;

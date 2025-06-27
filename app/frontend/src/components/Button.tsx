interface ButtonProps {
  children: React.ReactNode;
  onClick: () => void;
  colour?:
    | "primary"
    | "secondary"
    | "success"
    | "danger"
    | "warning"
    | "info"
    | "light"
    | "dark";
}

function Button({ children, onClick, colour = "primary" }: ButtonProps) {
  return (
    <button type="button" className={"btn btn-" + colour} onClick={onClick}>
      {children}
    </button>
  );
}

export default Button;

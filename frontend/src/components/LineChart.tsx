import React from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function LineChart() {
  const data = {
    labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    datasets: [
      {
        label: "Stock Price",
        data: [65, 59, 80, 81, 56, 55],
        borderColor: "rgb(75, 192, 192)",
        backgroundColor: "rgba(75, 192, 192, 0.2)",
        tension: 0.1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top" as const,
      },
    },
  };

  return (
    <div className="container-fluid margin-bottom">
      <div style={{ height: "80%", margin: "auto" }}>
        <div className="d-flex align-items-center justify-content-left mb-4">
          <img
            src="../main-logo-black-transparent.svg"
            alt="FinSight Logo"
            style={{ width: "80px", height: "80px", marginRight: "12px" }}
          />
          <div>
            <h3 className="text-dark mb-1">FinSight</h3>
            <p className="text-muted small mb-0">
              Helping you make sense of financial data.
            </p>
          </div>
        </div>
        <Line data={data} options={options} />
      </div>
    </div>
  );
}

export default LineChart;

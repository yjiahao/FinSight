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
      title: {
        display: true,
        text: "Stock Price Chart",
      },
    },
  };

  return (
    <>
      <div style={{ height: "80%", margin: "0 auto" }}>
        <h3 style={{ textAlign: "center", marginBottom: "20px" }}>
          Stock Price Prediction
        </h3>
        <Line data={data} options={options} />
      </div>
    </>
  );
}

export default LineChart;

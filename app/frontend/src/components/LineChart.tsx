import React, { useRef, useEffect } from "react";
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
  const chartRef = useRef<any>(null);

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
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top" as const,
      },
    },
  };

  useEffect(() => {
    const resizeChart = () => {
      if (chartRef.current) {
        chartRef.current.resize();
      }
    };

    // Listen for window resize
    window.addEventListener("resize", resizeChart);

    // Use ResizeObserver to detect container size changes
    const resizeObserver = new ResizeObserver(() => {
      resizeChart();
    });

    // Observe the chart container
    const chartContainer = chartRef.current?.canvas?.parentElement;
    if (chartContainer) {
      resizeObserver.observe(chartContainer);
    }

    return () => {
      window.removeEventListener("resize", resizeChart);
      resizeObserver.disconnect();
    };
  }, []);

  return (
    <div style={{ height: "100%", width: "100%" }}>
      <Line ref={chartRef} data={data} options={options} />
    </div>
  );
}

export default LineChart;

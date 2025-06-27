import { useState } from "react";

interface SelectorProps {
  stock: string;
  startDate: string;
  endDate: string;
}

// TODO: change the selector to some dropdown we can use
function Selector({ stock, startDate, endDate }: SelectorProps) {
  const [ticker, setTicker] = useState(stock);
  const [start, setStart] = useState(startDate);
  const [end, setEnd] = useState(endDate);

  // log values to console
  const logValues = () => {
    console.log(`Ticker: ${ticker}, Start Date: ${start}, End Date: ${end}`);
  };

  // handle input changes and log
  const handleTickerChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTicker = e.target.value;
    setTicker(newTicker);
    console.log(`Ticker changed to: ${newTicker}`);
  };

  const handleStartChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newStart = e.target.value;
    setStart(newStart);
    console.log(`Start Date changed to: ${newStart}`);
  };

  const handleEndChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newEnd = e.target.value;
    setEnd(newEnd);
    console.log(`End Date changed to: ${newEnd}`);
  };
  return (
    <div className="container-fluid" style={{ marginTop: "2rem" }}>
      <div
        className="p-4 rounded-3"
        style={{
          background: "linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)",
          border: "1px solid #dee2e6",
        }}
      >
        {/* Form Grid */}
        <div
          className="row g-3 justify-content-center"
          style={{ height: "100%", width: "100%" }}
        >
          <div className="col-lg-10">
            <div className="row g-3 align-items-end">
              {/* Ticker */}
              <div className="col-md-3">
                <label className="form-label text-muted small mb-1">
                  Ticker Symbol
                </label>
                <input
                  type="text"
                  className="form-control border-0 shadow-sm"
                  placeholder="AAPL"
                  value={ticker}
                  onChange={handleTickerChange}
                  style={{ backgroundColor: "white" }}
                />
              </div>

              {/* Start Date */}
              <div className="col-md-3">
                <label className="form-label text-muted small mb-1">From</label>
                <input
                  type="date"
                  className="form-control border-0 shadow-sm"
                  value={start}
                  onChange={handleStartChange}
                  style={{ backgroundColor: "white" }}
                />
              </div>

              {/* End Date */}
              <div className="col-md-3">
                <label className="form-label text-muted small mb-1">To</label>
                <input
                  type="date"
                  className="form-control border-0 shadow-sm"
                  value={end}
                  onChange={handleEndChange}
                  style={{ backgroundColor: "white" }}
                />
              </div>

              {/* Action Button */}
              <div className="col-md-3">
                <button
                  className="btn btn-primary px-4 py-2 shadow-sm w-100"
                  onClick={logValues}
                  style={{
                    background: "linear-gradient(135deg, #007bff, #0056b3)",
                    border: "none",
                  }}
                >
                  <i className="bi bi-play-circle me-2"></i>
                  Analyze Performance
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Selector;

import React, { useState } from "react";
import Header from "./components/Header/Header";
import Sidebar from "./components/Sidebar/Sidebar";
import Dashboard from "./components/Dashboard/Dashboard";
import Container from "./components/Containers/Containers";
import Items from "./components/Items/Items";
import Search from "./components/Search/Search";
import Wastage from "./components/Wastage/Wastage";
import Simulation from "./components/Simulation/Simulation";
import Systemlogs from "./components/Systemlogs/Systemlogs";
import ThreeDview from "./components/3DView/ThreeDview";
import "./App.css";

function App() {
  const [currentPage, setCurrentPage] = useState("dashboard");

  const renderPage = () => {
    switch (currentPage) {
      case "dashboard":
        return <Dashboard />;
      case "container":
        return <Container />;
      case "items":
        return <Items />;
      case "search":
        return <Search />;
      case "wastage":
        return <Wastage />;
      case "simulation":
        return <Simulation />;
      case "systemLogs":
        return <Systemlogs />;
        case "3DView":
        return <ThreeDview />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app">
      <Header />
      <div className="main-container">
        <Sidebar onPageChange={setCurrentPage} />
        <main className="content">
          {renderPage()}
        </main>
      </div>
    </div>
  );
}

export default App;
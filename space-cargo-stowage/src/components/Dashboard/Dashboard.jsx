import React from "react";
import "./dashboard.css";
import Button from "../Parts/Buttons";

function Dashboard() {
    return (
        <div className="dashboard-container">
            <div className="grid-box left-panel">
                <h2>Main Content</h2>
                {/* Content for left panel */}
            </div>
            <div className="grid-box top-right">
                <div className="buttons-container">
                    <Button text="Button 1" className="dashboard-button" />
                    <Button text="Button 2" className="dashboard-button" />
                    <Button text="Button 3" className="dashboard-button" />
                </div>
            </div>
            <div className="grid-box bottom-right">
                <h2>Bottom Right Content</h2>
                {/* Content for bottom right panel */}
            </div>
        </div>
    );
}

export default Dashboard;
import React, { useState, useEffect } from "react";
import './App.css'
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import StoryLoader from "./components/StoryLoader.jsx";
import StoryGenerator from "./components/StoryGenerator.jsx";
import SideBar from "./components/SideBar.jsx";
import { API_BASE_URL } from "./util.jsx";

const App = () => {
    const [serverLoading, setServerLoading] = useState(true);

    useEffect(() => {
        const checkServer = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/health`);
                if (response.ok) {
                    setServerLoading(false);
                } else {
                    setTimeout(checkServer, 3000);
                }
            } catch (error) {
                setTimeout(checkServer, 3000);
            }
        };
        checkServer();
    }, []);

    if (serverLoading) {
        return (
            <div className="app-container loading-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{ textAlign: 'center' }}>
                    <div className="spinner"></div>
                    <h2>Waking up the server...</h2>
                    <p>Since this is hosted on a free tier, it might take a minute.</p>
                </div>
            </div>
        );
    }

    return (
        <Router>
            <div className="app-container">
              <header>
                <h1>Interactive Story Game</h1>
              </header>
              <nav>
                <SideBar />
              </nav>
              <main>
                <Routes>
                  <Route path="/story/:id" element={<StoryLoader />} />
                  <Route path="/" element={<StoryGenerator />} />
                </Routes>
              </main>
            </div>
        </Router>
    )
}

export default App;
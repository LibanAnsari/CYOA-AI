import React from "react";
import { useState } from "react";

const ThemeInput = ({ onSubmit }) => {
    const [theme, setTheme] = useState("");
    const [error, setError] = useState("");

    const handleSubmit = (e) => {
        e.preventDefault();
        if (theme.trim() === "") {
            setError("Theme cannot be empty.");
            return;
        }
        if (theme.trim().length < 3) {
            setError("Theme must be at least 3 characters long.");
            return;
        }
        if (theme.trim().length > 200) {
            setError("Theme cannot exceed 200 characters.");
            return;
        }
        setError("");
        onSubmit(theme);    
    }   

    return (
        <div className="theme-input-container">
            <h2>Generate Your Story</h2>
            <p>Enter a theme for your story. It can be anything you like!</p>

            <form onSubmit={handleSubmit} className="theme-form">
                <div className="input-group">
                    <input type="text" value={theme} onChange={(e) => setTheme(e.target.value)} 
                    placeholder="Enter theme/scenarios...(pirates, space adventures, etc.)" 
                    className={error ? 'error' : ''}/>
                <p className="disclaimer">Note: The generated story is for entertainment purposes only. Be mindful of the content you create.</p>
                </div>
                {error && <p className="error-text">{error}</p>}
                <button type="submit" className="generate-btn">Generate Story</button>
            </form>
        </div>
    )
}

export default ThemeInput;
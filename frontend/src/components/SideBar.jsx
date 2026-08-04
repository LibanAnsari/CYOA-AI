import React from 'react'
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { API_BASE_URL } from '../util.jsx'
import { IoHome } from "react-icons/io5";

const SideBar = () => {
    const [storiesList, setStoriesList] = useState([]);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const fetchStories = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/stories/all-stories`);
            setStoriesList(response.data);
        } catch (error) {
            setError(`Failed to fetch stories list: ${error.message}`);
        }
    };

    useEffect(() => {
        fetchStories();

        const handleStoryCreated = () => {
            fetchStories();
        };

        window.addEventListener('story-created', handleStoryCreated);

        return () => {
            window.removeEventListener('story-created', handleStoryCreated);
        };
    }, []);

    return (
        <div className="sidebar">
            <div className="sidebar-header">
                <h2>Stories List</h2>
                <button onClick={() => navigate("/")} className="home-btn">
                    <IoHome size={24} />
                </button>
            </div>
            <div className="sidebar-content">
                {storiesList.length === 0 && !error && <p>No stories available.</p>}
            </div>
            {error && <p className="error-text">{error}</p>}
            <ul>
                {storiesList.map((story) => (
                    <li key={story.story_id}>
                        <button onClick={() => navigate(`/story/${story.story_id}`)}>
                            {story.title}
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default SideBar;
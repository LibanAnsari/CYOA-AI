import React from "react";
import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import LoadingStatus from "./LoadingStatus.jsx";
import StoryGame from "./StoryGame.jsx";
import { API_BASE_URL } from "../util.jsx";

const StoryLoader = () => {
    const { id } = useParams();
    const navigate = useNavigate();

    const [story, setStory] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (id) {
            loadStory(id);
        } else {
            setError("No story ID provided.");
            setLoading(false);
        }
    }, [id]);

    const loadStory = async (storyId) => {
        setStory(null);
        setLoading(true);
        setError(null);

        try {
            const response = await axios.get(`${API_BASE_URL}/stories/${storyId}/complete`);
            setStory(response.data);
            setLoading(false);
        } catch (err) {
            if(err.response && err.response.status === 404) {
                setError("Story not found.");
            } else {
                setError("An error occurred while loading the story.");
            }  
        } finally {
            setLoading(false);
        }
    }

    const createNewStory = () => {
        navigate("/");
    }

    if (loading) {
        return <LoadingStatus theme={story?.theme || "Loading..."} />;
    }

    if (error) {
        return (
            <div className="story-loader">
                <div className="error-message">
                    <h2>Story Error</h2>
                    <p>{error}</p>
                    <button onClick={createNewStory}>Create New Story</button>
                </div>
            </div>
        )
    }

    if (story) {
        return (
            <div className="story-loader">
                <StoryGame story={story} onNewStory={createNewStory} />
            </div>
        )
    }
}

export default StoryLoader;
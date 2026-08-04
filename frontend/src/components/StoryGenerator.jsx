import React from 'react'
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import ThemeInput from './ThemeInput.jsx'
import LoadingStatus from './LoadingStatus.jsx'
import { API_BASE_URL } from '../util.jsx'


const StoryGenerator = () => {
    const navigate = useNavigate();
    const [theme, setTheme] = useState('');
    const [loading, setLoading] = useState(false);
    const [jobId, setJobId] = useState(null);
    const [jobStatus, setJobStatus] = useState(null);
    const [error, setError] = useState(null);

    const resetState = () => {
        setTheme('');
        setLoading(false);
        setJobId(null);
        setJobStatus(null);
        setError(null);
        localStorage.removeItem('activeStoryJobId');
        localStorage.removeItem('activeStoryTheme');
    }

    useEffect(() => {
        const storedJobId = localStorage.getItem('activeStoryJobId');
        const storedTheme = localStorage.getItem('activeStoryTheme');

        if (storedJobId) {
            setJobId(storedJobId);
            setTheme(storedTheme || '');
            setLoading(true);
            pullJobStatus(storedJobId);
        }
    }, []);

    useEffect(() => {
        let pollInterval;

        if(jobId && jobStatus === "processing"){
            pollInterval = setInterval(() => {
                pullJobStatus(jobId);
            }, 5000);

            return () => {
                if (pollInterval) {
                    clearInterval(pollInterval);
                }
            }
        }
    }, [jobId, jobStatus]);

    const fetchStory = async (id) => {
        try{
            setLoading(true);
            setJobStatus('completed');
            localStorage.removeItem('activeStoryJobId');
            localStorage.removeItem('activeStoryTheme');
            window.dispatchEvent(new Event('story-created'));
            navigate(`/story/${id}`);
        } catch (err) {
            setError(`An error occurred while fetching the story: ${err.message}`);
            setLoading(false);
        }
    }

    const pullJobStatus = async (jobId) => {
        try {
            const response = await axios.get(`${API_BASE_URL}/jobs/${jobId}`);
            const { status, story_id, error: jobError } = response.data;
            setJobStatus(status);

            if (status === 'completed' && story_id) {
                fetchStory(story_id);
            } else if (status === 'failed') {
                setError(`Story generation failed: ${jobError || 'Unknown error'}`);
                setLoading(false);
            }

        } catch (err) {
            if (err.response?.status === 404) {
                setError('Job not found. Please try again.');
                localStorage.removeItem('activeStoryJobId');
                localStorage.removeItem('activeStoryTheme');
                setLoading(false);
            } else {
                const detail = err.response?.data?.detail || err.message;
                setError(`An error occurred while pulling job status: ${detail}`);
                setLoading(false);
            }
        }
    }

    const generateStory = async (submittedTheme) => {
        setLoading(true);
        setError(null);
        setTheme(submittedTheme);

        try{
            const response = await axios.post(`${API_BASE_URL}/stories/create`, {theme: submittedTheme});
            const { job_id , status } = response.data;
            setJobId(job_id);
            setJobStatus(status);
            localStorage.setItem('activeStoryJobId', job_id);
            localStorage.setItem('activeStoryTheme', submittedTheme);

            pullJobStatus(job_id);
        } catch (e) {
            const detail = e.response?.data?.detail || e.message;
            if (e.response?.status === 409) {
                const storedJobId = localStorage.getItem('activeStoryJobId');
                const storedTheme = localStorage.getItem('activeStoryTheme');

                if (storedJobId) {
                    setTheme(storedTheme || submittedTheme);
                    setJobId(storedJobId);
                    setLoading(true);
                    setError(null);
                    pullJobStatus(storedJobId);
                    return;
                }
            }

            setLoading(false);
            setError(`Failed to generate story: ${detail}`);
        }
    }


    return (
        <div className="story-generator">
            {error && 
                <div className="error-message">
                    <p>{error}</p>
                    <button onClick={resetState}>Try Again</button>
                </div>
            }
            
            {!jobId && !loading && !error &&
                <ThemeInput onSubmit={generateStory}/>
            }

            {loading && <LoadingStatus theme={theme}/>}
        </div>
    )
}

export default StoryGenerator;
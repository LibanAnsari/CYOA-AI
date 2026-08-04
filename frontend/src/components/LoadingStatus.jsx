import React from 'react'
import Spinner from './Spinner'

const LoadingStatus = ({ theme }) => {
    return (
        <div className="loading-container">
            <h2>Generating Story...</h2>
            <h3>Theme: {theme}</h3>
            <div className="loading-animation">
                <Spinner />
            </div>

            <p className="loading-info">Please wait while we generate your story...</p>
        </div>
    )
}

export default LoadingStatus;
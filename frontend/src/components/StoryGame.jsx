import React from 'react'
import { useState, useEffect } from 'react'

const StoryGame = ({ story, onNewStory}) => {
    const [currentNodeId, setCurrentNodeId] = useState(null);
    const [currentNode, setCurrentNode] = useState(null);
    const [options, setOptions] = useState([]);
    const [isEnding, setIsEnding] = useState(false);
    const [isWinningEnding, setIsWinningEnding] = useState(false);

    useEffect(() => {
        if(story && story.root_node) {
            const rootNodeId = story.root_node.id;
            setCurrentNodeId(rootNodeId);
        }
    }, [story]);

    useEffect(() => {
        if(currentNodeId && story && story.all_nodes) {
            const node = story.all_nodes[currentNodeId];
            setCurrentNode(node);
            setIsEnding(node.is_ending);
            setIsWinningEnding(node.is_winning_ending);
            setOptions(node.options || []);
        }
    }, [currentNodeId, story]);


    const chooseOption = (option) => {
        setCurrentNodeId(option.node_id);
    }

    const restartStory = () => {
        if(story && story.root_node) {
            const rootNodeId = story.root_node.id;
            setCurrentNodeId(rootNodeId);
        }
    }


    return (
        <div className="story-game">
            <header className='story-header'>
                <h2>{story?.title || "Your Story"}</h2>
                <h3>Theme: {story?.theme || "Unknown"}</h3>
            </header>

            <div className="story-content">
                {currentNode && (
                    <div key={currentNodeId} className="story-node">
                        <p>{currentNode.content}</p>
                        {isEnding ? (
                            <div className="story-ending">
                                <h3>{isWinningEnding ? "Congratulations! You've reached a winning ending!" : "The End!"}</h3>
                            </div>
                        ) : (
                            <div className="story-options">
                                <h3>What will you do next?</h3>
                                <div className="options-list">
                                    {options.map((option, index) => (
                                        <button key={index} onClick={() => chooseOption(option)} className="option-btn">
                                            {option.text}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                <div className="story-controls">
                    <button onClick={restartStory} className="reset-btn">Restart Story</button>
                
                    {onNewStory && (
                        <button onClick={onNewStory} className="new-story-btn">Create New Story</button>
                    )}
                </div>
            </div>
        </div>
    )
}


export default StoryGame;
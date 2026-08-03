from platform import node
from dotenv import load_dotenv
load_dotenv()

from requests import session
from sqlalchemy.orm import Session
from core.config import settings

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from core.prompts import STORY_PROMPT_CREATIVE, STORY_PROMPT_SADISTIC
from core.models import StoryLLMResponse, StoryNodeLLM
from models.story import Story, StoryNode


class StoryGenerator:
    
    @classmethod
    def _get_agent(cls):
        return create_agent(
            model=init_chat_model(settings.LLM_MODEL, temperature=0.7),
            system_prompt=STORY_PROMPT_CREATIVE,
            response_format=StoryLLMResponse,
        )
        
    
    @classmethod
    def generate_story(cls, db: Session, session_id: str, theme: str = "Fantasy") -> Story:
        agent = cls._get_agent()
        
        response = agent.invoke({"messages": [HumanMessage(content=f"Generate a story with the theme: {theme}")], "session_id": session_id})
        
        story_structure = response["structured_response"]
        
        story_db = Story(
            title=story_structure.title,
            theme=theme,
            session_id=session_id,
        )
        
        db.add(story_db)
        db.flush()  # Flush to get the story ID for the nodes
        
        root_node_data = story_structure.rootNode

        if isinstance(root_node_data, dict): # Just a safety check to ensure root_node_data is a StoryNodeLLM object, i dont need this
            root_node_data = StoryNodeLLM.model_validate(root_node_data)
            
        cls._process_story_node(db, story_db.id, root_node_data, is_root=True)
        
        db.commit()
        
        return story_db
    
    @classmethod
    def _process_story_node(cls, db: Session, story_id: int, node_data: StoryNodeLLM, is_root: bool = False) -> StoryNode:
        node = StoryNode(
            story_id=story_id,
            content=node_data.content if hasattr(node_data, 'content') else node_data['content'],
            is_root=is_root,
            is_ending=node_data.isEnding,
            is_winning_ending=node_data.isWinningEnding if hasattr(node_data, 'isWinningEnding') else node_data['isWinningEnding'],
            options=[]
        )
        
        db.add(node)
        db.flush()  # Flush to get the node ID for the options
        
        if not node.is_ending and (hasattr(node_data, 'options') and node_data.options):
            options_list = []
            for option_data in node_data.options:
                next_node = option_data.nextNode if hasattr(option_data, 'nextNode') else option_data['nextNode']
                
                if isinstance(next_node, dict):  # Just a safety check to ensure next_node is a StoryNodeLLM object
                    next_node = StoryNodeLLM.model_validate(next_node)
                    
                child_node = cls._process_story_node(db, story_id, next_node, False)
                
                options_list.append(
                    {
                        "text": option_data.text if hasattr(option_data, 'text') else option_data['text'],
                        "node_id": child_node.id
                    }
                )
            
            node.options = options_list
            
        db.flush()  # Flush to ensure the node is saved before returning
        
        return node

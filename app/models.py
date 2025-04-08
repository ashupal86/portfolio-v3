# This module exports model classes from app.models to avoid circular imports
from app import models

# Re-export all model classes for easy import elsewhere
User = models.get('User')
About = models.get('About')
Skill = models.get('Skill')
Project = models.get('Project')
Achievement = models.get('Achievement')
Education = models.get('Education')
BlogPost = models.get('BlogPost')
Contact = models.get('Contact') 